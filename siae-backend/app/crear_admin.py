"""Crea la cuenta de administrador o le da ese rol a una cuenta existente.

Se ejecuta en el servidor (no desde la web), así nadie puede volverse administrador registrándose:
    python -m app.crear_admin
La contraseña se escribe de forma oculta y nunca queda en el historial de la terminal.
"""

from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select

from app.db import SesionLocal
from app.esquemas import RegistroEntrada
from app.modelos import Usuario
from app.servicios import auditoria, autenticacion


def main() -> None:
    correo = input("Correo del administrador: ").strip().lower()
    with SesionLocal() as bd:
        usuario = bd.scalar(select(Usuario).where(Usuario.correo == correo))
        if usuario:
            usuario.perfil, usuario.activo = "administrador", True
            auditoria.registrar(bd, "admin_asignado_por_consola", usuario.id, correo)
            bd.commit()
            print(f"Listo: {usuario.nombre} ahora es administrador.")
            return
        nombre = input("Nombre completo: ").strip()
        clave = getpass("Contraseña (mínimo 8 caracteres): ")
        if clave != getpass("Repita la contraseña: "):
            raise SystemExit("Las contraseñas no coinciden.")
        try:
            datos = RegistroEntrada(nombre=nombre, correo=correo, clave=clave)
        except ValidationError as error:
            raise SystemExit("Datos inválidos: " + "; ".join(e["msg"] for e in error.errors()))
        usuario = autenticacion.registrar(bd, datos)
        usuario.perfil = "administrador"
        auditoria.registrar(bd, "admin_asignado_por_consola", usuario.id, correo)
        bd.commit()
        print(f"Listo: se creó la cuenta de administrador de {usuario.nombre}.")


if __name__ == "__main__":
    main()
