"""Advanced logging configuration with rotating files and colored console.

Uses colorama for console colors and a TimedRotatingFileHandler for persisted
logs under logs/ directory. File rotation keeps the last 14 days by default.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from typing import Optional

from colorama import Fore, Style, init as colorama_init

from .config import Settings, get_settings


class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore
        level = record.levelno
        if level >= logging.ERROR:
            color = Fore.RED
        elif level >= logging.WARNING:
            color = Fore.YELLOW
        elif level >= logging.INFO:
            color = Fore.GREEN
        else:
            color = Fore.CYAN
        msg = super().format(record)
        return f"{color}{msg}{Style.RESET_ALL}"


def configure_logging(settings: Optional[Settings] = None) -> None:
    settings = settings or get_settings()
    colorama_init()

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    # Console handler with colors
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(ColoredFormatter("%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"))

    # File handler with rotation
    os.makedirs("logs", exist_ok=True)
    fh = logging.handlers.TimedRotatingFileHandler("logs/autopilot.log", when="midnight", backupCount=14, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S"))

    # Clean handlers
    for h in list(root.handlers):
        root.removeHandler(h)

    root.addHandler(ch)
    root.addHandler(fh)

    logging.getLogger(__name__).debug("Logging configured with level %s", settings.LOG_LEVEL)
