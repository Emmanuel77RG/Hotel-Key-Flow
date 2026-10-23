from sqlalchemy.orm import Session
from app.models.finanzas import Cargo, Pago
from app.schemas.finanzas import CargoCrear, PagoCrear

def obtener_cargos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Cargo).offset(skip).limit(limit).all()

def crear_cargo(db: Session, cargo: CargoCrear):
    db_cargo = Cargo(**cargo.dict())
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    return db_cargo

def obtener_pagos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Pago).offset(skip).limit(limit).all()

def crear_pago(db: Session, pago: PagoCrear):
    db_pago = Pago(**pago.dict())
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago