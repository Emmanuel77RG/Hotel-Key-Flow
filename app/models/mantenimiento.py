from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class TicketMantenimiento(Base):
    __tablename__ = "tickets_mantenimiento"

    id_ticket = Column(Integer, primary_key=True, index=True, autoincrement=True)
    categoria = Column(String(50), nullable=False, default="General")
    prioridad = Column(String(30), nullable=False, default="Media")
    descripcion_falla = Column(String(255), nullable=False)
    estado_ticket = Column(String(50), nullable=False, default="Pendiente")
    nota_resolucion = Column(String(255), nullable=True)
    id_habitacion = Column(Integer, ForeignKey("habitaciones.id_habitacion"), nullable=True)
    id_usuario_reporta = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_resolucion = Column(DateTime, nullable=True)

    habitacion = relationship("Habitacion")
    usuario_reporta = relationship("Usuario")