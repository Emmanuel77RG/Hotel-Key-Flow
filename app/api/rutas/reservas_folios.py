from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.habitaciones import EstadoHabitacion
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
    habitacion = crud_habitaciones.obtener_habitacion(db, habitacion_id=reserva.id_habitacion)
    if not habitacion:
        raise HTTPException(status_code=404, detail="La habitación solicitada no existe.")
    
    if habitacion.estado != EstadoHabitacion.LIMPIA:  # o comparando con su valor en texto según tu lógica
        raise HTTPException(
            status_code=400,
            detail=f"La habitación {habitacion.numero_habitacion} actualmente se encuentra {habitacion.estado}."
        )

    # OPERACIÓN CRUD
    nueva_reserva = crud_reservas_folios.crear_reserva(db=db, reserva=reserva)
    return nueva_reserva

# F1SP4 - CHECK-IN Y FOLIO

@router.post("/{reserva_id}/checkin", summary="Realizar Check-in y generar Cuenta Folio (F1SP4)")
def realizar_checkin(reserva_id: int, db: Session = Depends(get_db)):
    
    # 1. Validar que la reserva exista
    reserva = crud_reservas_folios.obtener_reserva(db, reserva_id=reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")
    
    # 2. Validar que no se haya hecho check-in antes
    if reserva.estado_reserva not in ["Pendiente", "Confirmada"]:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede hacer check-in. La reserva está '{reserva.estado_reserva}'."
        )

    # 3. Actualizar la reserva a estado Activa (Check-in)
    reserva_actualizada = crud_reservas_folios.actualizar_estado_reserva(
        db, reserva_id=reserva_id, nuevo_estado="Activa"
    )

    # 4. Generar la Cuenta Folio (Cambiando el estado_folio a "Abierto")
    crud_reservas_folios.abrir_cuenta_folio(db=db, reserva_id=reserva_id)

    return {
        "mensaje": "Check-in realizado y Folio abierto con éxito.",
        "reserva_id": reserva_id,
        "nuevo_estado_reserva": "Activa",
        "nuevo_estado_folio": "Abierto"
    }