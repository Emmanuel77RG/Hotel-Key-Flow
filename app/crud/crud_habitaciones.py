from sqlalchemy.orm import Session
from app.models import habitaciones as models
from app.schemas import habitaciones as schemas

def obtener_habitacion_por_numero(db: Session, numero: str):
    return db.query(models.Habitacion).filter(models.Habitacion.numero_habitacion == numero).first()

def obtener_habitaciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Habitacion).offset(skip).limit(limit).all()

def crear_habitacion(db: Session, habitacion: schemas.HabitacionCrear):
    # Convertimos el esquema a un diccionario para pasarlo al modelo
    nueva_habitacion = models.Habitacion(**habitacion.model_dump())
    db.add(nueva_habitacion)
    db.commit()
    db.refresh(nueva_habitacion)
    return nueva_habitacion

def actualizar_estado_habitacion(db: Session, id_habitacion: int, estado_update: schemas.HabitacionEstadoUpdate):
    habitacion_db = db.query(models.Habitacion).filter(models.Habitacion.id_habitacion == id_habitacion).first()
    if habitacion_db:
        habitacion_db.estado = estado_update.estado
        db.commit()
        db.refresh(habitacion_db)
    return habitacion_db

def obtener_habitacion(db: Session, habitacion_id: int):
    from app.models.habitaciones import Habitacion 
    return db.query(Habitacion).filter(Habitacion.id_habitacion == habitacion_id).first()

def actualizar_habitacion(db: Session, id_habitacion: int, datos: schemas.HabitacionActualizar):
    habitacion_db = obtener_habitacion(db, id_habitacion)
    if not habitacion_db:
        return None
    if datos.numero_habitacion is not None:
        habitacion_db.numero_habitacion = datos.numero_habitacion
    if datos.tipo is not None:
        habitacion_db.tipo = datos.tipo
    if datos.capacidad is not None:
        habitacion_db.capacidad = datos.capacidad
    if datos.precio_base is not None:
        habitacion_db.precio_base = datos.precio_base
    if datos.estado is not None:
        habitacion_db.estado = datos.estado
    db.commit()
    db.refresh(habitacion_db)
    return habitacion_db