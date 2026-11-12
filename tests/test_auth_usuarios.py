"""
Pruebas de Autenticación (/login) y Gestión de Usuarios (/usuarios).
"""
import pytest


def test_login_exitoso_y_obtencion_token(client, usuarios_prueba):
    form_data = {
        "username": "admin@hotelkeyflow.com",
        "password": "Password123*",
    }
    r = client.post("/login", data=form_data)
    assert r.status_code == 200
    datos = r.json()
    assert "access_token" in datos
    assert datos["id_rol"] == 1


def test_login_credenciales_invalidas(client, usuarios_prueba):
    form_data = {
        "username": "admin@hotelkeyflow.com",
        "password": "PasswordEquivocada",
    }
    r = client.post("/login", data=form_data)
    assert r.status_code == 401
    assert "incorrectos" in r.json()["detail"]


def test_login_usuario_inexistente(client):
    form_data = {
        "username": "inexistente@keyflow.com",
        "password": "CualquierPassword",
    }
    r = client.post("/login", data=form_data)
    assert r.status_code == 401


def test_crud_usuarios_y_borrado_logico(client, headers_admin):
    # 1. Crear nuevo usuario
    payload = {
        "nombre": "Recepcionista Nocturno",
        "email": "recep_noche@keyflow.com",
        "password": "PasswordSegura2026*",
        "id_rol": 2,
    }
    r_crear = client.post("/usuarios/", json=payload, headers=headers_admin)
    assert r_crear.status_code == 200
    id_usr = r_crear.json()["id_usuario"]

    # 2. Listar usuarios
    r_list = client.get("/usuarios/", headers=headers_admin)
    assert r_list.status_code == 200
    assert any(u["id_usuario"] == id_usr for u in r_list.json())

    # 3. Borrado lógico (Desactivar cuenta)
    r_patch = client.patch(f"/usuarios/{id_usr}/estado", json={"estado_activo": False}, headers=headers_admin)
    assert r_patch.status_code == 200
    assert r_patch.json()["estado_activo"] is False

    # 4. Intentar login con cuenta desactivada
    r_login = client.post("/login", data={"username": "recep_noche@keyflow.com", "password": "PasswordSegura2026*"})
    assert r_login.status_code == 403
    assert "desactivada" in r_login.json()["detail"]

    # 5. Reactivar cuenta
    r_reactivar = client.patch(f"/usuarios/{id_usr}/estado", json={"estado_activo": True}, headers=headers_admin)
    assert r_reactivar.status_code == 200
    assert r_reactivar.json()["estado_activo"] is True
