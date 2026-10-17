import os

# Variables globales de configuración
SQLALCHEMY_DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:adminpsw@localhost:5432/hotel_keyflow",
)

SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-hotel-keyflow-cambiar-en-produccion")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

