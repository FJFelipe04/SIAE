"""Registro e inicio de sesión (HU-01)."""
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import config
from app.esquemas import RegistroEntrada
from app.modelos import BitacoraAuditoria, Empresa, Usuario
from app.seguridad import crear_token, generar_hash, verificar_clave
from app.servicios import auditoria


def _empresa(bd: Session) -> Empresa:
    """SIAE es monoempresa: la empresa se crea la primera vez con los datos de la configuración."""
    empresa = bd.scalar(select(Empresa).where(Empresa.nit == config.empresa_nit))
    if empresa is None:
        empresa = Empresa(nombre=config.empresa_nombre, nit=config.empresa_nit)
        bd.add(empresa)
        bd.flush()
    return empresa


def registrar(bd: Session, datos: RegistroEntrada) -> Usuario:
    correo = datos.correo.lower()
    if bd.scalar(select(Usuario).where(Usuario.correo == correo)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese correo.")
    usuario = Usuario(empresa_id=_empresa(bd).id, nombre=datos.nombre.strip(), correo=correo,
                      contrasena_hash=generar_hash(datos.clave), perfil=datos.perfil)
    bd.add(usuario)
    bd.flush()
    auditoria.registrar(bd, "registro", usuario.id)
    bd.commit()
    return usuario


def iniciar_sesion(bd: Session, correo: str, clave: str, ip: str = None) -> str:
    correo = correo.lower()
    hace_15 = datetime.now() - timedelta(minutes=15)
    fallidos = bd.scalar(select(func.count()).select_from(BitacoraAuditoria).where(
        BitacoraAuditoria.accion == "login_fallido", BitacoraAuditoria.detalle == correo, BitacoraAuditoria.fecha >= hace_15))
    if fallidos >= config.intentos_maximos:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Demasiados intentos fallidos. Intente de nuevo en 15 minutos.")
    usuario = bd.scalar(select(Usuario).where(Usuario.correo == correo))
    if usuario is None or not usuario.activo or not verificar_clave(clave, usuario.contrasena_hash):
        auditoria.registrar(bd, "login_fallido", detalle=correo, ip=ip)
        bd.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos.")
    usuario.ultimo_acceso = datetime.now()
    auditoria.registrar(bd, "login_ok", usuario.id, ip=ip)
    bd.commit()
    return crear_token(usuario.id)
