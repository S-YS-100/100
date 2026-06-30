"""Structured logging configuration for autopilot.

This module configures python's standard logging as well as structlog when
available. The goal is to produce structured events containing timestamp,
level, and message. Handlers and formatters are intentionally lightweight so
they function in environments without third-party logging backends.
"""
from __future__ import annotations

import logging
import sys
from typing import Any

from .config import Settings, get_settings


def configure_logging(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Basic configuration — console in a readable format.
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)

    # Remove other handlers to avoid double logging in some environments.
    for h in list(root.handlers):
        root.removeHandler(h)

    root.addHandler(handler)

    # Extra: configure uvloop or other integrations here if desired.
    logging.getLogger(__name__).debug("Logging configured", extra={"level": settings.LOG_LEVEL})
