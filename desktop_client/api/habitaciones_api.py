"""
Servicio API para la gestión de habitaciones y estados de limpieza.
"""
import requests
from .cliente_base import ClienteAPIBase


class HabitacionesAPI:
    def __init__(self, cliente: ClienteAPIBase):
        self.cliente = cliente

    def listar_todas(self) -> list:
        resp = self.cliente.get("/habitaciones/")
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def cambiar_estado(self, id_habitacion: int, nuevo_estado: str) -> dict:
        resp = self.cliente.put(f"/habitaciones/{id_habitacion}/estado", json={"nuevo_estado": nuevo_estado})
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))
