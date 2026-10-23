from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.finanzas import CargoCrear, CargoRespuesta, PagoCrear, PagoRespuesta
from app.crud import crud_finanzas

router = APIRouter()

# --- Endpoints de Cargos ---
@router.get("/cargos", response_model=List[CargoRespuesta], summary="Listar cargos")
def listar_cargos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_finanzas.obtener_cargos(db, skip=skip, limit=limit)

@router.post("/cargos", response_model=CargoRespuesta, summary="Crear un cargo a la reserva")
def crear_cargo(cargo: CargoCrear, db: Session = Depends(get_db)):
    return crud_finanzas.crear_cargo(db=db, cargo=cargo)

# --- Endpoints de Pagos ---
@router.get("/pagos", response_model=List[PagoRespuesta], summary="Listar pagos")
def listar_pagos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_finanzas.obtener_pagos(db, skip=skip, limit=limit)

@router.post("/pagos", response_model=PagoRespuesta, summary="Registrar un pago")
def crear_pago(pago: PagoCrear, db: Session = Depends(get_db)):
    return crud_finanzas.crear_pago(db=db, pago=pago)