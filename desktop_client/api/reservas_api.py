"""
Servicio API para la gestión de reservaciones y check-in.
"""
from .cliente_base import ClienteAPIBase


class ReservasAPI:
    def __init__(self, cliente: ClienteAPIBase):
        self.cliente = cliente

    def listar_todas(self) -> list:
        resp = self.cliente.get("/reservas/")
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def crear(self, datos: dict) -> dict:
        resp = self.cliente.post("/reservas/", json=datos)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def cancelar(self, id_reserva: int) -> dict:
        resp = self.cliente.put(f"/reservas/{id_reserva}/cancelar")
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def check_in(self, id_reserva: int, habitaciones_asignadas: list = None) -> dict:
        payload = {}
        if habitaciones_asignadas:
            payload["habitaciones_asignadas"] = habitaciones_asignadas
        resp = self.cliente.put(f"/reservas/{id_reserva}/check-in", json=payload)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))
