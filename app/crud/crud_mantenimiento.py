from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.mantenimiento import TicketMantenimiento
from app.schemas.mantenimiento import (
    TicketMantenimientoActualizar,
    TicketMantenimientoCrear,
)

def _enriquecer_ticket(db_ticket: TicketMantenimiento):
    if not db_ticket:
        return None
    db_ticket.numero_habitacion = (
        db_ticket.habitacion.numero_habitacion if db_ticket.habitacion else "S/N"
    )
    db_ticket.nombre_usuario_reporta = (
        db_ticket.usuario_reporta.nombre if db_ticket.usuario_reporta else "Personal"
    )
    if not db_ticket.categoria:
        db_ticket.categoria = "General"
    if not db_ticket.prioridad:
        db_ticket.prioridad = "Media"
    return db_ticket

def obtener_tickets(db: Session, skip: int = 0, limit: int = 100):
    tickets = (
        db.query(TicketMantenimiento)
        .order_by(TicketMantenimiento.id_ticket.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_enriquecer_ticket(t) for t in tickets]

def obtener_ticket_por_id(db: Session, id_ticket: int):
    ticket = (
        db.query(TicketMantenimiento)
        .filter(TicketMantenimiento.id_ticket == id_ticket)
        .first()
    )
    return _enriquecer_ticket(ticket)

def crear_ticket(db: Session, ticket: TicketMantenimientoCrear):
    db_ticket = TicketMantenimiento(
        id_habitacion=ticket.id_habitacion,
        id_usuario_reporta=ticket.id_usuario_reporta,
        categoria=(ticket.categoria or "General").strip(),
        prioridad=(ticket.prioridad or "Media").strip(),
        descripcion_falla=ticket.descripcion_falla.strip(),
        estado_ticket=ticket.estado_ticket or "Pendiente",
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return _enriquecer_ticket(db_ticket)

def actualizar_ticket(
    db: Session, id_ticket: int, datos: TicketMantenimientoActualizar
):
    db_ticket = (
        db.query(TicketMantenimiento)
        .filter(TicketMantenimiento.id_ticket == id_ticket)
        .first()
    )
    if not db_ticket:
        return None
    if datos.categoria is not None:
        db_ticket.categoria = datos.categoria.strip()
    if datos.prioridad is not None:
        db_ticket.prioridad = datos.prioridad.strip()
    if datos.descripcion_falla is not None:
        db_ticket.descripcion_falla = datos.descripcion_falla.strip()
    db.commit()
    db.refresh(db_ticket)
    return _enriquecer_ticket(db_ticket)

def actualizar_estado_ticket(
    db: Session,
    id_ticket: int,
    nuevo_estado: str,
    nota_resolucion: Optional[str] = None,
):
    db_ticket = (
        db.query(TicketMantenimiento)
        .filter(TicketMantenimiento.id_ticket == id_ticket)
        .first()
    )
    if not db_ticket:
        return None
    db_ticket.estado_ticket = nuevo_estado
    if nuevo_estado == "Resuelto":
        db_ticket.fecha_resolucion = datetime.utcnow()
        if nota_resolucion is not None:
            db_ticket.nota_resolucion = nota_resolucion.strip() or None
    else:
        db_ticket.fecha_resolucion = None
    db.commit()
    db.refresh(db_ticket)
    return _enriquecer_ticket(db_ticket)

def eliminar_ticket(db: Session, id_ticket: int) -> Optional[int]:
    db_ticket = (
        db.query(TicketMantenimiento)
        .filter(TicketMantenimiento.id_ticket == id_ticket)
        .first()
    )
    if not db_ticket:
        return None
    id_hab = db_ticket.id_habitacion
    db.delete(db_ticket)
    db.commit()
    return id_hab

def tiene_tickets_activos_habitacion(db: Session, id_habitacion: int) -> bool:
    activos = (
        db.query(TicketMantenimiento)
        .filter(
            TicketMantenimiento.id_habitacion == id_habitacion,
            TicketMantenimiento.estado_ticket != "Resuelto",
        )
        .count()
    )
    return activos > 0