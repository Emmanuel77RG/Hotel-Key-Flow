from fastapi import FastAPI
from app.api.rutas import usuarios, auth, habitaciones

# Inicializamos la aplicación
app = FastAPI(title="API Hotel KeyFlow - Arquitectura Modular")

# Conectamos las rutas (Endpoints)
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(habitaciones.router, prefix="/habitaciones", tags=["Gestión de Habitaciones"])

# Ruta de comprobación de estado
@app.get("/", tags=["Status"])
def check_status():
    return {"mensaje": "¡Conexión exitosa! La API modular de Hotel KeyFlow está corriendo a la perfección."}