"""Rutas de carga de archivos."""
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import obtener_sesion
from app.esquemas import ArchivoSalida
from app.modelos import ArchivoVentas, Usuario
from app.seguridad import usuario_actual
from app.servicios import archivos

ruta = APIRouter(prefix="/archivos", tags=["Archivos"])


def _salida(archivo, df):
    return {"id": archivo.id, "nombre_original": archivo.nombre_original, "formato": archivo.formato, "cantidad_registros": archivo.cantidad_registros,
            "columnas": [{"id": c.id, "nombre": c.nombre_original, "posicion": c.posicion, "tipo": c.tipo_detectado} for c in archivo.columnas],
            "vista_previa": archivos.vista(df)}


@ruta.post("", response_model=ArchivoSalida, status_code=status.HTTP_201_CREATED, summary="Cargar un archivo .xlsx o .csv")
async def cargar(archivo: UploadFile = File(...), usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    contenido = await archivo.read()
    registro, df = archivos.cargar(bd, usuario, archivo.filename or "sin_nombre", contenido)
    return _salida(registro, df)


@ruta.get("", summary="Listar mis archivos")
def listar(usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    filas = bd.scalars(select(ArchivoVentas).where(ArchivoVentas.usuario_id == usuario.id).order_by(ArchivoVentas.cargado_en.desc()))
    return [{"id": a.id, "nombre_original": a.nombre_original, "cantidad_registros": a.cantidad_registros, "cargado_en": a.cargado_en} for a in filas]


@ruta.get("/{archivo_id}", response_model=ArchivoSalida, summary="Ver un archivo y su vista previa original")
def ver(archivo_id: int, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    archivo = archivos.obtener(bd, usuario, archivo_id)
    return _salida(archivo, archivos.leer_original(archivo))
