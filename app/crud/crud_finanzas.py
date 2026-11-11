from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.finanzas import Cargo, Pago
from app.schemas.finanzas import CargoCrear, PagoCrear

def obtener_cargos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Cargo).order_by(Cargo.id_cargo.desc()).offset(skip).limit(limit).all()

def obtener_cargos_por_reserva(db: Session, id_reserva: int):
    return db.query(Cargo).filter(Cargo.id_reserva == id_reserva).order_by(Cargo.id_cargo).all()

def crear_cargo(db: Session, cargo: CargoCrear):
    try:
        db_cargo = Cargo(**cargo.model_dump())
        db.add(db_cargo)
        db.commit()
        db.refresh(db_cargo)
        return db_cargo
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en base de datos al registrar el cargo: {str(exc)}",
        )

def obtener_pagos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Pago).order_by(Pago.id_pago.desc()).offset(skip).limit(limit).all()

def obtener_pagos_por_reserva(db: Session, id_reserva: int):
    return db.query(Pago).filter(Pago.id_reserva == id_reserva).order_by(Pago.id_pago).all()

def crear_pago(db: Session, pago: PagoCrear):
    try:
        db_pago = Pago(**pago.model_dump())
        db.add(db_pago)
        db.commit()
        db.refresh(db_pago)
        return db_pago
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en base de datos al registrar el pago: {str(exc)}",
        )
