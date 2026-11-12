"""
Servicio API para el Punto de Venta (POS) y cargos a habitaciones.
"""
from .cliente_base import ClienteAPIBase


class PosAPI:
    def __init__(self, cliente: ClienteAPIBase):
        self.cliente = cliente

    def listar_productos(self, solo_activos: bool = True, categoria: str = None) -> list:
        params = {"solo_activos": solo_activos}
        if categoria and categoria != "Todas las categorías":
            params["categoria"] = categoria
        resp = self.cliente.get("/pos/productos", params=params)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def cargar_a_habitacion(self, id_habitacion: int, items: list, notas: str = None) -> dict:
        payload = {
            "id_habitacion": id_habitacion,
            "items": items,
            "notas": notas or "",
        }
        resp = self.cliente.post("/pos/cargar-habitacion", json=payload)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))
