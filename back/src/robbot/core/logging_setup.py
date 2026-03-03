"""
Centralized logging configuration for Clinica Go backend.

Structured logging aligned with WAHA model:
Format: [HH:MM:SS.mmm] LEVEL (ModuleName/ProcessID): Message

Features:
- No emojis (professional logs)
- Structured format with timestamps (milliseconds)
- Process ID for multi-worker debugging
- Log rotation by size and count
- Environment-based log levels (dev: DEBUG, prod: INFO)
- Console + file output
"""

import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Timezone de Brasília (UTC-3)
BRT = timezone(timedelta(hours=-3))


class StructuredFormatter(logging.Formatter):
    """
    WAHA-style structured logging for files (no colors).

    Format: [HH:MM:SS.mmm] LEVEL (PID): Message
    Example: [12:13:58.177] INFO (48): Application started
    """

    def format(self, record: logging.LogRecord) -> str:
        # Use BRT timezone
        ct = datetime.fromtimestamp(record.created, tz=BRT)
        ts = f"{ct.strftime('%H:%M:%S')}.{int(record.msecs):03d}"

        # Format exactly like WAHA - no padding
        return f"[{ts}] {record.levelname} ({record.process}): {record.getMessage()}"


class ColoredStructuredFormatter(logging.Formatter):
    """WAHA-style colorized formatter - clean and beautiful logs.

    Format: [HH:MM:SS.mmm] LEVEL (PID): Message
    Colors: Level-based (green=INFO, yellow=WARNING, red=ERROR)
    """

    # ANSI colors
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"

    # Level colors (bright and clear)
    DEBUG = "\x1b[36m"  # Cyan
    INFO = "\x1b[32m"  # Green
    WARNING = "\x1b[33m"  # Yellow
    ERROR = "\x1b[31m"  # Red
    CRITICAL = "\x1b[91m"  # Bright red

    # Timestamp color
    TIME = "\x1b[90m"  # Gray

    def format(self, record: logging.LogRecord) -> str:
        # Use BRT timezone
        ct = datetime.fromtimestamp(record.created, tz=BRT)
        ts = f"{ct.strftime('%H:%M:%S')}.{int(record.msecs):03d}"

        # Get level color
        level_color = getattr(self, record.levelname, self.INFO)

        # Format: [HH:MM:SS.mmm] LEVEL (PID): Message
        # Exactly like WAHA - no extra spaces
        return (
            f"{self.TIME}[{ts}]{self.RESET} "
            f"{level_color}{record.levelname}{self.RESET} "
            f"{self.DIM}({record.process}){self.RESET}: "
            f"{record.getMessage()}"
        )


class MessagePrefixStripFilter(logging.Filter):
    """Remove leading bracket-tags like [INFO], [SUCCESS], [WARNING], [ERROR] from messages.

    This keeps code-level messages clean while preserving WAHA-style level display.
    """

    _pattern = re.compile(r"^\[(INFO|SUCCESS|WARNING|ERROR)\]\s*")

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        if isinstance(record.msg, str):
            record.msg = self._pattern.sub("", record.msg)
        return True


def get_log_level() -> int:
    """
    Get log level based on environment.

    Returns:
        logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    log_level_str = os.getenv("LOG_LEVEL", "").upper()

    # Environment-based defaults
    if not log_level_str:
        if env in ("production", "prod") or env in ("staging", "test"):
            log_level_str = "INFO"
        else:  # development
            log_level_str = "DEBUG"

    return getattr(logging, log_level_str, logging.INFO)


def configure_logging(
    log_file: str | None = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_file: Path to log file (default: logs/robbot.log)
        max_bytes: Max size per log file before rotation
        backup_count: Number of backup files to keep
        console_output: Enable console output (True for dev, False for prod)

    Example:
        configure_logging()  # Uses defaults
        configure_logging(log_file="custom.log", backup_count=10)
    """
    level = get_log_level()
    root = logging.getLogger()

    # Avoid duplicate handlers on reload
    if root.handlers:
        return

    root.setLevel(level)
    # Console colorization controlled by env LOG_COLOR=true
    use_color = os.getenv("LOG_COLOR", "false").lower() == "true"
    base_formatter = StructuredFormatter()
    console_formatter = ColoredStructuredFormatter() if use_color else base_formatter
    msg_filter = MessagePrefixStripFilter()

    # Console handler (stdout for container logs)
    if console_output:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        console.setFormatter(console_formatter)
        console.addFilter(msg_filter)
        root.addHandler(console)

    # File handler with rotation
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = str(log_dir / "robbot.log")

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(base_formatter)
    file_handler.addFilter(msg_filter)
    root.addHandler(file_handler)

    # Silence noisy HTTP loggers (DEBUG spam from httpcore/httpx)
    # Set to WARNING to only see errors, not every HTTP request detail
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Silence all httpx noise

    # Silence noisy RQ DEBUG logs (queue operations are too verbose)
    logging.getLogger("rq.queue").setLevel(logging.INFO)
    logging.getLogger("rq.worker").setLevel(logging.INFO)
    logging.getLogger("rq.scheduler").setLevel(logging.INFO)

    # Harmonize uvicorn loggers to use root handlers/format
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = []  # delegate to root
        uv_logger.propagate = True

    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured: level=%s, file=%s, max_bytes=%s, backup_count=%s",
        logging.getLevelName(level),
        log_file,
        max_bytes,
        backup_count,
    )
