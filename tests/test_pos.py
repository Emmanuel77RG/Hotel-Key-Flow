"""
Pruebas del Punto de Venta (POS) y Comandas a Habitación (Sprint 6-7).
"""
import pytest
from datetime import date, timedelta


def test_catalogo_pos_y_comanda_a_habitacion(client, headers_admin, headers_recepcion):
    # 1. Crear producto en el catálogo POS
    p_data = {
        "nombre": "Club Sandwich con Papas",
        "categoria": "Restaurante / Alimentos",
        "precio_unitario": 180.0,
        "disponible": True,
    }
    r_prod = client.post("/pos/productos", json=p_data, headers=headers_admin)
    assert r_prod.status_code == 201
    id_prod = r_prod.json()["id_producto"]

    # 2. Listar productos disponibles
    r_list = client.get("/pos/productos?solo_disponibles=true", headers=headers_recepcion)
    assert r_list.status_code == 200
    assert any(p["id_producto"] == id_prod for p in r_list.json())

    # 3. Crear habitación, huésped y reserva con check-in activo
    r_hab = client.post("/habitaciones/", json={
        "numero_habitacion": "601", "tipo": "Suite", "capacidad": 2, "precio_base": 1200.0
    }, headers=headers_admin)
    id_hab = r_hab.json()["id_habitacion"]

    r_hue = client.post("/huespedes/", json={
        "documento_identidad": "INE-POS-TEST-01", "nombre_completo": "Cliente POS Test"
    }, headers=headers_admin)
    id_hue = r_hue.json()["id_huesped"]

    f_in = date.today() + timedelta(days=1)
    f_out = date.today() + timedelta(days=3)
    r_res = client.post("/reservas/", json={
        "fecha_entrada": str(f_in), "fecha_salida": str(f_out),
        "estado_reserva": "Confirmada", "estado_folio": "Abierto",
        "id_huesped": id_hue, "id_habitacion": id_hab,
    }, headers=headers_recepcion)
    id_res = r_res.json()["id_reserva"]

    # Check-in
    client.post(f"/reservas/{id_res}/checkin", headers=headers_recepcion)

    # 4. Cargar comanda de room service a la habitación
    comanda = {
        "id_reserva": id_res,
        "modalidad_servicio": "Room Service",
        "items": [
            {
                "id_producto": id_prod,
                "nombre": "Club Sandwich con Papas",
                "cantidad": 2,
                "precio_unitario": 180.0,
            }
        ]
    }
    r_comanda = client.post("/pos/cargar-habitacion", json=comanda, headers=headers_recepcion)
    assert r_comanda.status_code == 201
    assert float(r_comanda.json()["monto"]) == 360.0  # 2 * 180.0

    # 5. Verificar que el cargo se agregó al saldo de la cuenta folio
    saldo_folio = client.get(f"/reservas/{id_res}", headers=headers_recepcion).json()
    assert any("Club Sandwich" in c["descripcion"] for c in saldo_folio["cargos"])
