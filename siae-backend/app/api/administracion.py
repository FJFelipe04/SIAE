"""Rutas de administración global (solo perfil administrador)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import obtener_sesion
from app.esquemas import (
    EventoAuditoriaSalida,
    ResumenAdminSalida,
    TablaGlobalSalida,
    UsuarioAdminCambio,
    UsuarioAdminSalida,
)
from app.modelos import Usuario
from app.seguridad import solo_administrador
from app.servicios import administracion as srv

ruta = APIRouter(prefix="/admin", tags=["Administración"])


@ruta.get("/resumen", response_model=ResumenAdminSalida, summary="Cifras generales del sistema")
def resumen(admin: Usuario = Depends(solo_administrador), bd: Session = Depends(obtener_sesion)):
    return srv.resumen(bd)


@ruta.get("/usuarios", response_model=list[UsuarioAdminSalida], summary="Listar todos los usuarios")
def usuarios(admin: Usuario = Depends(solo_administrador), bd: Session = Depends(obtener_sesion)):
    return srv.listar_usuarios(bd)


@ruta.patch(
    "/usuarios/{usuario_id}", response_model=UsuarioAdminSalida, summary="Cambiar el perfil o activar/desactivar"
)
def actualizar(
    usuario_id: int,
    cambio: UsuarioAdminCambio,
    admin: Usuario = Depends(solo_administrador),
    bd: Session = Depends(obtener_sesion),
):
    return srv.actualizar_usuario(bd, admin, usuario_id, cambio)


@ruta.get("/tablas", response_model=list[TablaGlobalSalida], summary="Listar las tablas de todos los usuarios")
def tablas(admin: Usuario = Depends(solo_administrador), bd: Session = Depends(obtener_sesion)):
    return srv.listar_tablas(bd)


@ruta.get("/auditoria", response_model=list[EventoAuditoriaSalida], summary="Últimos eventos de la bitácora")
def auditoria(
    limite: int = Query(100, ge=1, le=500),
    admin: Usuario = Depends(solo_administrador),
    bd: Session = Depends(obtener_sesion),
):
    return srv.bitacora(bd, limite)
