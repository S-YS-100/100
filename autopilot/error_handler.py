"""Global error handling utilities for the application.

Wraps common network and database exceptions and implements retry where
appropriate to avoid crashing the application.
"""
from __future__ import annotations

import logging
import asyncio
from typing import Callable, Coroutine, TypeVar

T = TypeVar("T")
logger = logging.getLogger("autopilot.errors")


async def retry(coro: Callable[..., Coroutine[None, None, T]], attempts: int = 3, delay: float = 1.0) -> T:
    last = None
    for i in range(attempts):
        try:
            return await coro()
        except Exception as exc:
            last = exc
            logger.warning("Retry %d/%d failed: %s", i + 1, attempts, exc)
            await asyncio.sleep(delay * (i + 1))
    raise last  # type: ignore
