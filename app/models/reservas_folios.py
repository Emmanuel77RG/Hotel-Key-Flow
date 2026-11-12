from sqlalchemy import Column, Integer, Date, String, DateTime, ForeignKey, Table
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

# Lógica de Reservas - F1SP3
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
    habitaciones = relationship("Habitacion", secondary=reservas_habitaciones, backref="reservas")
    huesped = relationship("Huesped")

    @property
    def nombre_huesped(self):
        return self.huesped.nombre_completo if self.huesped else None

    @property
    def numeros_habitaciones(self):
        if self.habitaciones:
            return ", ".join(str(h.numero_habitacion) for h in self.habitaciones)
        return "Sin hab."