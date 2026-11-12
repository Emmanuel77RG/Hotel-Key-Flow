"""
Configuración centralizada de Logging para Hotel KeyFlow.
Proporciona salida tanto a consola como a archivo rotativo (RotatingFileHandler).
"""
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

# Directorio de logs en la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "hotel_keyflow.log"

FORMATO_LOG = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
FECHA_FORMATO = "%Y-%m-%d %H:%M:%S"


def inicializar_logging(nivel=logging.INFO):
    """
    Configura el sistema de logging con salida a consola y archivo rotativo.
    Rotación: Archivos de hasta 5 MB, manteniendo un máximo de 5 respaldos.
    """
    logger_raiz = logging.getLogger()
    if logger_raiz.hasHandlers():
        logger_raiz.handlers.clear()

    logger_raiz.setLevel(nivel)

    # 1. Handler para consola (stdout)
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(nivel)
    formatter_consola = logging.Formatter(FORMATO_LOG, datefmt=FECHA_FORMATO)
    handler_consola.setFormatter(formatter_consola)
    logger_raiz.addHandler(handler_consola)

    # 2. Handler rotativo a archivo
    handler_archivo = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB por archivo
        backupCount=5,              # Mantener 5 rotaciones
        encoding="utf-8"
    )
    handler_archivo.setLevel(nivel)
    formatter_archivo = logging.Formatter(FORMATO_LOG, datefmt=FECHA_FORMATO)
    handler_archivo.setFormatter(formatter_archivo)
    logger_raiz.addHandler(handler_archivo)

    logger = logging.getLogger("hotel_keyflow")
    logger.info("Sistema de logging rotativo inicializado correctamente en: %s", LOG_FILE)
    return logger
