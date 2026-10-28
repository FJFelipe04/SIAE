"""Pruebas del rol administrador (control global de usuarios, tablas y bitácora)."""

import psycopg2

from tests.conftest import URL_ADMIN, BD_PRUEBA
from tests.test_api import _confirmar


def _hacer_admin(correo):
    """Simula `python -m app.crear_admin`: el rol solo se asigna desde el servidor."""
    cn = psycopg2.connect(URL_ADMIN.rsplit("/", 1)[0] + "/" + BD_PRUEBA)
    with cn, cn.cursor() as cur:
        cur.execute("UPDATE usuario SET perfil = 'administrador' WHERE correo = %s", (correo,))
    cn.close()


def _cuenta(cliente, correo, clave="Clave2026", admin=False):
    cliente.post("/auth/registro", json={"nombre": "Usuario Prueba", "correo": correo, "clave": clave})
    if admin:
        _hacer_admin(correo)
    r = cliente.post("/auth/login", json={"correo": correo, "clave": clave})
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def test_no_se_puede_registrar_como_administrador(cliente):
    datos = {"nombre": "Intruso", "correo": "intruso@x.co", "clave": "Clave2026", "perfil": "administrador"}
    assert cliente.post("/auth/registro", json=datos).status_code == 422


def test_rutas_de_admin_prohibidas_para_otros_perfiles(cliente, token):
    for ruta in ("/admin/resumen", "/admin/usuarios", "/admin/tablas", "/admin/auditoria"):
        r = cliente.get(ruta, headers=token)
        assert r.status_code == 403
        assert "solo para el administrador" in r.json()["detail"]


def test_admin_ve_usuarios_resumen_y_bitacora(cliente, token):
    admin = _cuenta(cliente, "juanfe@siae.co", admin=True)
    assert cliente.get("/auth/yo", headers=admin).json()["perfil"] == "administrador"
    usuarios = cliente.get("/admin/usuarios", headers=admin).json()
    assert {u["correo"] for u in usuarios} == {"laura@comercialandina.co", "juanfe@siae.co"}
    resumen = cliente.get("/admin/resumen", headers=admin).json()
    assert resumen["usuarios"] == 2 and resumen["administradores"] == 1
    acciones = [e["accion"] for e in cliente.get("/admin/auditoria", headers=admin).json()]
    assert "login_ok" in acciones and "registro" in acciones


def test_admin_cambia_perfil_y_desactiva_cuenta(cliente, token):
    admin = _cuenta(cliente, "juanfe@siae.co", admin=True)
    laura = next(u for u in cliente.get("/admin/usuarios", headers=admin).json() if u["correo"].startswith("laura"))
    r = cliente.patch(f"/admin/usuarios/{laura['id']}", json={"perfil": "jefe_comercial"}, headers=admin)
    assert r.status_code == 200 and r.json()["perfil"] == "jefe_comercial"
    r = cliente.patch(f"/admin/usuarios/{laura['id']}", json={"activo": False}, headers=admin)
    assert r.json()["activo"] is False
    # su token deja de servir y no puede volver a entrar
    assert cliente.get("/tablas", headers=token).status_code == 401
    r = cliente.post("/auth/login", json={"correo": "laura@comercialandina.co", "clave": "Ventas2026"})
    assert r.status_code == 403 and "desactivada" in r.json()["detail"]
    cliente.patch(f"/admin/usuarios/{laura['id']}", json={"activo": True}, headers=admin)
    r = cliente.post("/auth/login", json={"correo": "laura@comercialandina.co", "clave": "Ventas2026"})
    assert r.status_code == 200
    acciones = [e["accion"] for e in cliente.get("/admin/auditoria", headers=admin).json()]
    assert {"admin_cambio_perfil", "admin_desactiva_usuario", "admin_activa_usuario"} <= set(acciones)


def test_admin_no_puede_quitarse_su_propio_rol(cliente):
    admin = _cuenta(cliente, "juanfe@siae.co", admin=True)
    yo = cliente.get("/auth/yo", headers=admin).json()
    for cambio in ({"perfil": "analista"}, {"activo": False}):
        assert cliente.patch(f"/admin/usuarios/{yo['id']}", json=cambio, headers=admin).status_code == 409


def test_admin_accede_a_las_tablas_de_todos(cliente, token, archivo_id):
    tabla_id = _confirmar(cliente, token, archivo_id)[1].json()["id"]
    admin = _cuenta(cliente, "juanfe@siae.co", admin=True)
    otro = _cuenta(cliente, "otro@x.co")
    tablas = cliente.get("/admin/tablas", headers=admin).json()
    assert tablas[0]["id"] == tabla_id and tablas[0]["correo_propietario"] == "laura@comercialandina.co"
    reporte = {"tabla_id": tabla_id, "tipo": "barras", "agrupacion": "mes"}
    assert cliente.post("/reportes", json=reporte, headers=admin).json()["indicadores"]["ventas_totales"] == 788500
    assert cliente.get(f"/tablas/{tabla_id}/excel", headers=admin).status_code == 200
    # un usuario normal sigue sin ver tablas ajenas
    assert cliente.post("/reportes", json=reporte, headers=otro).status_code == 404
    assert cliente.delete(f"/tablas/{tabla_id}", headers=admin).status_code == 204
    acciones = [e["accion"] for e in cliente.get("/admin/auditoria", headers=admin).json()]
    assert "admin_elimina_tabla" in acciones


def test_admin_cambia_usuario_inexistente(cliente):
    admin = _cuenta(cliente, "juanfe@siae.co", admin=True)
    assert cliente.patch("/admin/usuarios/999", json={"activo": False}, headers=admin).status_code == 404


def _consola(monkeypatch, respuestas, claves):
    from app import crear_admin

    respuestas, claves = iter(respuestas), iter(claves)
    monkeypatch.setattr("builtins.input", lambda _: next(respuestas))
    monkeypatch.setattr(crear_admin, "getpass", lambda _: next(claves))
    return crear_admin.main


def test_consola_crea_la_cuenta_de_administrador(cliente, monkeypatch, capsys):
    _consola(monkeypatch, ["Juanfe@SIAE.co", "Juan Felipe Perdomo"], ["Admin2026", "Admin2026"])()
    assert "se creó la cuenta de administrador" in capsys.readouterr().out
    r = cliente.post("/auth/login", json={"correo": "juanfe@siae.co", "clave": "Admin2026"})
    yo = cliente.get("/auth/yo", headers={"Authorization": "Bearer " + r.json()["access_token"]}).json()
    assert yo["perfil"] == "administrador"


def test_consola_promueve_cuenta_existente_y_valida_claves(cliente, token, monkeypatch, capsys):
    _consola(monkeypatch, ["laura@comercialandina.co"], [])()
    assert "ahora es administrador" in capsys.readouterr().out
    assert cliente.get("/admin/resumen", headers=token).status_code == 200
    import pytest

    with pytest.raises(SystemExit, match="no coinciden"):
        _consola(monkeypatch, ["nuevo@x.co", "Nuevo Admin"], ["Clave2026", "Otra2026"])()
    with pytest.raises(SystemExit, match="Datos inválidos"):
        _consola(monkeypatch, ["nuevo@x.co", "Nuevo Admin"], ["corta", "corta"])()
