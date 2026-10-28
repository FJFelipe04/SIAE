"""Contraseñas con bcrypt y tokens JWT."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import config
from app.db import obtener_sesion
from app.modelos import Usuario

esquema_bearer = HTTPBearer(auto_error=False)


def generar_hash(clave: str) -> str:
    return bcrypt.hashpw(clave.encode(), bcrypt.gensalt()).decode()


def verificar_clave(clave: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(clave.encode(), hash_guardado.encode())
    except ValueError:
        return False


def crear_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=config.minutos_token)
    return jwt.encode({"sub": str(usuario_id), "exp": expira}, config.secret_key, algorithm="HS256")


def usuario_actual(credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer),
                   bd: Session = Depends(obtener_sesion)) -> Usuario:
    """Dependencia que exige un token válido en el encabezado Authorization: Bearer <token>."""
    no_autorizado = HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión inválida o expirada. Inicie sesión de nuevo.")
    if credenciales is None:
        raise no_autorizado
    try:
        datos = jwt.decode(credenciales.credentials, config.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise no_autorizado
    usuario = bd.get(Usuario, int(datos["sub"]))
    if usuario is None or not usuario.activo:
        raise no_autorizado
    return usuario
