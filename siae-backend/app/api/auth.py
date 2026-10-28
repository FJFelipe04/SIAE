"""Rutas de autenticación."""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.db import obtener_sesion
from app.esquemas import LoginEntrada, RegistroEntrada, TokenSalida, UsuarioSalida
from app.modelos import Usuario
from app.seguridad import usuario_actual
from app.servicios import autenticacion

ruta = APIRouter(prefix="/auth", tags=["Autenticación"])


@ruta.post("/registro", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED, summary="Registrar un usuario")
def registrar(datos: RegistroEntrada, bd: Session = Depends(obtener_sesion)):
    u = autenticacion.registrar(bd, datos)
    return UsuarioSalida(id=u.id, nombre=u.nombre, correo=u.correo, perfil=u.perfil)


@ruta.post("/login", response_model=TokenSalida, summary="Iniciar sesión y obtener un token")
def login(datos: LoginEntrada, request: Request, bd: Session = Depends(obtener_sesion)):
    token = autenticacion.iniciar_sesion(bd, datos.correo, datos.clave, request.client.host if request.client else None)
    return TokenSalida(mensaje="Autenticación satisfactoria", access_token=token)


@ruta.get("/yo", response_model=UsuarioSalida, summary="Datos del usuario autenticado")
def yo(usuario: Usuario = Depends(usuario_actual)):
    return UsuarioSalida(id=usuario.id, nombre=usuario.nombre, correo=usuario.correo, perfil=usuario.perfil)
