from pydantic import BaseModel
from app.models.habitaciones import EstadoHabitacion

class HabitacionBase(BaseModel):
    numero_habitacion: str
    tipo: str
    capacidad: int
    precio_base: float

class HabitacionCrear(HabitacionBase):
    pass

class HabitacionEstadoUpdate(BaseModel):
    estado: EstadoHabitacion

class HabitacionRespuesta(HabitacionBase):
    id_habitacion: int
    estado: EstadoHabitacion

    class Config:
        from_attributes = True