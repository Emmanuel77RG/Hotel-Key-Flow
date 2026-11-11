"""
Pruebas de Control de Acceso Basado en Roles (RBAC) y Seguridad de Endpoints.
"""
import pytest


def test_endpoint_protegido_sin_token_devuelve_401(client):
    respuesta = client.get("/habitaciones/")
    assert respuesta.status_code == 401


def test_usuario_limpieza_no_puede_crear_habitacion_devuelve_403(client, headers_limpieza):
    payload = {
        "numero_habitacion": "999",
        "tipo": "Suite Presidencial",
        "capacidad": 2,
        "precio_base": 1500.0,
    }
    respuesta = client.post("/habitaciones/", json=payload, headers=headers_limpieza)
    assert respuesta.status_code == 403
    assert "Acceso denegado" in respuesta.json()["detail"]


def test_administrador_puede_crear_habitacion_exitosamente_201(client, headers_admin):
    payload = {
        "numero_habitacion": "101",
        "tipo": "Sencilla",
        "capacidad": 1,
        "precio_base": 650.0,
    }
    respuesta = client.post("/habitaciones/", json=payload, headers=headers_admin)
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["numero_habitacion"] == "101"
    assert datos["estado"] == "Limpia"


def test_limpieza_no_puede_marcar_habitacion_como_ocupada_devuelve_403(client, headers_admin, headers_limpieza):
    # 1. Admin crea la habitación
    r_crear = client.post("/habitaciones/", json={
        "numero_habitacion": "102",
        "tipo": "Doble",
        "capacidad": 2,
        "precio_base": 900.0,
    }, headers=headers_admin)
    id_hab = r_crear.json()["id_habitacion"]

    # 2. Limpieza intenta ponerla Ocupada directamente
    r_patch = client.patch(
        f"/habitaciones/{id_hab}/estado",
        json={"estado": "Ocupada"},
        headers=headers_limpieza,
    )
    assert r_patch.status_code == 403
    assert "personal de limpieza no puede marcar habitaciones como 'Ocupada'" in r_patch.json()["detail"]
