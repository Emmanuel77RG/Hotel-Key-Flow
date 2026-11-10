"""
Servicio API para la gestión de tickets de mantenimiento y averías.
"""
from .cliente_base import ClienteAPIBase


class MantenimientoAPI:
    def __init__(self, cliente: ClienteAPIBase):
        self.cliente = cliente

    def listar_tickets(self, estado: str = None, id_habitacion: int = None) -> list:
        params = {}
        if estado:
            params["estado"] = estado
        if id_habitacion:
            params["id_habitacion"] = id_habitacion
        resp = self.cliente.get("/mantenimiento/tickets", params=params)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def crear_ticket(self, datos: dict) -> dict:
        resp = self.cliente.post("/mantenimiento/tickets", json=datos)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def actualizar_estado(
        self,
        id_ticket: int,
        nuevo_estado: str,
        notas_resolucion: str = None,
        costo_reparacion: float = None,
    ) -> dict:
        payload = {"nuevo_estado": nuevo_estado}
        if notas_resolucion is not None:
            payload["notas_resolucion"] = notas_resolucion
        if costo_reparacion is not None:
            payload["costo_reparacion"] = float(costo_reparacion)
        resp = self.cliente.put(f"/mantenimiento/tickets/{id_ticket}/estado", json=payload)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))
