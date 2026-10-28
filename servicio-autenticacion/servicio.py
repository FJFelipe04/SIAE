"""
Servicio web de registro e inicio de sesión (caso GA7-220501096-AA5-EV01).

- POST /registro  {usuario, contrasena}  -> crea el usuario (la contraseña se guarda con bcrypt).
- POST /login     {usuario, contrasena}  -> "Autenticación satisfactoria" o "Error en la autenticación".

Ejecutar:  uvicorn servicio:app --port 8001
"""
import os
import sqlite3

import bcrypt
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

RUTA_BD = os.getenv("AUTH_BD", "usuarios.db")

app = FastAPI(title="Servicio de autenticación", version="1.0.0")


class Credenciales(BaseModel):
    """Datos que recibe el servicio. El usuario solo admite letras, números, punto y guion bajo."""
    usuario: str = Field(min_length=4, max_length=30, pattern=r"^[A-Za-z0-9._]+$", examples=["juanfe"])
    contrasena: str = Field(min_length=8, max_length=72, examples=["Clave2026"])


def conectar() -> sqlite3.Connection:
    conexion = sqlite3.connect(RUTA_BD)
    conexion.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT PRIMARY KEY, hash TEXT NOT NULL)")
    return conexion


@app.post("/registro", status_code=status.HTTP_201_CREATED, summary="Registrar un usuario")
def registrar(datos: Credenciales):
    hash_clave = bcrypt.hashpw(datos.contrasena.encode(), bcrypt.gensalt()).decode()
    with conectar() as conexion:
        try:
            conexion.execute("INSERT INTO usuarios (usuario, hash) VALUES (?, ?)", (datos.usuario.lower(), hash_clave))
        except sqlite3.IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya existe.")
    return {"mensaje": "Usuario registrado correctamente", "usuario": datos.usuario.lower()}


@app.post("/login", summary="Iniciar sesión")
def login(datos: Credenciales):
    with conectar() as conexion:
        fila = conexion.execute("SELECT hash FROM usuarios WHERE usuario = ?", (datos.usuario.lower(),)).fetchone()
    # Mismo mensaje si el usuario no existe o la contraseña es incorrecta: no se revela cuál falló.
    if fila is None or not bcrypt.checkpw(datos.contrasena.encode(), fila[0].encode()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Error en la autenticación")
    return {"mensaje": "Autenticación satisfactoria", "usuario": datos.usuario.lower()}
