"""Application context to expose the running Application instance to handlers and services.

This module contains a single global `app` variable which is set by the
Application constructor at runtime. Handlers can import this module to access
shared services (db, cache, ai, telegram) without creating circular imports.
"""
from __future__ import annotations

from typing import Any

app: Any = None
