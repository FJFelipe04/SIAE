"""Esquemas Pydantic: validan lo que entra y documentan lo que sale de la API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class RegistroEntrada(BaseModel):
    nombre: str = Field(min_length=3, max_length=100, examples=["Laura Gómez"])
    correo: EmailStr = Field(examples=["laura@comercialandina.co"])
    clave: str = Field(min_length=8, max_length=72, examples=["Ventas2026"])
    perfil: Literal["analista", "jefe_comercial"] = "analista"


class LoginEntrada(BaseModel):
    correo: EmailStr
    clave: str = Field(min_length=1, max_length=72)


class TokenSalida(BaseModel):
    mensaje: str
    access_token: str
    token_type: str = "bearer"


class UsuarioSalida(BaseModel):
    id: int
    nombre: str
    correo: str
    perfil: str


class UsuarioAdminSalida(UsuarioSalida):
    activo: bool
    creado_en: datetime
    ultimo_acceso: Optional[datetime] = None
    archivos: int
    tablas: int


class UsuarioAdminCambio(BaseModel):
    perfil: Optional[Literal["analista", "jefe_comercial", "administrador"]] = None
    activo: Optional[bool] = None


class TablaGlobalSalida(BaseModel):
    id: int
    nombre: str
    filas: int
    columnas: int
    creada_en: datetime
    usuario_id: int
    propietario: str
    correo_propietario: str


class EventoAuditoriaSalida(BaseModel):
    id: int
    fecha: datetime
    accion: str
    correo: Optional[str] = None
    detalle: Optional[str] = None
    ip: Optional[str] = None


class ResumenAdminSalida(BaseModel):
    usuarios: int
    usuarios_activos: int
    administradores: int
    archivos: int
    tablas: int
    registros: int


class VistaPrevia(BaseModel):
    columnas: list[str]
    filas: list[list[Any]]
    total_filas: int
    aviso: Optional[str] = None


class ArchivoSalida(BaseModel):
    id: int
    nombre_original: str
    formato: str
    cantidad_registros: int
    columnas: list[dict]
    vista_previa: VistaPrevia


class PasoEntrada(BaseModel):
    tipo: Literal[
        "eliminar_columna",
        "renombrar_columna",
        "cambiar_tipo",
        "formato_fecha",
        "quitar_duplicados",
        "quitar_caracteres",
    ]
    columna: Optional[str] = None
    parametros: dict = Field(default_factory=dict, examples=[{"nuevo": "valor_venta"}])


class SesionSalida(BaseModel):
    id: int
    archivo_id: int
    estado: str
    pasos: list[dict]
    vista_previa: VistaPrevia


class ConfirmarEntrada(BaseModel):
    nombre_tabla: str = Field(
        min_length=3, max_length=100, pattern=r"^[A-Za-z0-9_\-]+$", examples=["ventas_sep_2026_limpia"]
    )
    columna_fecha: str
    columna_valor: str


class TablaSalida(BaseModel):
    id: int
    nombre: str
    filas: int
    columnas: int
    filas_omitidas: int = 0


class ReporteEntrada(BaseModel):
    tabla_id: int
    tipo: Literal["tabla_dinamica", "barras", "lineas", "torta"] = "lineas"
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    agrupacion: Literal["dia", "mes", "anio"] = "mes"


class ReporteSalida(BaseModel):
    id: int
    tipo: str
    agrupacion: str
    serie: list[dict]
    indicadores: dict
