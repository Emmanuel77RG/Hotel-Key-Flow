from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.mantenimiento import TicketMantenimientoCrear, TicketMantenimientoRespuesta
from app.crud import crud_mantenimiento

router = APIRouter()

@router.get("/", response_model=List[TicketMantenimientoRespuesta], summary="Listar tickets de mantenimiento")
def listar_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_mantenimiento.obtener_tickets(db, skip=skip, limit=limit)

@router.post("/", response_model=TicketMantenimientoRespuesta, summary="Crear un ticket de mantenimiento")
def crear_ticket(ticket: TicketMantenimientoCrear, db: Session = Depends(get_db)):
    return crud_mantenimiento.crear_ticket(db=db, ticket=ticket)