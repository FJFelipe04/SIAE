"""Pruebas de la API por historia de usuario (requieren PostgreSQL)."""


# ---------- HU-01 Autenticación ----------
def test_registro_y_login(cliente):
    r = cliente.post("/auth/registro", json={"nombre": "Laura Gómez", "correo": "Laura@ComercialAndina.co", "clave": "Ventas2026"})
    assert r.status_code == 201 and r.json()["correo"] == "laura@comercialandina.co"
    r = cliente.post("/auth/login", json={"correo": "laura@comercialandina.co", "clave": "Ventas2026"})
    assert r.status_code == 200 and r.json()["mensaje"] == "Autenticación satisfactoria"
    yo = cliente.get("/auth/yo", headers={"Authorization": "Bearer " + r.json()["access_token"]})
    assert yo.json()["nombre"] == "Laura Gómez"


def test_validaciones_de_registro(cliente):
    assert cliente.post("/auth/registro", json={"nombre": "Ana", "correo": "no-es-correo", "clave": "12345678"}).status_code == 422
    assert cliente.post("/auth/registro", json={"nombre": "Ana", "correo": "ana@x.co", "clave": "corta"}).status_code == 422
    assert cliente.post("/auth/registro", json={"nombre": "A", "correo": "ana@x.co", "clave": "12345678"}).status_code == 422
    cliente.post("/auth/registro", json={"nombre": "Ana", "correo": "ana@x.co", "clave": "12345678"})
    assert cliente.post("/auth/registro", json={"nombre": "Ana 2", "correo": "ana@x.co", "clave": "12345678"}).status_code == 409


def test_login_incorrecto_y_bloqueo(cliente):
    cliente.post("/auth/registro", json={"nombre": "Ana", "correo": "ana@x.co", "clave": "12345678"})
    for _ in range(5):
        r = cliente.post("/auth/login", json={"correo": "ana@x.co", "clave": "malaclave"})
        assert r.status_code == 401 and r.json()["detail"] == "Correo o contraseña incorrectos."
    assert cliente.post("/auth/login", json={"correo": "ana@x.co", "clave": "12345678"}).status_code == 429


def test_rutas_protegidas_sin_token(cliente):
    assert cliente.get("/tablas").status_code == 401
    assert cliente.get("/tablas", headers={"Authorization": "Bearer token-falso"}).status_code == 401


# ---------- HU-02 Carga y vista previa ----------
def test_carga_csv_y_vista_previa_original(cliente, token, archivo_id):
    r = cliente.get(f"/archivos/{archivo_id}", headers=token).json()
    assert r["cantidad_registros"] == 8 and len(r["columnas"]) == 8
    assert r["vista_previa"]["filas"][2][0] == "02-09-2026"            # formato original intacto
    assert r["vista_previa"]["filas"][4][7] == "cliente nuevo; referido"  # comillas respetadas
    tipos = {c["nombre"]: c["tipo"] for c in r["columnas"]}
    assert tipos["Cantidad"] == "numero" and tipos["Cliente"] == "texto"


def test_carga_rechaza_formato(cliente, token):
    r = cliente.post("/archivos", headers=token, files={"archivo": ("ventas.pdf", b"%PDF", "application/pdf")})
    assert r.status_code == 422 and "no es .xlsx ni .csv" in r.json()["detail"]


def test_carga_xlsx(cliente, token):
    import io
    import openpyxl
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.append(["Fecha", "Valor"])
    hoja.append(["05/09/2026", "1000"])
    buf = io.BytesIO()
    libro.save(buf)
    r = cliente.post("/archivos", headers=token, files={"archivo": ("v.xlsx", buf.getvalue(), "application/octet-stream")})
    assert r.status_code == 201 and r.json()["cantidad_registros"] == 1


def test_no_ve_archivos_de_otro_usuario(cliente, token, archivo_id):
    cliente.post("/auth/registro", json={"nombre": "Otro", "correo": "otro@x.co", "clave": "12345678"})
    t2 = cliente.post("/auth/login", json={"correo": "otro@x.co", "clave": "12345678"}).json()["access_token"]
    assert cliente.get(f"/archivos/{archivo_id}", headers={"Authorization": "Bearer " + t2}).status_code == 404


# ---------- HU-03 Transformación y deshacer ----------
def test_transformar_y_deshacer(cliente, token, archivo_id):
    s = cliente.post(f"/sesiones?archivo_id={archivo_id}", headers=token).json()
    sid = s["id"]
    r = cliente.post(f"/sesiones/{sid}/pasos", headers=token, json={"tipo": "formato_fecha", "columna": "Fecha"}).json()
    assert r["vista_previa"]["aviso"].startswith("1 fila")
    r = cliente.post(f"/sesiones/{sid}/pasos", headers=token, json={"tipo": "quitar_duplicados"}).json()
    assert r["vista_previa"]["total_filas"] == 7
    r = cliente.post(f"/sesiones/{sid}/pasos", headers=token, json={"tipo": "eliminar_columna", "columna": "Observaciones"}).json()
    assert "Observaciones" not in r["vista_previa"]["columnas"]
    r = cliente.delete(f"/sesiones/{sid}/pasos/ultimo", headers=token).json()
    assert "Observaciones" in r["vista_previa"]["columnas"] and len(r["pasos"]) == 2
    original = cliente.get(f"/archivos/{archivo_id}", headers=token).json()
    assert original["vista_previa"]["total_filas"] == 8  # el archivo original no cambió


