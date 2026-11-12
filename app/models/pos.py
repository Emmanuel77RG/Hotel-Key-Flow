from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from app.db.database import Base


class ProductoPOS(Base):
    __tablename__ = "productos_pos"

    id_producto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    categoria = Column(String(60), nullable=False, default="Restaurante / Alimentos")
    precio_unitario = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
