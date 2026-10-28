"""Rutas de sesiones de transformación."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import obtener_sesion
from app.esquemas import ConfirmarEntrada, PasoEntrada, SesionSalida, TablaSalida
from app.modelos import Usuario
from app.seguridad import usuario_actual
from app.servicios import transformacion as srv

ruta = APIRouter(prefix="/sesiones", tags=["Transformación"])


@ruta.post("", response_model=SesionSalida, status_code=status.HTTP_201_CREATED, summary="Iniciar una sesión de transformación")
def crear(archivo_id: int, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    sesion = srv.crear(bd, usuario, archivo_id)
    df, aviso = srv.estado_actual(sesion)
    return srv.salida(sesion, df, aviso)


@ruta.get("/{sesion_id}", response_model=SesionSalida, summary="Ver la sesión con la vista previa actual")
def ver(sesion_id: int, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    sesion = srv.obtener(bd, usuario, sesion_id, solo_pendiente=False)
    df, aviso = srv.estado_actual(sesion)
    return srv.salida(sesion, df, aviso)


@ruta.post("/{sesion_id}/pasos", response_model=SesionSalida, summary="Aplicar una transformación")
def aplicar(sesion_id: int, paso: PasoEntrada, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    sesion, df, aviso = srv.aplicar(bd, usuario, sesion_id, paso)
    return srv.salida(sesion, df, aviso)


@ruta.delete("/{sesion_id}/pasos/ultimo", response_model=SesionSalida, summary="Deshacer el último paso")
def deshacer(sesion_id: int, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    sesion, df, aviso = srv.deshacer(bd, usuario, sesion_id)
    return srv.salida(sesion, df, aviso)


@ruta.post("/{sesion_id}/confirmar", response_model=TablaSalida, status_code=status.HTTP_201_CREATED, summary="Confirmar y generar la tabla transformada")
def confirmar(sesion_id: int, datos: ConfirmarEntrada, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    return srv.confirmar(bd, usuario, sesion_id, datos)


@ruta.post("/{sesion_id}/cancelar", status_code=status.HTTP_204_NO_CONTENT, summary="Cancelar sin guardar")
def cancelar(sesion_id: int, usuario: Usuario = Depends(usuario_actual), bd: Session = Depends(obtener_sesion)):
    srv.cancelar(bd, usuario, sesion_id)
