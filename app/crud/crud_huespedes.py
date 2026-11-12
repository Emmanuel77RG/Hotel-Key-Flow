from sqlalchemy.orm import Session
from app.models.huespedes import Huesped
from app.schemas.huespedes import HuespedCrear, HuespedActualizar

def obtener_huespedes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Huesped).order_by(Huesped.id_huesped).offset(skip).limit(limit).all()

def obtener_huesped(db: Session, id_huesped: int):
    return db.query(Huesped).filter(Huesped.id_huesped == id_huesped).first()

def obtener_huesped_por_documento(db: Session, documento_identidad: str):
    return db.query(Huesped).filter(Huesped.documento_identidad == documento_identidad).first()

def crear_huesped(db: Session, huesped: HuespedCrear):
    db_huesped = Huesped(**huesped.model_dump())
    db.add(db_huesped)
    db.commit()
    db.refresh(db_huesped)
    return db_huesped

def actualizar_huesped(db: Session, id_huesped: int, datos: HuespedActualizar):
    db_huesped = obtener_huesped(db, id_huesped)
    if not db_huesped:
        return None
    if datos.documento_identidad is not None:
        db_huesped.documento_identidad = datos.documento_identidad
    if datos.nombre_completo is not None:
        db_huesped.nombre_completo = datos.nombre_completo
    if datos.email is not None:
        db_huesped.email = datos.email
    if datos.telefono is not None:
        db_huesped.telefono = datos.telefono
    if datos.rfc is not None:
        db_huesped.rfc = datos.rfc
    db.commit()
    db.refresh(db_huesped)
    return db_huesped

def eliminar_huesped(db: Session, id_huesped: int):
    db_huesped = obtener_huesped(db, id_huesped)
    if not db_huesped:
        return False
    db.delete(db_huesped)
    db.commit()
    return True