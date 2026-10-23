from sqlalchemy import Column, Integer, Date, String, DateTime, ForeignKey, Table
from datetime import datetime
from app.db.database import Base

# Tabla intermedia exacta del DDL
reservas_habitaciones = Table(
    "reservas_habitaciones",
    Base.metadata,
    Column("id_reserva", Integer, ForeignKey("reservas_folios.id_reserva", ondelete="CASCADE"), primary_key=True),
    Column("id_habitacion", Integer, ForeignKey("habitaciones.id_habitacion", ondelete="CASCADE"), primary_key=True)
)

class ReservaFolio(Base):
    __tablename__ = "reservas_folios"

    id_reserva = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fecha_entrada = Column(Date, nullable=False)
    fecha_salida = Column(Date, nullable=False)
    estado_reserva = Column(String(50), nullable=False)
    estado_folio = Column(String(50), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    id_huesped = Column(Integer, ForeignKey("huespedes.id_huesped"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)