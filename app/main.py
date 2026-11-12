from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import Base, engine
from app.api.dependencias import get_db
from app.core.logging_config import inicializar_logging
from app.api.rutas import (
    usuarios,
    auth,
    habitaciones,
    huespedes,
    reservas_folios,
    mantenimiento,
    finanzas,
    pos,
    reportes,
)

# Inicializar logging centralizado con rotación a archivo
logger = inicializar_logging()

# Inicialización segura de tablas
try:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE huespedes ADD COLUMN IF NOT EXISTS rfc VARCHAR(20);"))
        conn.execute(text("ALTER TABLE pagos ALTER COLUMN metodo_pago TYPE VARCHAR(100);"))
        conn.execute(text("ALTER TABLE tickets_mantenimiento ADD COLUMN IF NOT EXISTS categoria VARCHAR(50) DEFAULT 'General';"))
        conn.execute(text("ALTER TABLE tickets_mantenimiento ADD COLUMN IF NOT EXISTS prioridad VARCHAR(30) DEFAULT 'Media';"))
        conn.execute(text("ALTER TABLE tickets_mantenimiento ADD COLUMN IF NOT EXISTS nota_resolucion VARCHAR(255);"))
except Exception as exc:
    logger.warning("Base de datos no disponible durante inicialización estática: %s", exc)

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="API Hotel KeyFlow - Arquitectura Modular",
    description="Sistema PMS local para gestión hotelera, reservas, folios, mantenimiento y POS.",
    version="0.7.0",
)

# Conectamos las rutas (Endpoints)
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(habitaciones.router, prefix="/habitaciones", tags=["Gestión de Habitaciones"])
app.include_router(huespedes.router, prefix="/huespedes", tags=["Gestión de Huéspedes"])
app.include_router(reservas_folios.router, prefix="/reservas", tags=["Gestión de Reservas"])
app.include_router(mantenimiento.router, prefix="/mantenimiento", tags=["Tickets de Mantenimiento"])
app.include_router(finanzas.router, prefix="/finanzas", tags=["Cargos y Pagos"])
app.include_router(pos.router, prefix="/pos", tags=["Punto de Venta (Restaurante y Room Service)"])
app.include_router(reportes.router, prefix="/reportes", tags=["Reportes Operativos y Corte de Caja"])

# Rutas de comprobación de estado y Healthcheck (Punto 20)
@app.get("/", tags=["Status"])
def check_status():
    return {"mensaje": "¡Conexión exitosa! La API modular de Hotel KeyFlow está corriendo a la perfección."}

@app.get("/health", tags=["Status"], summary="Healthcheck del sistema y base de datos")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as exc:
        db_status = f"unhealthy: {exc}"
        logger.error("Fallo de salud en base de datos: %s", exc)

    estado_general = "healthy" if db_status == "healthy" else "degraded"
    codigo_http = status.HTTP_200_OK if db_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": estado_general,
        "database": db_status,
        "version": "0.7.0",
    }
