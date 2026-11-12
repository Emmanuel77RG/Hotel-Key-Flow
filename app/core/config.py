import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError(
        "CRITICAL: La variable de entorno DATABASE_URL no está definida. "
        "Por favor configura tu archivo .env basado en .env.example."
    )

SECRET_KEY: str = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "CRITICAL: La variable de entorno SECRET_KEY no está definida. "
        "Por favor configura tu archivo .env basado en .env.example."
    )

ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
