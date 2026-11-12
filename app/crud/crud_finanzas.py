from sqlalchemy.orm import Session
from app.models.finanzas import Cargo, Pago
from app.schemas.finanzas import CargoCrear, PagoCrear

def obtener_cargos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Cargo).order_by(Cargo.id_cargo.desc()).offset(skip).limit(limit).all()

def obtener_cargos_por_reserva(db: Session, id_reserva: int):
    return db.query(Cargo).filter(Cargo.id_reserva == id_reserva).order_by(Cargo.id_cargo).all()

def crear_cargo(db: Session, cargo: CargoCrear):
    db_cargo = Cargo(**cargo.model_dump())
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

def obtener_pagos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Pago).order_by(Pago.id_pago.desc()).offset(skip).limit(limit).all()

def obtener_pagos_por_reserva(db: Session, id_reserva: int):
    return db.query(Pago).filter(Pago.id_reserva == id_reserva).order_by(Pago.id_pago).all()

def crear_pago(db: Session, pago: PagoCrear):
    db_pago = Pago(**pago.model_dump())
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago