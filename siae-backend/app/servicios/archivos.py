"""Carga de archivos de ventas y vista previa (HU-02)."""
import hashlib
import io
import os
import uuid

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import config
from app.dominio.transformaciones import a_numero, normalizar_fecha
from app.modelos import ArchivoVentas, ColumnaArchivo, Usuario
from app.servicios import auditoria

FILAS_VISTA = 50


def leer_tabla(contenido: bytes, formato: str) -> pd.DataFrame:
    """Lee el archivo como texto (dtype=str) para no alterar los datos originales."""
    if formato == "csv":
        texto = contenido.decode("utf-8-sig", errors="replace")
        primera = texto.splitlines()[0] if texto else ""
        sep = ";" if primera.count(";") > primera.count(",") else ","
        return pd.read_csv(io.StringIO(texto), sep=sep, dtype=str, keep_default_na=False)
    return pd.read_excel(io.BytesIO(contenido), dtype=str, keep_default_na=False, engine="openpyxl")


def detectar_tipo(serie: pd.Series) -> str:
    muestra = [v for v in serie.head(100) if str(v).strip()]
    if muestra and all(normalizar_fecha(v) for v in muestra):
        return "fecha"
    if muestra and all(a_numero(v) is not None for v in muestra):
        return "numero"
    return "texto"


def vista(df: pd.DataFrame, aviso=None) -> dict:
    filas = df.head(FILAS_VISTA).astype(object).where(df.head(FILAS_VISTA).notna(), None).values.tolist()
    return {"columnas": [str(c) for c in df.columns], "filas": filas, "total_filas": len(df), "aviso": aviso}


def cargar(bd: Session, usuario: Usuario, nombre: str, contenido: bytes) -> tuple[ArchivoVentas, pd.DataFrame]:
    formato = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if formato not in ("xlsx", "csv"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"El archivo {nombre} no es .xlsx ni .csv.")
    if len(contenido) > config.max_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "El archivo supera el límite de 50 MB.")
    try:
        df = leer_tabla(contenido, formato)
    except Exception:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "No se pudo leer el archivo. Verifique que no esté dañado.")
    if len(df) > config.max_registros:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El archivo supera los 500.000 registros.")
    if df.columns.empty:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "El archivo no tiene encabezados.")
    carpeta = os.path.join(config.almacenamiento, str(usuario.id))
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{uuid.uuid4().hex}.{formato}")
    with open(ruta, "wb") as f:  # el original se guarda tal cual y nunca se modifica
        f.write(contenido)
    archivo = ArchivoVentas(usuario_id=usuario.id, nombre_original=nombre[:255], formato=formato, tamano_bytes=len(contenido),
                            cantidad_registros=len(df), ruta_almacenamiento=ruta, hash_sha256=hashlib.sha256(contenido).hexdigest())
    archivo.columnas = [ColumnaArchivo(nombre_original=str(c)[:150], posicion=i + 1, tipo_detectado=detectar_tipo(df[c]))
                        for i, c in enumerate(df.columns)]
    bd.add(archivo)
    bd.flush()
    auditoria.registrar(bd, "carga", usuario.id, f"archivo {archivo.id}: {nombre}")
    bd.commit()
    return archivo, df


def obtener(bd: Session, usuario: Usuario, archivo_id: int) -> ArchivoVentas:
    archivo = bd.scalar(select(ArchivoVentas).where(ArchivoVentas.id == archivo_id, ArchivoVentas.usuario_id == usuario.id))
    if archivo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Archivo no encontrado.")
    return archivo


def leer_original(archivo: ArchivoVentas) -> pd.DataFrame:
    with open(archivo.ruta_almacenamiento, "rb") as f:
        contenido = f.read()
    if hashlib.sha256(contenido).hexdigest() != archivo.hash_sha256:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "El archivo original fue alterado.")
    return leer_tabla(contenido, archivo.formato)
