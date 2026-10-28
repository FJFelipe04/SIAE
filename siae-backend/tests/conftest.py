"""Configuración de pruebas: base de datos PostgreSQL de prueba creada desde el script SQL del proyecto."""

import os
import pathlib
import tempfile

import psycopg2
import pytest

URL_ADMIN = os.getenv("SIAE_TEST_ADMIN", "postgresql://postgres@127.0.0.1:54329/postgres")
BD_PRUEBA = "siae_test"
os.environ["SIAE_DATABASE_URL"] = (
    URL_ADMIN.rsplit("/", 1)[0].replace("postgresql://", "postgresql+psycopg2://") + "/" + BD_PRUEBA
)
os.environ["SIAE_ALMACENAMIENTO"] = tempfile.mkdtemp(prefix="siae_archivos_")
os.environ["SIAE_EMPRESA_NIT"] = "900123456-7"

DDL = pathlib.Path(__file__).resolve().parents[1] / "sql" / "siae_postgresql.sql"


def _recrear_bd():
    cn = psycopg2.connect(URL_ADMIN)
    cn.autocommit = True
    with cn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {BD_PRUEBA} WITH (FORCE)")
        cur.execute(f"CREATE DATABASE {BD_PRUEBA}")
    cn.close()
    cn = psycopg2.connect(URL_ADMIN.rsplit("/", 1)[0] + "/" + BD_PRUEBA)
    cn.autocommit = True
    with cn.cursor() as cur:
        cur.execute(DDL.read_text())
    cn.close()


@pytest.fixture()
def cliente():
    _recrear_bd()
    from fastapi.testclient import TestClient
    from app.db import motor
    from app.main import app

    motor.dispose()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def token(cliente):
    cliente.post(
        "/auth/registro", json={"nombre": "Laura Gómez", "correo": "laura@comercialandina.co", "clave": "Ventas2026"}
    )
    r = cliente.post("/auth/login", json={"correo": "laura@comercialandina.co", "clave": "Ventas2026"})
    return {"Authorization": "Bearer " + r.json()["access_token"]}


CSV_EJEMPLO = (
    "Fecha;Cliente;Producto;Cantidad;Valor;Vendedor;Ciudad;Observaciones\n"
    "01/08/2026;Cliente A;Producto 1;3;45.000;Vendedor 1;Neiva;-\n"
    "15/08/2026;Cliente C;Producto 3;2;98.000;Vendedor 1;Neiva;\n"
    "02-09-2026;Cliente B;Producto 2;1;120.000;Vendedor 2;Pitalito;pago contado\n"
    "02-09-2026;Cliente B;Producto 2;1;120.000;Vendedor 2;Pitalito;pago contado\n"
    "2026-09-10;Cliente D;Producto 1;5;75.000;Vendedor 3;Garzón;\"cliente nuevo; referido\"\n"
    "20/09/2026;Cliente A;Producto 4;1;$ 210.500;Vendedor 1;Neiva;\n"
    "05/10/2026;Cliente E;Producto 2;2;240.000;Vendedor 2;Pitalito;\n"
    "sin fecha;Cliente F;Producto 1;1;15.000;Vendedor 3;Neiva;dato con error\n"
)


@pytest.fixture()
def archivo_id(cliente, token):
    r = cliente.post("/archivos", headers=token, files={"archivo": ("ventas.csv", CSV_EJEMPLO.encode(), "text/csv")})
    return r.json()["id"]
