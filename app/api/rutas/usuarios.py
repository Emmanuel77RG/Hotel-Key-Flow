from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text  # <-- 1. Agrega esta importación
from app.schemas import usuarios as schemas
from app.crud import crud_usuarios
from app.api.dependencias import get_db, exigir_rol_admin

router = APIRouter()

@router.get("/", response_model=List[schemas.UsuarioRespuesta])
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_actual = Depends(exigir_rol_admin)
):
    return crud_usuarios.obtener_usuarios(db, skip=skip, limit=limit)

@router.post("/")
def crear_usuario(
    usuario: schemas.UsuarioCrear,
    db: Session = Depends(get_db),
    admin_actual = Depends(exigir_rol_admin)
):
    db_user = crud_usuarios.obtener_usuario_por_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    nuevo_usuario = crud_usuarios.crear_usuario(db=db, usuario=usuario)
    return {"mensaje": "Usuario creado exitosamente", "id_usuario": nuevo_usuario.id_usuario}

@router.put("/{id_usuario}", response_model=schemas.UsuarioRespuesta)
def modificar_usuario(
    id_usuario: int,
    datos: schemas.UsuarioActualizar,
    db: Session = Depends(get_db),
    admin_actual = Depends(exigir_rol_admin)
):
    usuario_existente = crud_usuarios.obtener_usuario_por_id(db, id_usuario)
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if datos.email and datos.email != usuario_existente.email:
        email_ocupado = crud_usuarios.obtener_usuario_por_email(db, email=datos.email)
        if email_ocupado:
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario")

    return crud_usuarios.actualizar_usuario(db, id_usuario=id_usuario, datos=datos)

@router.patch("/{id_usuario}/estado", response_model=schemas.UsuarioRespuesta)
def cambiar_estado_usuario(
    id_usuario: int,
    estado_update: schemas.UsuarioEstadoUpdate,
    db: Session = Depends(get_db),
    admin_actual = Depends(exigir_rol_admin)
):
    if id_usuario == admin_actual.id_usuario and not estado_update.estado_activo:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta de Administrador")

    usuario_actualizado = crud_usuarios.cambiar_estado_usuario(
        db, id_usuario=id_usuario, estado_activo=estado_update.estado_activo
    )
    if not usuario_actualizado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario_actualizado

@router.post("/setup-roles")
def inicializar_roles(db: Session = Depends(get_db)):
    # Ajusta "nombre" por el nombre real de tu columna en la tabla roles si es distinto
    db.execute(text("INSERT INTO roles (id_rol, nombre_rol) VALUES (1, 'Administrador');"))
    db.commit()
    return {"msg": "Rol creado de forma segura"}