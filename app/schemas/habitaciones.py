from typing import Optional
from pydantic import BaseModel, Field
from app.models.habitaciones import EstadoHabitacion

class HabitacionBase(BaseModel):
    numero_habitacion: str = Field(..., min_length=1, max_length=10, description="Número identificador de habitación")
    tipo: str = Field(..., min_length=1, max_length=50, description="Tipo de habitación (Sencilla, Doble, Suite, etc.)")
    capacidad: int = Field(..., gt=0, description="Capacidad máxima de personas (debe ser mayor a 0)")
    precio_base: float = Field(..., gt=0, description="Tarifa base por noche (debe ser mayor a 0)")

class HabitacionCrear(HabitacionBase):
    pass

class HabitacionActualizar(BaseModel):
    numero_habitacion: Optional[str] = Field(None, min_length=1, max_length=10)
    tipo: Optional[str] = Field(None, min_length=1, max_length=50)
    capacidad: Optional[int] = Field(None, gt=0)
    precio_base: Optional[float] = Field(None, gt=0)
    estado: Optional[EstadoHabitacion] = None

class HabitacionEstadoUpdate(BaseModel):
    estado: EstadoHabitacion

class HabitacionRespuesta(HabitacionBase):
    id_habitacion: int
    estado: EstadoHabitacion

    class Config:
        from_attributes = True
