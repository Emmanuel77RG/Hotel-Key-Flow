from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UsuarioCrear(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Contraseña de acceso (mínimo 6 caracteres)")
    id_rol: int = Field(..., gt=0, description="Identificador del rol asignado")

class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, description="Nueva contraseña (mínimo 6 caracteres)")
    id_rol: Optional[int] = Field(None, gt=0)

class UsuarioEstadoUpdate(BaseModel):
    estado_activo: bool

class UsuarioRespuesta(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr
    id_rol: Optional[int] = None
    estado_activo: bool
    fecha_creacion: Optional[datetime] = None

    class Config:
        from_attributes = True
