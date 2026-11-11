import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class CargoBase(BaseModel):
    monto: float = Field(..., gt=0, description="Monto del cargo (debe ser mayor a $0.00)")
    descripcion: str = Field(..., min_length=1, max_length=255, description="Concepto del cargo")
    id_reserva: int = Field(..., gt=0)

class CargoCrear(CargoBase):
    pass

class CargoRespuesta(CargoBase):
    id_cargo: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class PagoBase(BaseModel):
    monto: float = Field(..., gt=0, description="Monto del pago (debe ser mayor a $0.00)")
    metodo_pago: str = Field(..., min_length=1, max_length=100, description="Método de pago utilizado")
    id_reserva: int = Field(..., gt=0)
    id_usuario: Optional[int] = None

class PagoCrear(PagoBase):
    pass

class PagoRespuesta(PagoBase):
    id_pago: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class FacturaSolicitar(BaseModel):
    id_reserva: int = Field(..., gt=0)
    rfc_cliente: str
    razon_social: Optional[str] = "PÚBLICO EN GENERAL"

    @field_validator("rfc_cliente")
    @classmethod
    def validar_formato_rfc(cls, v: str) -> str:
        # Criterio de Aceptación BDD RF-FAC-005 (Sección 10.2 y 19.2):
        # Rechazar caracteres especiales inválidos (ej. guiones "XAXX-010101-000") con HTTP 422
        rfc_limpio = v.strip().upper()
        patron_rfc = r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$"
        if not re.match(patron_rfc, rfc_limpio):
            raise ValueError(
                "Formato de RFC inválido. Debe contener 12 o 13 caracteres alfanuméricos sin guiones ni espacios (ej. XAXX010101000)."
            )
        return rfc_limpio
