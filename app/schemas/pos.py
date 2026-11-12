from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class ProductoPOSBase(BaseModel):
    nombre: str
    categoria: str = "Restaurante / Alimentos"
    precio_unitario: float
    disponible: bool = True

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        limpio = v.strip()
        if not limpio:
            raise ValueError("El nombre del producto o servicio no puede estar vacío.")
        return limpio

    @field_validator("precio_unitario")
    @classmethod
    def validar_precio(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("El precio unitario debe ser mayor a $0.00.")
        return round(float(v), 2)


class ProductoPOSCrear(ProductoPOSBase):
    pass


class ProductoPOSActualizar(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    precio_unitario: Optional[float] = None
    disponible: Optional[bool] = None

    @field_validator("precio_unitario")
    @classmethod
    def validar_precio_opcional(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("El precio unitario debe ser mayor a $0.00.")
        return round(float(v), 2) if v is not None else None


class ProductoPOSRespuesta(ProductoPOSBase):
    id_producto: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ItemComandaPOS(BaseModel):
    id_producto: Optional[int] = None
    nombre: str
    cantidad: int
    precio_unitario: float

    @field_validator("cantidad")
    @classmethod
    def validar_cantidad(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La cantidad de cada producto debe ser al menos 1.")
        return v

    @field_validator("precio_unitario")
    @classmethod
    def validar_precio_item(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("El precio unitario del producto debe ser mayor a $0.00.")
        return round(float(v), 2)


class ComandaHabitacionCrear(BaseModel):
    id_reserva: int
    modalidad_servicio: Optional[str] = "Room Service"
    notas: Optional[str] = None
    items: List[ItemComandaPOS]

    @field_validator("items")
    @classmethod
    def validar_items(cls, v: List[ItemComandaPOS]) -> List[ItemComandaPOS]:
        if not v:
            raise ValueError("La comanda debe incluir al menos un producto o servicio.")
        return v
