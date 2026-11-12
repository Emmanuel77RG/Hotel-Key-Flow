from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    id_rol: int

class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    id_rol: Optional[int] = None

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

