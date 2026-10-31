from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text  # <-- 1. Agrega esta importación
from app.schemas import usuarios as schemas
from app.crud import crud_usuarios
from app.api.dependencias import get_db

router = APIRouter()

@router.post("/")
def crear_usuario(usuario: schemas.UsuarioCrear, db: Session = Depends(get_db)):
    db_user = crud_usuarios.obtener_usuario_por_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    nuevo_usuario = crud_usuarios.crear_usuario(db=db, usuario=usuario)
    return {"mensaje": "Usuario creado exitosamente", "id_usuario": nuevo_usuario.id_usuario}

@router.post("/setup-roles")
def inicializar_roles(db: Session = Depends(get_db)):
    # Ajusta "nombre" por el nombre real de tu columna en la tabla roles si es distinto
    db.execute(text("INSERT INTO roles (id_rol, nombre_rol) VALUES (1, 'Administrador');"))
    db.commit()
    return {"msg": "Rol creado de forma segura"}