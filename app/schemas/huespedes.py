import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

def _validar_rfc_opcional(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    limpio = v.strip().upper()
    if not limpio:
        return None
    patron_rfc = r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$"
    if not re.match(patron_rfc, limpio):
        raise ValueError(
            "Formato de RFC inválido. Debe contener 12 o 13 caracteres alfanuméricos sin guiones ni espacios (ej. XAXX010101000)."
        )
    return limpio

class HuespedBase(BaseModel):
    documento_identidad: str = Field(..., min_length=3, max_length=50, description="Identificación oficial única (INE/Pasaporte)")
    nombre_completo: str = Field(..., min_length=2, max_length=150, description="Nombre completo del huésped")
    email: Optional[str] = None
    telefono: Optional[str] = None
    rfc: Optional[str] = None

    @field_validator("rfc")
    @classmethod
    def check_rfc(cls, v: Optional[str]) -> Optional[str]:
        return _validar_rfc_opcional(v)

class HuespedCrear(HuespedBase):
    pass

class HuespedActualizar(BaseModel):
    documento_identidad: Optional[str] = Field(None, min_length=3, max_length=50)
    nombre_completo: Optional[str] = Field(None, min_length=2, max_length=150)
    email: Optional[str] = None
    telefono: Optional[str] = None
    rfc: Optional[str] = None

    @field_validator("rfc")
    @classmethod
    def check_rfc(cls, v: Optional[str]) -> Optional[str]:
        return _validar_rfc_opcional(v)

class HuespedRespuesta(HuespedBase):
    id_huesped: int
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True
