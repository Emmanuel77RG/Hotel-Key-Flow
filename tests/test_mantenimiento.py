"""
Pruebas del Módulo de Mantenimiento y Bloqueo Operativo de Habitaciones (RF-MAN-001).
"""
import pytest


def test_crear_ticket_bloquea_habitacion_en_mantenimiento_y_resolver_libera(client, headers_admin):
    # 1. Crear habitación
    r_hab = client.post("/habitaciones/", json={
        "numero_habitacion": "401",
        "tipo": "Sencilla",
        "capacidad": 1,
        "precio_base": 700.0,
    }, headers=headers_admin)
    id_hab = r_hab.json()["id_habitacion"]

    # 2. Reportar ticket de mantenimiento
    payload_ticket = {
        "id_habitacion": id_hab,
        "categoria": "Fontanería",
        "prioridad": "Alta",
        "descripcion_falla": "Fuga de agua en el lavabo del baño principal",
    }
    r_tick = client.post("/mantenimiento/", json=payload_ticket, headers=headers_admin)
    assert r_tick.status_code == 201
    id_tick = r_tick.json()["id_ticket"]

    # 3. Verificar que la habitación quedó automáticamente bloqueada en "Mantenimiento"
    r_hab_check = client.get("/habitaciones/", headers=headers_admin)
    hab_actual = next(h for h in r_hab_check.json() if h["id_habitacion"] == id_hab)
    assert hab_actual["estado"] == "Mantenimiento"

    # 4. Resolver ticket
    r_resuelto = client.patch(
        f"/mantenimiento/{id_tick}/estado",
        json={"estado_ticket": "Resuelto", "nota_resolucion": "Se cambió el empaque de la tubería"},
        headers=headers_admin
    )
    assert r_resuelto.status_code == 200

    # 5. Verificar que la habitación quedó liberada en "Sucia" para posterior limpieza
    r_hab_liberada = client.get("/habitaciones/", headers=headers_admin)
    hab_lib = next(h for h in r_hab_liberada.json() if h["id_habitacion"] == id_hab)
    assert hab_lib["estado"] == "Sucia"
