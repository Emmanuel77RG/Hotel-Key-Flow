from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketMantenimientoBase(BaseModel):
    id_habitacion: int
    descripcion_falla: str
    estado_ticket: Optional[str] = "Pendiente"
    id_usuario_reporta: Optional[int] = None

class TicketMantenimientoCrear(TicketMantenimientoBase):
    pass

class TicketMantenimientoEstadoActualizar(BaseModel):
    estado_ticket: str

class TicketMantenimientoRespuesta(TicketMantenimientoBase):
    id_ticket: int
    numero_habitacion: Optional[str] = None
    nombre_usuario_reporta: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_resolucion: Optional[datetime] = None

    class Config:
        from_attributes = True