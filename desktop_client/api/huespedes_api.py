"""
Servicio API para huéspedes, folios de cuenta, pagos y facturación.
"""
from .cliente_base import ClienteAPIBase


class HuespedesAPI:
    def __init__(self, cliente: ClienteAPIBase):
        self.cliente = cliente

    def listar(self, q: str = None) -> list:
        params = {"q": q} if q else None
        resp = self.cliente.get("/huespedes/", params=params)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def crear(self, datos: dict) -> dict:
        resp = self.cliente.post("/huespedes/", json=datos)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def obtener_folio(self, id_reserva: int) -> dict:
        resp = self.cliente.get(f"/finanzas/folio/{id_reserva}")
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def registrar_pago(self, id_reserva: int, metodo_pago: str, monto: float) -> dict:
        payload = {
            "id_reserva": id_reserva,
            "metodo_pago": metodo_pago,
            "monto": float(monto),
        }
        resp = self.cliente.post("/finanzas/pagos", json=payload)
        if resp.status_code in (200, 201):
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def facturar(self, id_reserva: int, rfc_cliente: str, razon_social: str) -> dict:
        payload = {
            "id_reserva": id_reserva,
            "rfc_cliente": rfc_cliente,
            "razon_social": razon_social,
        }
        resp = self.cliente.post("/finanzas/facturar", json=payload)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))

    def check_out(self, id_reserva: int) -> dict:
        resp = self.cliente.put(f"/reservas/{id_reserva}/check-out")
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))
