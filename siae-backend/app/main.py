"""Punto de entrada de la API de SIAE.

Ejecutar en desarrollo:  uvicorn app.main:app --reload
Documentación interactiva: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import administracion, archivos, auth, sesiones, tablas

app = FastAPI(
    title="SIAE API",
    version="1.0.0",
    description="Sistema de Inteligencia Analítica Empresarial: carga, transformación y análisis de datos de ventas.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
for modulo in (auth, archivos, sesiones, tablas, administracion):
    app.include_router(modulo.ruta)


@app.get("/salud", tags=["Sistema"], summary="Comprobar que la API está en línea")
def salud():
    return {"estado": "ok"}
