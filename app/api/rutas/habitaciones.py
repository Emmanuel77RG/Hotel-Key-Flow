from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas import habitaciones as schemas
from app.crud import crud_habitaciones
from app.api.dependencias import get_db, get_usuario_actual

router = APIRouter()

@router.post("/", response_model=schemas.HabitacionRespuesta, status_code=status.HTTP_201_CREATED)
def crear_habitacion(
    habitacion: schemas.HabitacionCrear, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual) # ¡Candado activado!
):
    db_habitacion = crud_habitaciones.obtener_habitacion_por_numero(db, numero=habitacion.numero_habitacion)
    if db_habitacion:
        raise HTTPException(status_code=400, detail="El número de habitación ya existe")
    return crud_habitaciones.crear_habitacion(db=db, habitacion=habitacion)

@router.get("/", response_model=List[schemas.HabitacionRespuesta])
def listar_habitaciones(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual) # ¡Candado activado!
):
    return crud_habitaciones.obtener_habitaciones(db, skip=skip, limit=limit)

@router.patch("/{id_habitacion}/estado", response_model=schemas.HabitacionRespuesta)
def cambiar_estado_limpieza(
    id_habitacion: int, 
    estado_update: schemas.HabitacionEstadoUpdate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(get_usuario_actual) # ¡Candado activado!
):
    habitacion_actualizada = crud_habitaciones.actualizar_estado_habitacion(db, id_habitacion, estado_update)
    if not habitacion_actualizada:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return habitacion_actualizada