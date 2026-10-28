"""Configuración leída de variables de entorno (ver .env.example)."""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Configuracion:
    database_url: str = field(
        default_factory=lambda: os.getenv("SIAE_DATABASE_URL", "postgresql+psycopg2://postgres@127.0.0.1:5432/siae")
    )
    secret_key: str = field(default_factory=lambda: os.getenv("SIAE_SECRET_KEY", "solo-para-desarrollo"))
    almacenamiento: str = field(default_factory=lambda: os.getenv("SIAE_ALMACENAMIENTO", "./almacenamiento"))
    empresa_nombre: str = field(default_factory=lambda: os.getenv("SIAE_EMPRESA_NOMBRE", "Empresa de prueba"))
    empresa_nit: str = field(default_factory=lambda: os.getenv("SIAE_EMPRESA_NIT", "000000000-0"))
    minutos_token: int = 30  # cierre de sesión por inactividad
    max_bytes: int = 50 * 1024 * 1024  # 50 MB
    max_registros: int = 500_000
    intentos_maximos: int = 5  # bloqueo temporal de inicio de sesión


config = Configuracion()
