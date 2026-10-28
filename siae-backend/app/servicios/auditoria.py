"""Registro de acciones en la bitácora de auditoría."""

from typing import Optional

from sqlalchemy.orm import Session

from app.modelos import BitacoraAuditoria


def registrar(
    bd: Session, accion: str, usuario_id: Optional[int] = None, detalle: Optional[str] = None, ip: Optional[str] = None
) -> None:
    bd.add(BitacoraAuditoria(usuario_id=usuario_id, accion=accion, detalle=detalle, ip=ip))
