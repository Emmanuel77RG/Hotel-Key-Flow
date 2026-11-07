from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.models.reservas_folios import ReservaFolio
from app.schemas.reservas_folios import ReservaCrear
from app.models.habitaciones import Habitacion
from app.models.finanzas import Cargo, Pago

# Creación del CRUD - F1SP3

def verificar_disponibilidad_fechas(
    db: Session,
    id_habitacion: int,
    fecha_entrada: date,
    fecha_salida: date,
    excluir_reserva_id: int | None = None
) -> bool:
    """
    RF-RES-003: Verifica que la habitación no tenga reservas activas o confirmadas
    cuyas fechas se traslapen con el rango [fecha_entrada, fecha_salida).
    """
    query = (
        db.query(ReservaFolio)
        .join(ReservaFolio.habitaciones)
        .filter(
            Habitacion.id_habitacion == id_habitacion,
            ReservaFolio.estado_reserva.in_(["Pendiente", "Confirmada", "Activa"]),
            ReservaFolio.fecha_entrada < fecha_salida,
            ReservaFolio.fecha_salida > fecha_entrada,
        )
    )
    if excluir_reserva_id is not None:
        query = query.filter(ReservaFolio.id_reserva != excluir_reserva_id)
    reserva_en_conflicto = query.first()
    return reserva_en_conflicto is None

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
    return (
        db.query(ReservaFolio)
        .options(joinedload(ReservaFolio.huesped), joinedload(ReservaFolio.habitaciones))
        .filter(ReservaFolio.id_reserva == reserva_id)
        .first()
    )

def obtener_reservas(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(ReservaFolio)
        .options(joinedload(ReservaFolio.huesped), joinedload(ReservaFolio.habitaciones))
        .order_by(ReservaFolio.id_reserva.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def actualizar_estado_reserva(db: Session, reserva_id: int, nuevo_estado: str):
    reserva = db.query(ReservaFolio).filter(ReservaFolio.id_reserva == reserva_id).first()
    if reserva:
        reserva.estado_reserva = nuevo_estado  
        db.commit()
        db.refresh(reserva)
    return reserva

# F1SP4 - Programar el Check-in y Check-out

def abrir_cuenta_folio(db: Session, reserva_id: int):
    reserva = db.query(ReservaFolio).filter(ReservaFolio.id_reserva == reserva_id).first()
    if reserva:
        reserva.estado_folio = "Abierto"
        db.commit()
        db.refresh(reserva)
    return reserva

def cerrar_cuenta_folio(db: Session, reserva_id: int):
    reserva = db.query(ReservaFolio).filter(ReservaFolio.id_reserva == reserva_id).first()
    if reserva:
        reserva.estado_folio = "Cerrado"
        db.commit()
        db.refresh(reserva)
    return reserva

def calcular_saldo_folio(db: Session, reserva_id: int) -> dict:
    cargos = db.query(Cargo).filter(Cargo.id_reserva == reserva_id).all()
    pagos = db.query(Pago).filter(Pago.id_reserva == reserva_id).all()
    total_cargos = round(sum(float(c.monto) for c in cargos), 2)
    total_pagos = round(sum(float(p.monto) for p in pagos), 2)
    saldo_pendiente = round(total_cargos - total_pagos, 2)
    return {
        "total_cargos": total_cargos,
        "total_pagos": total_pagos,
        "saldo_pendiente": saldo_pendiente,
        "cargos": cargos,
        "pagos": pagos,
    }