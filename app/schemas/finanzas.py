from pydantic import BaseModel
from datetime import datetime

class CargoBase(BaseModel):
    monto: float
    descripcion: str
    id_reserva: int

class CargoCrear(CargoBase):
    pass

class CargoRespuesta(CargoBase):
    id_cargo: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class PagoBase(BaseModel):
    monto: float
    metodo_pago: str
    id_reserva: int
    id_usuario: int

class PagoCrear(PagoBase):
    pass

class PagoRespuesta(PagoBase):
    id_pago: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True