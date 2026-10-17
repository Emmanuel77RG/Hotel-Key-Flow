from sqlalchemy import Column, Integer, String, Numeric, Enum
from app.db.database import Base
import enum

# Esta es nuestra Máquina de Estados
class EstadoHabitacion(str, enum.Enum):
    LIMPIA = "Limpia"
    SUCIA = "Sucia"
    EN_LIMPIEZA = "En Limpieza"
    OCUPADA = "Ocupada"
    MANTENIMIENTO = "Mantenimiento"

class Habitacion(Base):
    __tablename__ = "habitaciones"
    
    id_habitacion = Column(Integer, primary_key=True, index=True)
    numero_habitacion = Column(String(10), unique=True, index=True, nullable=False)
    tipo = Column(String(50), nullable=False) # Ej. Sencilla, Doble, Suite
    capacidad = Column(Integer, nullable=False)
    precio_base = Column(Numeric(10, 2), nullable=False)
    estado = Column(Enum(EstadoHabitacion), default=EstadoHabitacion.LIMPIA, nullable=False)