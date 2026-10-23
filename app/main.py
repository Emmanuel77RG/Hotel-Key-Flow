from fastapi import FastAPI
from app.db.database import Base, engine
from app.api.rutas import usuarios, auth, habitaciones
from app.models import (
    usuarios as usuarios_model,
    habitaciones as habitaciones_model,
    huespedes as huespedes_model,
    reservas_folios as reservas_model,
    mantenimiento as mantenimiento_model,
    finanzas as finanzas_model
)
from app.api.rutas import (
    usuarios,
    auth,
    habitaciones,
    huespedes,
    reservas_folios,
    mantenimiento,
    finanzas
)

# CREA LAS TABLAS AUTOMÁTICAMENTE AL ARRANCAR
Base.metadata.create_all(bind=engine)

# Inicializamos la aplicación
app = FastAPI(title="API Hotel KeyFlow - Arquitectura Modular")

# Conectamos las rutas (Endpoints)
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(habitaciones.router, prefix="/habitaciones", tags=["Gestión de Habitaciones"])
app.include_router(huespedes.router, prefix="/huespedes", tags=["Gestión de Huéspedes"])
app.include_router(reservas_folios.router, prefix="/reservas", tags=["Gestión de Reservas"])
app.include_router(mantenimiento.router, prefix="/mantenimiento", tags=["Tickets de Mantenimiento"])
app.include_router(finanzas.router, prefix="/finanzas", tags=["Cargos y Pagos"])

# Ruta de comprobación de estado
@app.get("/", tags=["Status"])
def check_status():
    return {"mensaje": "¡Conexión exitosa! La API modular de Hotel KeyFlow está corriendo a la perfección."}