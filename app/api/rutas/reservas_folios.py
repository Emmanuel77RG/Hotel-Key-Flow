from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.reservas_folios import ReservaCrear, ReservaRespuesta
from app.crud import crud_reservas_folios

router = APIRouter()

@router.get("/", response_model=List[ReservaRespuesta], summary="Listar reservas y folios")
def listar_reservas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_reservas_folios.obtener_reservas(db, skip=skip, limit=limit)

@router.post("/", response_model=ReservaRespuesta, summary="Crear una reserva")
def crear_reserva(reserva: ReservaCrear, db: Session = Depends(get_db)):
    return crud_reservas_folios.crear_reserva(db=db, reserva=reserva)