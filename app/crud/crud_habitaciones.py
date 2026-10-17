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