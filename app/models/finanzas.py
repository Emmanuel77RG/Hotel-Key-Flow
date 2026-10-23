from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.db.database import Base

class Cargo(Base):
    __tablename__ = "cargos"

    id_cargo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    monto = Column(Float, nullable=False)
    descripcion = Column(String(255), nullable=False)
    id_reserva = Column(Integer, ForeignKey("reservas_folios.id_reserva", ondelete="CASCADE"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, index=True, autoincrement=True)
    monto = Column(Float, nullable=False)
    metodo_pago = Column(String(50), nullable=False)
    id_reserva = Column(Integer, ForeignKey("reservas_folios.id_reserva", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)