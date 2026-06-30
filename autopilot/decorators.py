"""Decorator utilities used across handlers and services.

These decorators are lightweight and generic so they can be applied to multiple
handler frameworks. They intentionally don't import Telegram-specific types to
keep them usable and import-safe during early startup.
"""
from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Awaitable, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])
logger = logging.getLogger("autopilot.decorators")


def owner_only(func: F) -> F:
    """Decorator that asserts the first argument (usually `event`/`update`) has a `user_id` attribute matching OWNER_ID.

    This is a lightweight guard used at runtime in handlers. It does not prevent
    import-time side effects.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        from .config import get_settings

        settings = get_settings()
        owner = settings.OWNER_ID
        user_id = None
        if args:
            ev = args[0]
            user_id = getattr(ev, "user_id", None) or getattr(ev, "from_user_id", None)
        if owner is None:
            logger.warning("OWNER_ID not set — owner_only check will pass")
        elif user_id is not None and int(user_id) != int(owner):
            logger.warning("Permission denied for user %s", user_id)
            return None
        return await func(*args, **kwargs)

    return wrapper  # type: ignore


def log_execution(func: F) -> F:
    """Log execution time and arguments for async functions."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = asyncio.get_event_loop().time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = asyncio.get_event_loop().time() - start
            logger.info("Executed %s in %.3fs", func.__name__, elapsed)

    return wrapper  # type: ignore


def handle_errors(func: F) -> F:
    """Top-level error handler to avoid bubbling exceptions to the event loop."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            logger.exception("Unhandled exception in handler %s", func.__name__)
            # Failure is swallowed — handlers should manage user-facing errors.
            return None

    return wrapper  # type: ignore
