"""Administración global de SIAE: usuarios, tablas de todos y bitácora (solo perfil administrador)."""

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.esquemas import UsuarioAdminCambio
from app.modelos import ArchivoVentas, BitacoraAuditoria, RegistroVenta, TablaTransformada, Usuario
from app.servicios import auditoria


def _conteo(bd: Session, modelo, usuario_id: Optional[int] = None) -> int:
    consulta = select(func.count()).select_from(modelo)
    if usuario_id is not None:
        consulta = consulta.where(modelo.usuario_id == usuario_id)
    return bd.scalar(consulta)


def resumen(bd: Session) -> dict:
    return {
        "usuarios": _conteo(bd, Usuario),
        "usuarios_activos": bd.scalar(select(func.count()).select_from(Usuario).where(Usuario.activo.is_(True))),
        "administradores": bd.scalar(
            select(func.count()).select_from(Usuario).where(Usuario.perfil == "administrador")
        ),
        "archivos": _conteo(bd, ArchivoVentas),
        "tablas": _conteo(bd, TablaTransformada),
        "registros": _conteo(bd, RegistroVenta),
    }


def _salida(bd: Session, u: Usuario) -> dict:
    return {
        "id": u.id,
        "nombre": u.nombre,
        "correo": u.correo,
        "perfil": u.perfil,
        "activo": u.activo,
        "creado_en": u.creado_en,
        "ultimo_acceso": u.ultimo_acceso,
        "archivos": _conteo(bd, ArchivoVentas, u.id),
        "tablas": _conteo(bd, TablaTransformada, u.id),
    }


def listar_usuarios(bd: Session) -> list:
    return [_salida(bd, u) for u in bd.scalars(select(Usuario).order_by(Usuario.id))]


def _proteger_al_propio_admin(admin: Usuario, usuario: Usuario, cambio: UsuarioAdminCambio) -> None:
    """Evita que el sistema se quede sin quien lo administre."""
    if usuario.id != admin.id:
        return
    if cambio.activo is False or cambio.perfil not in (None, "administrador"):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "No puede quitarse a sí mismo el rol de administrador ni desactivar su cuenta."
        )


def actualizar_usuario(bd: Session, admin: Usuario, usuario_id: int, cambio: UsuarioAdminCambio) -> dict:
    usuario = bd.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado.")
    _proteger_al_propio_admin(admin, usuario, cambio)
    if cambio.perfil and cambio.perfil != usuario.perfil:
        auditoria.registrar(
            bd, "admin_cambio_perfil", admin.id, f"{usuario.correo}: {usuario.perfil} → {cambio.perfil}"
        )
        usuario.perfil = cambio.perfil
    if cambio.activo is not None and cambio.activo != usuario.activo:
        accion = "admin_activa_usuario" if cambio.activo else "admin_desactiva_usuario"
        auditoria.registrar(bd, accion, admin.id, usuario.correo)
        usuario.activo = cambio.activo
    bd.commit()
    return _salida(bd, usuario)


def listar_tablas(bd: Session) -> list:
    filas = bd.execute(
        select(TablaTransformada, Usuario)
        .join(Usuario, TablaTransformada.usuario_id == Usuario.id)
        .order_by(TablaTransformada.creada_en.desc())
    ).all()
    return [
        {
            "id": t.id,
            "nombre": t.nombre,
            "filas": t.filas,
            "columnas": t.columnas,
            "creada_en": t.creada_en,
            "usuario_id": u.id,
            "propietario": u.nombre,
            "correo_propietario": u.correo,
        }
        for t, u in filas
    ]


def bitacora(bd: Session, limite: int = 100) -> list:
    filas = bd.execute(
        select(BitacoraAuditoria, Usuario.correo)
        .outerjoin(Usuario, BitacoraAuditoria.usuario_id == Usuario.id)
        .order_by(BitacoraAuditoria.id.desc())
        .limit(limite)
    ).all()
    return [
        {"id": b.id, "fecha": b.fecha, "accion": b.accion, "correo": correo, "detalle": b.detalle, "ip": b.ip}
        for b, correo in filas
    ]
