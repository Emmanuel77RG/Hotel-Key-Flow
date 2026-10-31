from sqlalchemy.orm import Session
from app.models.reservas_folios import ReservaFolio
from app.schemas.reservas_folios import ReservaCrear
from app.models.habitaciones import Habitacion

# F1SP4 (CHECK-IN Y FOLIOS)

def crear_reserva(db: Session, reserva: ReservaCrear):
    # Creamos el objeto solo con los campos directos de la tabla reservas_folios
    db_reserva = ReservaFolio(
        fecha_entrada=reserva.fecha_entrada,
        fecha_salida=reserva.fecha_salida,
        estado_reserva=reserva.estado_reserva,
        estado_folio=reserva.estado_folio,
        id_usuario=reserva.id_usuario,
        id_huesped=reserva.id_huesped
    )
    db.add(db_reserva)
    db.flush() # Asigna el id_reserva sin cerrar la transacción todavía

    # Asociamos la habitación mediante la relación de la tabla intermedia
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

def abrir_cuenta_folio(db: Session, reserva_id: int):
    # En tu diseño, abrir el folio es actualizar la misma tabla
    reserva = db.query(ReservaFolio).filter(ReservaFolio.id_reserva == reserva_id).first()
    if reserva:
        reserva.estado_folio = "Abierto"
        db.commit()
        db.refresh(reserva)
    return reserva