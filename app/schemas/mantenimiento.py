from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketMantenimientoBase(BaseModel):
    id_habitacion: int
    id_usuario: int
    descripcion_problema: str
    estado: str

class TicketMantenimientoCrear(TicketMantenimientoBase):
    pass

class TicketMantenimientoRespuesta(TicketMantenimientoBase):
    id_ticket: int
    fecha_reporte: Optional[datetime] = None

    class Config:
        from_attributes = True