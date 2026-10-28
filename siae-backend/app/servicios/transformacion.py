"""Sesiones de transformación: aplicar, deshacer, confirmar y cancelar (HU-03 y HU-04)."""

import csv
import io
import json
from datetime import datetime

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dominio.transformaciones import ErrorTransformacion, a_numero, aplicar_pasos, normalizar_fecha
from app.esquemas import ConfirmarEntrada, PasoEntrada
from app.modelos import MapeoCampos, PasoTransformacion, SesionTransformacion, TablaTransformada, Usuario
from app.servicios import archivos, auditoria


def _pasos(sesion):
    return [(p.tipo, p.columna_objetivo, p.parametros) for p in sesion.pasos]


def estado_actual(sesion: SesionTransformacion):
    """Reaplica todos los pasos sobre el archivo original (el original no cambia)."""
    return aplicar_pasos(archivos.leer_original(sesion.archivo), _pasos(sesion))


def salida(sesion, df, aviso=None) -> dict:
    return {
        "id": sesion.id,
        "archivo_id": sesion.archivo_id,
        "estado": sesion.estado,
        "pasos": [
            {"orden": p.orden, "tipo": p.tipo, "columna": p.columna_objetivo, "parametros": p.parametros}
            for p in sesion.pasos
        ],
        "vista_previa": archivos.vista(df, aviso),
    }


def crear(bd: Session, usuario: Usuario, archivo_id: int) -> SesionTransformacion:
    archivo = archivos.obtener(bd, usuario, archivo_id)
    sesion = SesionTransformacion(archivo_id=archivo.id, usuario_id=usuario.id)
    bd.add(sesion)
    bd.commit()
    return sesion


def obtener(bd: Session, usuario: Usuario, sesion_id: int, solo_pendiente: bool = True) -> SesionTransformacion:
    sesion = bd.scalar(
        select(SesionTransformacion).where(
            SesionTransformacion.id == sesion_id, SesionTransformacion.usuario_id == usuario.id
        )
    )
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
    sesion.pasos.append(
        PasoTransformacion(
            orden=len(sesion.pasos) + 1, tipo=paso.tipo, columna_objetivo=paso.columna, parametros=paso.parametros
        )
    )
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


def _validar_confirmacion(bd: Session, usuario: Usuario, df, datos: ConfirmarEntrada) -> None:
    repetida = select(TablaTransformada).where(
        TablaTransformada.usuario_id == usuario.id, TablaTransformada.nombre == datos.nombre_tabla
    )
    if bd.scalar(repetida):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya tiene una tabla con ese nombre.")
    for col in (datos.columna_fecha, datos.columna_valor):
        if col not in df.columns:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"La columna '{col}' no existe en el resultado.")


def _guardar_mapeo(bd: Session, sesion: SesionTransformacion, datos: ConfirmarEntrada) -> None:
    """Guarda qué columnas son fecha y valor, solo si conservan su nombre original."""
    cols = {c.nombre_original: c.id for c in sesion.archivo.columnas}
    if datos.columna_fecha not in cols or datos.columna_valor not in cols:
        return
    if bd.scalar(select(MapeoCampos).where(MapeoCampos.archivo_id == sesion.archivo_id)):
        return
    bd.add(
        MapeoCampos(
            archivo_id=sesion.archivo_id,
            columna_fecha_id=cols[datos.columna_fecha],
            columna_valor_id=cols[datos.columna_valor],
        )
    )


def _copiar_registros(bd: Session, tabla_id: int, df, datos: ConfirmarEntrada) -> tuple:
    """Inserta las filas válidas con COPY de PostgreSQL y devuelve (guardadas, omitidas).

    Antes se creaba un objeto ORM por fila y 500.000 filas tardaban 34,7 s (defecto DEF-01).
    """
    otras = [c for c in df.columns if c not in (datos.columna_fecha, datos.columna_valor)]
    fechas = df[datos.columna_fecha].map(normalizar_fecha)
    valores = df[datos.columna_valor].map(a_numero)
    validas = fechas.notna() & valores.notna()  # filas sin fecha o valor válido no se pueden analizar
    extras = [
        {c: (None if pd.isna(v) else str(v)) for c, v in zip(otras, fila)}
        for fila in df.loc[validas, otras].itertuples(index=False, name=None)
    ]
    buffer = io.StringIO()
    escritor = csv.writer(buffer)
    for f, v, e in zip(fechas[validas], valores[validas], extras):
        escritor.writerow([tabla_id, f, round(v, 2), json.dumps(e, ensure_ascii=False)])
    buffer.seek(0)
    cursor = bd.connection().connection.cursor()
    cursor.copy_expert("COPY registro_venta (tabla_id, fecha, valor, datos) FROM STDIN WITH (FORMAT csv)", buffer)
    return int(validas.sum()), int((~validas).sum())


def confirmar(bd: Session, usuario: Usuario, sesion_id: int, datos: ConfirmarEntrada) -> dict:
    sesion = obtener(bd, usuario, sesion_id)
    df, _ = estado_actual(sesion)
    _validar_confirmacion(bd, usuario, df, datos)
    _guardar_mapeo(bd, sesion, datos)
    tabla = TablaTransformada(
        sesion_id=sesion.id, usuario_id=usuario.id, nombre=datos.nombre_tabla, filas=0, columnas=len(df.columns)
    )
    bd.add(tabla)
    bd.flush()
    tabla.filas, omitidas = _copiar_registros(bd, tabla.id, df, datos)
    sesion.estado, sesion.cerrada_en = "confirmada", datetime.now()
    auditoria.registrar(bd, "confirmacion", usuario.id, f"tabla {tabla.id}: {tabla.nombre}")
    bd.commit()  # todo o nada: si algo falla antes, no se guarda nada
    return {
        "id": tabla.id,
        "nombre": tabla.nombre,
        "filas": tabla.filas,
        "columnas": tabla.columnas,
        "filas_omitidas": omitidas,
    }
