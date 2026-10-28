"""Modelos ORM. Corresponden 1 a 1 con sql/siae_postgresql.sql."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

TIPOS_TRANSFORMACION = (
    "eliminar_columna",
    "renombrar_columna",
    "cambiar_tipo",
    "formato_fecha",
    "quitar_duplicados",
    "quitar_caracteres",
)


class Empresa(Base):
    __tablename__ = "empresa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    nit: Mapped[str] = mapped_column(String(20), unique=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (CheckConstraint("perfil IN ('analista','jefe_comercial')"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    correo: Mapped[str] = mapped_column(String(150), unique=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20), default="analista")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ArchivoVentas(Base):
    __tablename__ = "archivo_ventas"
    __table_args__ = (
        CheckConstraint("formato IN ('xlsx','csv')"),
        CheckConstraint("tamano_bytes <= 52428800"),
        CheckConstraint("cantidad_registros <= 500000"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    nombre_original: Mapped[str] = mapped_column(String(255))
    formato: Mapped[str] = mapped_column(String(4))
    tamano_bytes: Mapped[int] = mapped_column(BigInteger)
    cantidad_registros: Mapped[int] = mapped_column(Integer)
    ruta_almacenamiento: Mapped[str] = mapped_column(String(500))
    hash_sha256: Mapped[str] = mapped_column(String(64))
    cargado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    columnas: Mapped[list["ColumnaArchivo"]] = relationship(
        order_by="ColumnaArchivo.posicion", cascade="all, delete-orphan"
    )


class ColumnaArchivo(Base):
    __tablename__ = "columna_archivo"
    __table_args__ = (CheckConstraint("tipo_detectado IN ('texto','numero','fecha')"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    archivo_id: Mapped[int] = mapped_column(ForeignKey("archivo_ventas.id", ondelete="CASCADE"))
    nombre_original: Mapped[str] = mapped_column(String(150))
    posicion: Mapped[int] = mapped_column(SmallInteger)
    tipo_detectado: Mapped[str] = mapped_column(String(10))


class MapeoCampos(Base):
    __tablename__ = "mapeo_campos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    archivo_id: Mapped[int] = mapped_column(ForeignKey("archivo_ventas.id"), unique=True)
    columna_fecha_id: Mapped[int] = mapped_column(ForeignKey("columna_archivo.id"))
    columna_valor_id: Mapped[int] = mapped_column(ForeignKey("columna_archivo.id"))


class SesionTransformacion(Base):
    __tablename__ = "sesion_transformacion"
    __table_args__ = (CheckConstraint("estado IN ('pendiente','confirmada','cancelada')"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    archivo_id: Mapped[int] = mapped_column(ForeignKey("archivo_ventas.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    estado: Mapped[str] = mapped_column(String(12), default="pendiente")
    iniciada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    cerrada_en: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    pasos: Mapped[list["PasoTransformacion"]] = relationship(
        order_by="PasoTransformacion.orden", cascade="all, delete-orphan"
    )
    archivo: Mapped[ArchivoVentas] = relationship()


class PasoTransformacion(Base):
    __tablename__ = "paso_transformacion"
    __table_args__ = (UniqueConstraint("sesion_id", "orden"), CheckConstraint(f"tipo IN {TIPOS_TRANSFORMACION}"))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sesion_id: Mapped[int] = mapped_column(ForeignKey("sesion_transformacion.id", ondelete="CASCADE"))
    orden: Mapped[int] = mapped_column(SmallInteger)
    tipo: Mapped[str] = mapped_column(String(25))
    columna_objetivo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    parametros: Mapped[dict] = mapped_column(JSONB, default=dict)
    aplicado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TablaTransformada(Base):
    __tablename__ = "tabla_transformada"
    __table_args__ = (UniqueConstraint("usuario_id", "nombre"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sesion_id: Mapped[int] = mapped_column(ForeignKey("sesion_transformacion.id"), unique=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    filas: Mapped[int] = mapped_column(Integer)
    columnas: Mapped[int] = mapped_column(SmallInteger)
    creada_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class RegistroVenta(Base):
    __tablename__ = "registro_venta"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tabla_id: Mapped[int] = mapped_column(ForeignKey("tabla_transformada.id", ondelete="CASCADE"))
    fecha: Mapped[date] = mapped_column(Date)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    datos: Mapped[dict] = mapped_column(JSONB, default=dict)


class Reporte(Base):
    __tablename__ = "reporte"
    __table_args__ = (
        CheckConstraint("tipo IN ('tabla_dinamica','barras','lineas','torta')"),
        CheckConstraint("agrupacion IN ('dia','mes','anio')"),
        CheckConstraint(
            "fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio", name="ck_reporte_rango"
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tabla_id: Mapped[int] = mapped_column(ForeignKey("tabla_transformada.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    tipo: Mapped[str] = mapped_column(String(15))
    fecha_inicio: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    agrupacion: Mapped[str] = mapped_column(String(10), default="mes")
    generado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    indicadores: Mapped[list["Indicador"]] = relationship(cascade="all, delete-orphan")


class Indicador(Base):
    __tablename__ = "indicador"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporte_id: Mapped[int] = mapped_column(ForeignKey("reporte.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(60))
    valor: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    formula: Mapped[str] = mapped_column(String(200))


class BitacoraAuditoria(Base):
    __tablename__ = "bitacora_auditoria"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    accion: Mapped[str] = mapped_column(String(40))
    detalle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
