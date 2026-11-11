from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from datetime import datetime
from app.db.database import Base

class Cargo(Base):
    __tablename__ = "cargos"

    id_cargo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    monto = Column(Numeric(10, 2), nullable=False)
    descripcion = Column(String(255), nullable=False)
    # Regla contable: RESTRICT para impedir borrado en cascada de comprobantes financieros
    id_reserva = Column(Integer, ForeignKey("reservas_folios.id_reserva", ondelete="RESTRICT"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Pago(Base):
    __tablename__ = "pagos"

    id_pago = Column(Integer, primary_key=True, index=True, autoincrement=True)
    monto = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(String(100), nullable=False)
    # Regla contable: RESTRICT para impedir borrado en cascada de comprobantes financieros
    id_reserva = Column(Integer, ForeignKey("reservas_folios.id_reserva", ondelete="RESTRICT"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
