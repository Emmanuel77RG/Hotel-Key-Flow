"""
Servicio API para la obtención de métricas, reportes y corte de caja.
"""
from .cliente_base import ClienteAPIBase


class ReportesAPI:
    def __init__(self, cliente: ClienteAPIBase):
        self.cliente = cliente

    def obtener_resumen(self, fecha: str = None) -> dict:
        params = {"fecha": fecha} if fecha else None
        resp = self.cliente.get("/reportes/resumen", params=params)
        if resp.status_code == 200:
            return resp.json()
        raise RuntimeError(self.cliente.extraer_detalle(resp))
