from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ReservaFolioBase(BaseModel):
    fecha_entrada: date
    fecha_salida: date
    estado_reserva: str
    estado_folio: str
    id_usuario: Optional[int] = None
    id_huesped: int

class ReservaCrear(ReservaFolioBase):
    id_habitacion: int

class ReservaRespuesta(ReservaFolioBase):
    id_reserva: int
    nombre_huesped: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True