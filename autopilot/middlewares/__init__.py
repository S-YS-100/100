"""Middleware implementations used to wrap handler execution.

Each middleware is async and receives the handler and arguments to execute.
Middlewares compose by calling the next callable in the chain.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Awaitable, Callable

from ..config import get_settings

logger = logging.getLogger("autopilot.middlewares")


class LoggingMiddleware:
    __slots__ = ()

    async def __call__(self, handler: Callable[..., Awaitable[Any]], *args, **kwargs):
        start = time.time()
        try:
            return await handler(*args, **kwargs)
        finally:
            elapsed = time.time() - start
            logger.info("Handler %s executed in %.3fs", getattr(handler, "__name__", "handler"), elapsed)


class RateLimitMiddleware:
    __slots__ = ("limit", "window", "cache")

    def __init__(self, cache, limit: int = 5, window: int = 10):
        self.cache = cache
        self.limit = limit
        self.window = window

    async def __call__(self, handler, update, *args, **kwargs):
        user_id = getattr(update, "user_id", None) or getattr(update, "from_user_id", None)
        if user_id is None:
            return await handler(update, *args, **kwargs)
        key = f"rl:{user_id}"
        counter = await self.cache.get(key) or 0
        if counter >= self.limit:
            logger.warning("Rate limit exceeded for user %s", user_id)
            return None
        await self.cache.set(key, counter + 1, ttl=self.window)
        return await handler(update, *args, **kwargs)


class MaintenanceMiddleware:
    __slots__ = ("enabled",)

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    async def __call__(self, handler, *args, **kwargs):
        if self.enabled:
            logger.info("Maintenance mode active — blocking handler")
            return None
        return await handler(*args, **kwargs)


class BanMiddleware:
    __slots__ = ("banned_set",)

    def __init__(self, banned_set: set[int] | None = None) -> None:
        self.banned_set = banned_set or set()

    async def __call__(self, handler, update, *args, **kwargs):
        user_id = getattr(update, "user_id", None) or getattr(update, "from_user_id", None)
        if user_id in self.banned_set:
            logger.warning("Blocked banned user %s", user_id)
            return None
        return await handler(update, *args, **kwargs)


class LanguageMiddleware:
    __slots__ = ()

    async def __call__(self, handler, update, *args, **kwargs):
        # Could set language in context; left minimal for now
        return await handler(update, *args, **kwargs)


class ErrorMiddleware:
    __slots__ = ()

    async def __call__(self, handler, *args, **kwargs):
        try:
            return await handler(*args, **kwargs)
        except Exception:
            logger.exception("Unhandled error in handler")
            return None
