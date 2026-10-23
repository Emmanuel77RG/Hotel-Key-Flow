from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.huespedes import HuespedCrear, HuespedRespuesta
from app.crud import crud_huespedes

router = APIRouter()

@router.get("/", response_model=List[HuespedRespuesta], summary="Listar huéspedes")
def listar_huespedes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_huespedes.obtener_huespedes(db, skip=skip, limit=limit)

@router.post("/", response_model=HuespedRespuesta, summary="Registrar un nuevo huésped")
def crear_huesped(huesped: HuespedCrear, db: Session = Depends(get_db)):
    return crud_huespedes.crear_huesped(db=db, huesped=huesped)