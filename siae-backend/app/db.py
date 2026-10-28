"""Conexión a la base de datos con SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import config

motor = create_engine(config.database_url, pool_pre_ping=True)
SesionLocal = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def obtener_sesion():
    """Dependencia de FastAPI: abre una sesión por petición y la cierra al final."""
    sesion = SesionLocal()
    try:
        yield sesion
    finally:
        sesion.close()
