from sqlalchemy.orm import Session
from app.models.reservas_folios import ReservaFolio
from app.schemas.reservas_folios import ReservaCrear

def obtener_reservas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ReservaFolio).offset(skip).limit(limit).all()

def obtener_reserva_por_id(db: Session, id_reserva: int):
    return db.query(ReservaFolio).filter(ReservaFolio.id_reserva == id_reserva).first()

def crear_reserva(db: Session, reserva: ReservaCrear):
    db_reserva = ReservaFolio(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva