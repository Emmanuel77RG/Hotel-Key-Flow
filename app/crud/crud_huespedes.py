from sqlalchemy.orm import Session
from app.models.huespedes import Huesped
from app.schemas.huespedes import HuespedCrear

def obtener_huespedes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Huesped).offset(skip).limit(limit).all()

def crear_huesped(db: Session, huesped: HuespedCrear):
    db_huesped = Huesped(**huesped.dict())
    db.add(db_huesped)
    db.commit()
    db.refresh(db_huesped)
    return db_huesped