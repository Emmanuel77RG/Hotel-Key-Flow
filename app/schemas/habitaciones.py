from typing import Optional
from pydantic import BaseModel
from app.models.habitaciones import EstadoHabitacion

class HabitacionBase(BaseModel):
    numero_habitacion: str
    tipo: str
    capacidad: int
    precio_base: float

class HabitacionCrear(HabitacionBase):
    pass

class HabitacionActualizar(BaseModel):
    numero_habitacion: Optional[str] = None
    tipo: Optional[str] = None
    capacidad: Optional[int] = None
    precio_base: Optional[float] = None
    estado: Optional[EstadoHabitacion] = None

class HabitacionEstadoUpdate(BaseModel):
    estado: EstadoHabitacion

class HabitacionRespuesta(HabitacionBase):
    id_habitacion: int
    estado: EstadoHabitacion

    class Config:
        from_attributes = True