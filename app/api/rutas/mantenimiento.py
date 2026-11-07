from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencias import get_db, get_usuario_actual
from app.schemas.mantenimiento import (
    TicketMantenimientoCrear,
    TicketMantenimientoEstadoActualizar,
    TicketMantenimientoRespuesta,
)
from app.crud import crud_mantenimiento, crud_habitaciones

router = APIRouter()

ESTADOS_TICKET_PERMITIDOS = ["Pendiente", "En Reparación", "Resuelto"]

@router.get("/", response_model=List[TicketMantenimientoRespuesta], summary="Listar tickets de mantenimiento")
def listar_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    return crud_mantenimiento.obtener_tickets(db, skip=skip, limit=limit)

@router.post(
    "/",
    response_model=TicketMantenimientoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un ticket de falla y bloquear la habitación en Mantenimiento",
)
def crear_ticket(
    ticket: TicketMantenimientoCrear,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    if not ticket.descripcion_falla or not ticket.descripcion_falla.strip():
        raise HTTPException(
            status_code=400,
            detail="La descripción de la falla es obligatoria.",
        )

    habitacion = crud_habitaciones.obtener_habitacion(db, habitacion_id=ticket.id_habitacion)
    if not habitacion:
        raise HTTPException(status_code=404, detail="La habitación seleccionada no existe.")

    if habitacion.estado == "Ocupada":
        raise HTTPException(
            status_code=400,
            detail=f"La habitación {habitacion.numero_habitacion} está actualmente 'Ocupada' por un huésped. Realice primero el Check-out o cambio de habitación antes de bloquearla por mantenimiento.",
        )

    ticket.id_usuario_reporta = usuario_actual.id_usuario
    ticket.estado_ticket = "Pendiente"

    nuevo_ticket = crud_mantenimiento.crear_ticket(db=db, ticket=ticket)

    # Bloqueo automático del estado físico de la habitación a 'Mantenimiento'
    habitacion.estado = "Mantenimiento"
    db.commit()

    return nuevo_ticket

@router.patch(
    "/{id_ticket}/estado",
    response_model=TicketMantenimientoRespuesta,
    summary="Actualizar estado de un ticket de mantenimiento y liberar habitación al resolver",
)
def actualizar_estado_ticket(
    id_ticket: int,
    datos_estado: TicketMantenimientoEstadoActualizar,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_usuario_actual),
):
    nuevo_estado = datos_estado.estado_ticket
    if nuevo_estado not in ESTADOS_TICKET_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Estado de ticket no válido. Opciones permitidas: {ESTADOS_TICKET_PERMITIDOS}",
        )

    ticket_actual = crud_mantenimiento.obtener_ticket_por_id(db, id_ticket=id_ticket)
    if not ticket_actual:
        raise HTTPException(status_code=404, detail="Ticket de mantenimiento no encontrado.")

    ticket_actualizado = crud_mantenimiento.actualizar_estado_ticket(
        db=db, id_ticket=id_ticket, nuevo_estado=nuevo_estado
    )

    if ticket_actualizado and ticket_actualizado.id_habitacion:
        habitacion = crud_habitaciones.obtener_habitacion(
            db, habitacion_id=ticket_actualizado.id_habitacion
        )
        if habitacion and habitacion.estado != "Ocupada":
            if nuevo_estado == "Resuelto":
                # Si ya no quedan otros tickets abiertos para esta habitación, pasa a 'Sucia' para limpieza
                if not crud_mantenimiento.tiene_tickets_activos_habitacion(
                    db, id_habitacion=habitacion.id_habitacion
                ):
                    habitacion.estado = "Sucia"
                    db.commit()
            else:
                habitacion.estado = "Mantenimiento"
                db.commit()

    return ticket_actualizado