from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.reservas_folios import ReservaCrear, ReservaRespuesta
from app.crud import crud_reservas_folios, crud_habitaciones

router = APIRouter()

@router.get("/", response_model=List[ReservaRespuesta], summary="Listar reservas y folios")
def listar_reservas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_reservas_folios.obtener_reservas(db, skip=skip, limit=limit)

@router.post("/", response_model=ReservaRespuesta, summary="Crear una reserva")
def crear_reserva(reserva: ReservaCrear, db: Session = Depends(get_db)):
    
    # Lógica de negocio (F1SP3)
    
    # Validación de coherencia cronológica
    if reserva.fecha_salida <= reserva.fecha_entrada:
        raise HTTPException(
            status_code=400, 
            detail="Error de lógica: La fecha de salida debe ser posterior a la fecha de entrada."
        )

    # Validación de disponibilidad de la habitación
    habitacion = crud_habitaciones.obtener_habitacion(db, habitacion_id=reserva.habitacion_id)
    if not habitacion:
        raise HTTPException(status_code=404, detail="La habitación solicitada no existe.")
    
    if habitacion.estado != "Disponible":
        raise HTTPException(
            status_code=400, 
            detail=f"La habitación {habitacion.numero} actualmente se encuentra {habitacion.estado}."
        )

    # OPERACIÓN CRUD
    nueva_reserva = crud_reservas_folios.crear_reserva(db=db, reserva=reserva)
    return nueva_reserva