"""Sesiones de transformación: aplicar, deshacer, confirmar y cancelar (HU-03 y HU-04)."""
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.transformaciones import ErrorTransformacion, a_numero, aplicar_pasos, normalizar_fecha
from app.esquemas import ConfirmarEntrada, PasoEntrada
from app.modelos import ColumnaArchivo, MapeoCampos, PasoTransformacion, RegistroVenta, SesionTransformacion, TablaTransformada, Usuario
from app.servicios import archivos, auditoria


def _pasos(sesion):
    return [(p.tipo, p.columna_objetivo, p.parametros) for p in sesion.pasos]


def estado_actual(sesion: SesionTransformacion):
    """Reaplica todos los pasos sobre el archivo original (el original no cambia)."""
    return aplicar_pasos(archivos.leer_original(sesion.archivo), _pasos(sesion))


def salida(sesion, df, aviso=None) -> dict:
    return {"id": sesion.id, "archivo_id": sesion.archivo_id, "estado": sesion.estado,
            "pasos": [{"orden": p.orden, "tipo": p.tipo, "columna": p.columna_objetivo, "parametros": p.parametros} for p in sesion.pasos],
            "vista_previa": archivos.vista(df, aviso)}


def crear(bd: Session, usuario: Usuario, archivo_id: int) -> SesionTransformacion:
    archivo = archivos.obtener(bd, usuario, archivo_id)
    sesion = SesionTransformacion(archivo_id=archivo.id, usuario_id=usuario.id)
    bd.add(sesion)
    bd.commit()
    return sesion


def obtener(bd: Session, usuario: Usuario, sesion_id: int, solo_pendiente: bool = True) -> SesionTransformacion:
    sesion = bd.scalar(select(SesionTransformacion).where(SesionTransformacion.id == sesion_id, SesionTransformacion.usuario_id == usuario.id))
    if sesion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sesión no encontrada.")
    if solo_pendiente and sesion.estado != "pendiente":
        raise HTTPException(status.HTTP_409_CONFLICT, f"La sesión ya está {sesion.estado}.")
    return sesion


def aplicar(bd: Session, usuario: Usuario, sesion_id: int, paso: PasoEntrada):
    sesion = obtener(bd, usuario, sesion_id)
    nuevos = _pasos(sesion) + [(paso.tipo, paso.columna, paso.parametros)]
    try:  # se valida antes de guardar: si falla, el paso no se registra
        df, aviso = aplicar_pasos(archivos.leer_original(sesion.archivo), nuevos)
    except ErrorTransformacion as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
    sesion.pasos.append(PasoTransformacion(orden=len(sesion.pasos) + 1, tipo=paso.tipo, columna_objetivo=paso.columna, parametros=paso.parametros))
    bd.commit()
    return sesion, df, aviso


def deshacer(bd: Session, usuario: Usuario, sesion_id: int):
    sesion = obtener(bd, usuario, sesion_id)
    if not sesion.pasos:
        raise HTTPException(status.HTTP_409_CONFLICT, "No hay pasos para deshacer.")
    sesion.pasos.pop()  # cascade delete-orphan borra el paso en la base de datos
    bd.commit()
    df, aviso = estado_actual(sesion)
    return sesion, df, aviso


def cancelar(bd: Session, usuario: Usuario, sesion_id: int) -> None:
    sesion = obtener(bd, usuario, sesion_id)
    sesion.estado, sesion.cerrada_en = "cancelada", datetime.now()
    bd.commit()


def confirmar(bd: Session, usuario: Usuario, sesion_id: int, datos: ConfirmarEntrada) -> dict:
    sesion = obtener(bd, usuario, sesion_id)
    if bd.scalar(select(TablaTransformada).where(TablaTransformada.usuario_id == usuario.id, TablaTransformada.nombre == datos.nombre_tabla)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya tiene una tabla con ese nombre.")
    df, _ = estado_actual(sesion)
    for col in (datos.columna_fecha, datos.columna_valor):
        if col not in df.columns:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"La columna '{col}' no existe en el resultado.")
    # Mapeo de campos (solo si las columnas existen con su nombre original)
    cols = {c.nombre_original: c.id for c in sesion.archivo.columnas}
    if datos.columna_fecha in cols and datos.columna_valor in cols and not bd.scalar(select(MapeoCampos).where(MapeoCampos.archivo_id == sesion.archivo_id)):
        bd.add(MapeoCampos(archivo_id=sesion.archivo_id, columna_fecha_id=cols[datos.columna_fecha], columna_valor_id=cols[datos.columna_valor]))
    tabla = TablaTransformada(sesion_id=sesion.id, usuario_id=usuario.id, nombre=datos.nombre_tabla, filas=0, columnas=len(df.columns))
    bd.add(tabla)
    bd.flush()
    otras = [c for c in df.columns if c not in (datos.columna_fecha, datos.columna_valor)]
    registros, omitidas = [], 0
    for fila in df.to_dict("records"):
        fecha, valor = normalizar_fecha(fila[datos.columna_fecha]), a_numero(fila[datos.columna_valor])
        if fecha is None or valor is None:
            omitidas += 1  # filas sin fecha o valor válido no se pueden analizar
            continue
        registros.append(RegistroVenta(tabla_id=tabla.id, fecha=datetime.strptime(fecha, "%Y-%m-%d").date(), valor=round(valor, 2),
                                       datos={c: (None if fila[c] is None else str(fila[c])) for c in otras}))
    bd.add_all(registros)
    tabla.filas = len(registros)
    sesion.estado, sesion.cerrada_en = "confirmada", datetime.now()
    auditoria.registrar(bd, "confirmacion", usuario.id, f"tabla {tabla.id}: {tabla.nombre}")
    bd.commit()  # todo o nada: si algo falla antes, no se guarda nada
    return {"id": tabla.id, "nombre": tabla.nombre, "filas": tabla.filas, "columnas": tabla.columnas, "filas_omitidas": omitidas}
