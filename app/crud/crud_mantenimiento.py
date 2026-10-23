from sqlalchemy.orm import Session
from app.models.mantenimiento import TicketMantenimiento
from app.schemas.mantenimiento import TicketMantenimientoCrear

def obtener_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TicketMantenimiento).offset(skip).limit(limit).all()

def obtener_ticket_por_id(db: Session, id_ticket: int):
    return db.query(TicketMantenimiento).filter(TicketMantenimiento.id_ticket == id_ticket).first()

def crear_ticket(db: Session, ticket: TicketMantenimientoCrear):
    db_ticket = TicketMantenimiento(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket