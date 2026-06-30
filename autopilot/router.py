"""Central router for mapping update types to handler callables.

This is a simple, dependency-free router that handler modules can use to
register their async callbacks during application setup.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List

Handler = Callable[..., Awaitable[Any]]


class Router:
    """Lightweight router storing handlers by name and type."""

    def __init__(self) -> None:
        self.handlers: Dict[str, List[Handler]] = {}

    def add_handler(self, name: str, handler: Handler) -> None:
        self.handlers.setdefault(name, []).append(handler)

    def get_handlers(self, name: str) -> List[Handler]:
        return self.handlers.get(name, [])


# package-level router instance
router = Router()
