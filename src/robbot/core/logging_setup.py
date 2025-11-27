import logging
from logging.handlers import RotatingFileHandler
import os

from robbot.config.settings import settings

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def configure_logging() -> None:
    """
    Configura o logging básico da aplicação.
    - Console handler
    - RotatingFileHandler (arquivo local) para captura histórica em dev
    """
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger()
    if root.handlers:
        # evita adicionar handlers duplicados em reinícios do container durante dev
        return

    root.setLevel(level)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    root.addHandler(console)

    # Rotating file handler (opcional, útil em dev)
    log_file = getattr(settings, "LOG_FILE", None) or "robbot.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    root.addHandler(file_handler)
