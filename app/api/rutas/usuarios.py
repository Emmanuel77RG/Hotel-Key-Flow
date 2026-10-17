from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import usuarios as schemas
from app.crud import crud_usuarios
from app.api.dependencias import get_db

# Usamos APIRouter para agrupar las rutas de este módulo
router = APIRouter()

@router.post("/")
def crear_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    # 1. Verificamos si el email ya existe usando nuestro CRUD
    db_user = crud_usuarios.obtener_usuario_por_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # 2. Creamos el usuario delegando la lógica al CRUD
    nuevo_usuario = crud_usuarios.crear_usuario(db=db, usuario=usuario)
    
    return {"mensaje": "Usuario creado exitosamente", "id_usuario": nuevo_usuario.id_usuario}