from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class ReservaFolioBase(BaseModel):
    fecha_entrada: date
    fecha_salida: date
    estado_reserva: str
    estado_folio: str
    id_usuario: int
    id_huesped: int

class ReservaCrear(ReservaFolioBase):
    pass

class ReservaRespuesta(ReservaFolioBase):
    id_reserva: int
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True