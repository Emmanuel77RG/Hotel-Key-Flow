from sqlalchemy.orm import Session
from app.models import usuarios as models
from app.schemas import usuarios as schemas
from app.core import security

def obtener_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def obtener_usuario_por_id(db: Session, id_usuario: int):
    return db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()

def obtener_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).order_by(models.Usuario.id_usuario).offset(skip).limit(limit).all()

def crear_usuario(db: Session, usuario: schemas.UsuarioCrear):
    hashed_pw = security.get_password_hash(usuario.password)
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=hashed_pw,
        id_rol=usuario.id_rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

def actualizar_usuario(db: Session, id_usuario: int, datos: schemas.UsuarioActualizar):
    usuario_db = obtener_usuario_por_id(db, id_usuario)
    if not usuario_db:
        return None
    if datos.nombre is not None:
        usuario_db.nombre = datos.nombre
    if datos.email is not None:
        usuario_db.email = datos.email
    if datos.id_rol is not None:
        usuario_db.id_rol = datos.id_rol
    if datos.password:
        usuario_db.password_hash = security.get_password_hash(datos.password)
    db.commit()
    db.refresh(usuario_db)
    return usuario_db

def cambiar_estado_usuario(db: Session, id_usuario: int, estado_activo: bool):
    usuario_db = obtener_usuario_por_id(db, id_usuario)
    if not usuario_db:
        return None
    usuario_db.estado_activo = estado_activo
    db.commit()
    db.refresh(usuario_db)
    return usuario_db