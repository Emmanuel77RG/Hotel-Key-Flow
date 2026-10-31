from sqlalchemy.orm import Session
from app.models.reservas_folios import ReservaFolio
from app.schemas.reservas_folios import ReservaCrear
from app.models.habitaciones import Habitacion

# Creación del CRUD - F1SP3

def crear_reserva(db: Session, reserva: ReservaCrear):
    db_reserva = ReservaFolio(
        fecha_entrada=reserva.fecha_entrada,
        fecha_salida=reserva.fecha_salida,
        estado_reserva=reserva.estado_reserva,
        estado_folio=reserva.estado_folio,
        id_usuario=reserva.id_usuario,
        id_huesped=reserva.id_huesped
    )
    db.add(db_reserva)
    db.flush() 

    if reserva.id_habitacion:
        habitacion = db.query(Habitacion).filter(Habitacion.id_habitacion == reserva.id_habitacion).first()
        if habitacion:
            db_reserva.habitaciones.append(habitacion)

    db.commit()
    db.refresh(db_reserva)
    return db_reserva

def obtener_reserva(db: Session, reserva_id: int):
    return db.query(ReservaFolio).filter(ReservaFolio.id_reserva == reserva_id).first()

def obtener_reservas(db: Session, skip: int = 0, limit: int = 100):
    from app.models.reservas_folios import ReservaFolio
    return db.query(ReservaFolio).offset(skip).limit(limit).all()

def actualizar_estado_reserva(db: Session, reserva_id: int, nuevo_estado: str):
    reserva = db.query(ReservaFolio).filter(ReservaFolio.id_reserva == reserva_id).first()
    if reserva:
        reserva.estado_reserva = nuevo_estado  
        db.commit()
        db.refresh(reserva)
    return reserva

# F1SP4 - Programar el Check-in

def abrir_cuenta_folio(db: Session, reserva_id: int):
    reserva = db.query(ReservaFolio).filter(ReservaFolio.id_reserva == reserva_id).first()
    if reserva:
        reserva.estado_folio = "Abierto"
        db.commit()
        db.refresh(reserva)
    return reserva