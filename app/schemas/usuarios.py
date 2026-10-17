from pydantic import BaseModel, EmailStr

class UsuarioCrear(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    id_rol: int
