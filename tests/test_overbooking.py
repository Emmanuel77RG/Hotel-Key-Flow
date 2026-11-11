"""
Pruebas del Motor de Reservas y Prevención de Overbooking (RF-RES-003).
"""
import pytest
from datetime import date, timedelta


def _crear_huesped_y_habitacion(client, headers_admin):
    # Crear habitación
    r_hab = client.post("/habitaciones/", json={
        "numero_habitacion": "201",
        "tipo": "Sencilla",
        "capacidad": 1,
        "precio_base": 800.0,
    }, headers=headers_admin)
    id_hab = r_hab.json()["id_habitacion"]

    # Crear huésped
    r_huesped = client.post("/huespedes/", json={
        "documento_identidad": "INE-TEST-2026-01",
        "nombre_completo": "Juan Pérez López",
        "email": "juan@test.com",
    }, headers=headers_admin)
    id_huesped = r_huesped.json()["id_huesped"]

    return id_hab, id_huesped


def test_rechazo_de_reserva_con_fechas_pasadas_devuelve_400(client, headers_recepcion, headers_admin):
    id_hab, id_huesped = _crear_huesped_y_habitacion(client, headers_admin)

    ayer = date.today() - timedelta(days=1)
    manana = date.today() + timedelta(days=1)

    payload = {
        "fecha_entrada": str(ayer),
        "fecha_salida": str(manana),
        "estado_reserva": "Confirmada",
        "estado_folio": "Abierto",
        "id_huesped": id_huesped,
        "id_habitacion": id_hab,
    }
    r = client.post("/reservas/", json=payload, headers=headers_recepcion)
    assert r.status_code == 400
    assert "fechas de entrada en el pasado" in r.json()["detail"]


def test_prevencion_overbooking_cruce_de_fechas_devuelve_409(client, headers_recepcion, headers_admin):
    id_hab, id_huesped = _crear_huesped_y_habitacion(client, headers_admin)

    # 1. Primera reserva válida del día +20 al día +25
    f_entrada_1 = date.today() + timedelta(days=20)
    f_salida_1 = date.today() + timedelta(days=25)

    r1 = client.post("/reservas/", json={
        "fecha_entrada": str(f_entrada_1),
        "fecha_salida": str(f_salida_1),
        "estado_reserva": "Confirmada",
        "estado_folio": "Abierto",
        "id_huesped": id_huesped,
        "id_habitacion": id_hab,
    }, headers=headers_recepcion)
    assert r1.status_code == 201

    # 2. Segunda reserva que se traslapa (del día +22 al +24) para la misma habitación
    f_entrada_2 = date.today() + timedelta(days=22)
    f_salida_2 = date.today() + timedelta(days=24)

    r2 = client.post("/reservas/", json={
        "fecha_entrada": str(f_entrada_2),
        "fecha_salida": str(f_salida_2),
        "estado_reserva": "Confirmada",
        "estado_folio": "Abierto",
        "id_huesped": id_huesped,
        "id_habitacion": id_hab,
    }, headers=headers_recepcion)

    # Debe ser rechazada con 409 Conflict por sobreventa
    assert r2.status_code == 409
    assert "Inventario no disponible para las fechas seleccionadas" in r2.json()["detail"]
