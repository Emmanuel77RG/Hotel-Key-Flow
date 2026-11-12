"""
Pruebas de Check-in transaccional (RF-RES-004) y Check-out con saldo cero (RF-RES-005).
"""
import pytest
from datetime import date, timedelta


def _preparar_reserva_activa(client, headers_admin, headers_recepcion):
    # Habitación
    r_hab = client.post("/habitaciones/", json={
        "numero_habitacion": "301",
        "tipo": "Junior Suite",
        "capacidad": 2,
        "precio_base": 1000.0,
    }, headers=headers_admin)
    id_hab = r_hab.json()["id_habitacion"]

    # Huésped
    r_huesped = client.post("/huespedes/", json={
        "documento_identidad": "PASAPORTE-TEST-99",
        "nombre_completo": "Ana Martínez Ruiz",
    }, headers=headers_admin)
    id_huesped = r_huesped.json()["id_huesped"]

    # Reserva de 2 noches
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

    return id_hab, id_res


def test_checkin_transaccional_abre_folio_cambia_a_ocupada_y_genera_cargo(client, headers_admin, headers_recepcion):
    id_hab, id_res = _preparar_reserva_activa(client, headers_admin, headers_recepcion)

    # Realizar Check-in
    r_checkin = client.post(f"/reservas/{id_res}/checkin", headers=headers_recepcion)
    assert r_checkin.status_code == 200
    datos = r_checkin.json()
    assert datos["nuevo_estado_reserva"] == "Activa"
    assert datos["nuevo_estado_folio"] == "Abierto"
    assert datos["cargo_hospedaje_generado"] == 2000.0  # 2 noches * 1000.0

    # Verificar que la habitación quedó en "Ocupada"
    r_habs = client.get("/habitaciones/", headers=headers_recepcion)
    hab_actual = next(h for h in r_habs.json() if h["id_habitacion"] == id_hab)
    assert hab_actual["estado"] == "Ocupada"


def test_checkout_falla_si_hay_saldo_pendiente(client, headers_admin, headers_recepcion):
    id_hab, id_res = _preparar_reserva_activa(client, headers_admin, headers_recepcion)
    client.post(f"/reservas/{id_res}/checkin", headers=headers_recepcion)

    # Intentar checkout sin pagar (saldo pendiente = $2000)
    r_checkout = client.post(f"/reservas/{id_res}/checkout", headers=headers_recepcion)
    assert r_checkout.status_code == 400
    assert "saldo pendiente" in r_checkout.json()["detail"]


def test_checkout_exitoso_con_saldo_cero_pasa_habitacion_a_sucia(client, headers_admin, headers_recepcion):
    id_hab, id_res = _preparar_reserva_activa(client, headers_admin, headers_recepcion)
    client.post(f"/reservas/{id_res}/checkin", headers=headers_recepcion)

    # Registrar el pago por el total adeudado ($2000)
    r_pago = client.post("/finanzas/pagos", json={
        "id_reserva": id_res,
        "monto": 2000.0,
        "metodo_pago": "Efectivo",
    }, headers=headers_recepcion)
    assert r_pago.status_code == 200

    # Ahora el Check-out debe ser exitoso
    r_checkout = client.post(f"/reservas/{id_res}/checkout", headers=headers_recepcion)
    assert r_checkout.status_code == 200
    assert r_checkout.json()["nuevo_estado_reserva"] == "Finalizada"
    assert r_checkout.json()["nuevo_estado_folio"] == "Cerrado"

    # Verificar que la habitación quedó liberada en estado "Sucia" para camarería
    r_habs = client.get("/habitaciones/", headers=headers_recepcion)
    hab_actual = next(h for h in r_habs.json() if h["id_habitacion"] == id_hab)
    assert hab_actual["estado"] == "Sucia"
