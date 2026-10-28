import importlib
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def cliente():
    os.environ["AUTH_BD"] = os.path.join(tempfile.mkdtemp(), "prueba.db")
    import servicio
    importlib.reload(servicio)
    return TestClient(servicio.app)


def test_registro_y_login_correcto(cliente):
    assert cliente.post("/registro", json={"usuario": "juanfe", "contrasena": "Clave2026"}).status_code == 201
    r = cliente.post("/login", json={"usuario": "juanfe", "contrasena": "Clave2026"})
    assert r.status_code == 200 and r.json()["mensaje"] == "Autenticación satisfactoria"


def test_login_incorrecto(cliente):
    cliente.post("/registro", json={"usuario": "juanfe", "contrasena": "Clave2026"})
    for datos in ({"usuario": "juanfe", "contrasena": "otraClave1"}, {"usuario": "noexiste", "contrasena": "Clave2026"}):
        r = cliente.post("/login", json=datos)
        assert r.status_code == 401 and r.json()["detail"] == "Error en la autenticación"


def test_usuario_repetido(cliente):
    cliente.post("/registro", json={"usuario": "juanfe", "contrasena": "Clave2026"})
    assert cliente.post("/registro", json={"usuario": "JuanFe", "contrasena": "Clave2026"}).status_code == 409


@pytest.mark.parametrize("datos", [{"usuario": "ab", "contrasena": "Clave2026"}, {"usuario": "juan fe", "contrasena": "Clave2026"},
                                   {"usuario": "juanfe", "contrasena": "corta"}, {"usuario": "juanfe"}])
def test_validaciones(cliente, datos):
    assert cliente.post("/registro", json=datos).status_code == 422
