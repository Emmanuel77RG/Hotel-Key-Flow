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


def test_enmascaramiento_token_para_recepcionista_y_admin_completo(client, headers_admin, headers_recepcion):
    from app.core.security import enmascarar_token_pago

    # 1. Prueba unitaria de enmascaramiento RNF-SEG-003
    assert enmascarar_token_pago("Tarjeta Chip ****7390 (Tok: 8A7B2C1D)") == "Tarjeta Chip ****7390 (Tok: ****2C1D)"
    assert enmascarar_token_pago("Tarjeta NFC ****4821 (Tok: 9B8C7D6E)") == "Tarjeta NFC ****4821 (Tok: ****7D6E)"
    assert enmascarar_token_pago("Efectivo") == "Efectivo"

    from datetime import date, timedelta

    # 2. Flujo completo: Crear huésped, habitación, reserva y pago
    r_h = client.post("/huespedes/", json={
        "documento_identidad": "INE12345678",
        "nombre_completo": "Carlos Gómez",
        "email": "carlos@test.com",
        "telefono": "5551234567"
    }, headers=headers_admin)
    id_huesped = r_h.json()["id_huesped"]

    r_hab = client.post("/habitaciones/", json={"numero_habitacion": "501", "tipo": "Suite", "capacidad": 2, "precio_base": 1200.0}, headers=headers_admin)
    id_hab = r_hab.json()["id_habitacion"]

    f_in = date.today() + timedelta(days=1)
    f_out = date.today() + timedelta(days=3)
    r_res = client.post("/reservas/", json={
        "fecha_entrada": str(f_in),
        "fecha_salida": str(f_out),
        "estado_reserva": "Confirmada",
        "estado_folio": "Abierto",
        "id_huesped": id_huesped,
        "id_habitacion": id_hab,
    }, headers=headers_recepcion)
    id_res = r_res.json()["id_reserva"]

    # Check-in para abrir el folio
    client.post(f"/reservas/{id_res}/checkin", headers=headers_admin)

    # Registrar pago con token completo
    token_original = "Tarjeta Chip ****7390 (Tok: ABCDEF12)"
    pago_resp_recep = client.post("/finanzas/pagos", json={
        "id_reserva": id_res,
        "monto": 500.0,
        "metodo_pago": token_original,
    }, headers=headers_recepcion)

    assert pago_resp_recep.status_code == 200
    # Recepcionista ve token enmascarado
    assert "ABCDEF12" not in pago_resp_recep.json()["metodo_pago"]
    assert "(Tok: ****EF12)" in pago_resp_recep.json()["metodo_pago"]

    # Consulta de saldo de la reserva: Recepcionista ve token enmascarado
    saldo_recep = client.get(f"/reservas/{id_res}", headers=headers_recepcion).json()
    assert any("(Tok: ****EF12)" in p["metodo_pago"] for p in saldo_recep["pagos"])
    assert not any("ABCDEF12" in p["metodo_pago"] for p in saldo_recep["pagos"])

    # Consulta de saldo de la reserva: Administrador ve el token completo
    saldo_admin = client.get(f"/reservas/{id_res}", headers=headers_admin).json()
    assert any("ABCDEF12" in p["metodo_pago"] for p in saldo_admin["pagos"])

    # Reporte de corte/auditoría: Recepcionista ve enmascarado, Admin ve completo
    rep_recep = client.get("/reportes/resumen", headers=headers_recepcion).json()
    assert all("ABCDEF12" not in p["metodo_pago"] for p in rep_recep["pagos_detalle"])

    rep_admin = client.get("/reportes/resumen", headers=headers_admin).json()
    assert any("ABCDEF12" in p["metodo_pago"] for p in rep_admin["pagos_detalle"])

