import logging
import os
import sys
from datetime import datetime

def get_logger(name: str):
    """
    Devuelve un logger configurado para consola y archivo.
    Incluye timestamps, nivel, módulo y soporte de tracebacks con exc_info=True.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Nombre del archivo log diario
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Evitar duplicar handlers
    if not logger.handlers:
        # 🖥️ Consola (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_format)

        # 📁 Archivo (logs/app_YYYYMMDD.log)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # 🧩 Evitar propagación a root (doble impresión en consola)
        logger.propagate = False

    return logger


# ============================================================
# 💡 Ejemplo de uso con traceback
# ============================================================
if __name__ == "__main__":
    log = get_logger(__name__)
    try:
        1 / 0
    except Exception as e:
        # El parámetro exc_info=True muestra el stack completo en el log
        log.error(f"❌ Error de prueba: {e}", exc_info=True)
