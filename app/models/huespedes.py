from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base

class Huesped(Base):
    __tablename__ = "huespedes"

    id_huesped = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Regla de Integridad Referencial: UNIQUE para impedir documentos de identidad duplicados
    documento_identidad = Column(String(50), unique=True, index=True, nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    email = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    rfc = Column(String(20), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