def test_transformacion_invalida_no_se_guarda(cliente, token, archivo_id):
    sid = cliente.post(f"/sesiones?archivo_id={archivo_id}", headers=token).json()["id"]
    r = cliente.post(f"/sesiones/{sid}/pasos", headers=token, json={"tipo": "renombrar_columna", "columna": "Cliente", "parametros": {"nuevo": "Producto"}})
    assert r.status_code == 422
    assert cliente.get(f"/sesiones/{sid}", headers=token).json()["pasos"] == []


# ---------- HU-04 Confirmar y generar tabla ----------
def _confirmar(cliente, token, archivo_id, nombre="ventas_ago_oct_2026"):
    sid = cliente.post(f"/sesiones?archivo_id={archivo_id}", headers=token).json()["id"]
    for paso in ({"tipo": "formato_fecha", "columna": "Fecha"}, {"tipo": "quitar_duplicados"}, {"tipo": "eliminar_columna", "columna": "Observaciones"}):
        cliente.post(f"/sesiones/{sid}/pasos", headers=token, json=paso)
    return sid, cliente.post(f"/sesiones/{sid}/confirmar", headers=token, json={"nombre_tabla": nombre, "columna_fecha": "Fecha", "columna_valor": "Valor"})


def test_confirmar_genera_tabla(cliente, token, archivo_id):
    sid, r = _confirmar(cliente, token, archivo_id)
    assert r.status_code == 201
    assert r.json()["filas"] == 6 and r.json()["filas_omitidas"] == 1  # la fila 'sin fecha' no se puede analizar
    assert cliente.post(f"/sesiones/{sid}/pasos", headers=token, json={"tipo": "quitar_duplicados"}).status_code == 409


def test_cancelar_no_guarda(cliente, token, archivo_id):
    sid = cliente.post(f"/sesiones?archivo_id={archivo_id}", headers=token).json()["id"]
    assert cliente.post(f"/sesiones/{sid}/cancelar", headers=token).status_code == 204
    assert cliente.get("/tablas", headers=token).json() == []


def test_nombre_de_tabla_repetido(cliente, token, archivo_id):
    _confirmar(cliente, token, archivo_id)
    _, r = _confirmar(cliente, token, archivo_id)
    assert r.status_code == 409


def test_nombre_de_tabla_invalido(cliente, token, archivo_id):
    _, r = _confirmar(cliente, token, archivo_id, nombre="tabla con espacios!")
    assert r.status_code == 422


# ---------- HU-05 y HU-06 Reportes e indicadores ----------
def test_reporte_por_mes_e_indicadores(cliente, token, archivo_id):
    _, r = _confirmar(cliente, token, archivo_id)
    tid = r.json()["id"]
    rep = cliente.post("/reportes", headers=token, json={"tabla_id": tid, "tipo": "lineas", "agrupacion": "mes"}).json()
    assert rep["serie"] == [{"periodo": "2026-08", "total": 143000.0}, {"periodo": "2026-09", "total": 405500.0}, {"periodo": "2026-10", "total": 240000.0}]
    assert rep["indicadores"]["ventas_totales"] == 788500.0
    assert round(rep["indicadores"]["crecimiento_ultimo_periodo"], 2) == -40.81


def test_reporte_con_filtro_y_rango_invertido(cliente, token, archivo_id):
    _, r = _confirmar(cliente, token, archivo_id)
    tid = r.json()["id"]
    rep = cliente.post("/reportes", headers=token, json={"tabla_id": tid, "fecha_inicio": "2026-09-01", "fecha_fin": "2026-09-30"}).json()
    assert rep["indicadores"]["ventas_totales"] == 405500.0
    malo = cliente.post("/reportes", headers=token, json={"tabla_id": tid, "fecha_inicio": "2026-10-01", "fecha_fin": "2026-01-01"})
    assert malo.status_code == 422


def test_exportar_y_eliminar_tabla(cliente, token, archivo_id):
    _, r = _confirmar(cliente, token, archivo_id)
    tid = r.json()["id"]
    excel = cliente.get(f"/tablas/{tid}/excel", headers=token)
    assert excel.status_code == 200 and excel.content[:2] == b"PK"  # los .xlsx son archivos ZIP
    assert cliente.delete(f"/tablas/{tid}", headers=token).status_code == 204
    assert cliente.get("/tablas", headers=token).json() == []


def test_confirmar_guarda_columnas_extra_como_texto(cliente, token, archivo_id):
    import io
    import openpyxl
    _, r = _confirmar(cliente, token, archivo_id)
    libro = openpyxl.load_workbook(io.BytesIO(cliente.get(f"/tablas/{r.json()['id']}/excel", headers=token).content))
    filas = list(libro.active.values)
    encabezados = filas[0]
    assert "Cliente" in encabezados and "None" not in [str(v) for fila in filas[1:] for v in fila if v is not None]
    assert filas[1][encabezados.index("Cliente")] == "Cliente A"
