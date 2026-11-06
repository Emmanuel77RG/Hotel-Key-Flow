from pydantic import BaseModel
from typing import Optional

class HuespedBase(BaseModel):
    documento_identidad: str
    nombre_completo: str
    email: Optional[str] = None
    telefono: Optional[str] = None

class HuespedCrear(HuespedBase):
    pass

class HuespedActualizar(BaseModel):
    documento_identidad: Optional[str] = None
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

class HuespedRespuesta(HuespedBase):
    id_huesped: int

    class Config:
        from_attributes = True