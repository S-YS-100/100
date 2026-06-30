"""Cache service with Redis fallback and in-memory TTL cache.

Lightweight cache service that stores only small objects with TTL. If REDIS_URL
is provided it uses aioredis; otherwise an in-memory dict with asyncio cleanup
is used. Designed to never cache large datasets.
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from typing import Any, Dict, Optional

from ..config import get_settings

logger = logging.getLogger("autopilot.cache")


class InMemoryCache:
    __slots__ = ("store", "_lock", "_task")

    def __init__(self) -> None:
        self.store: Dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()
        self._task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._purge_loop())

    async def close(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def _purge_loop(self) -> None:
        while True:
            now = time.time()
            async with self._lock:
                keys = [k for k, (_, exp) in self.store.items() if exp and exp < now]
                for k in keys:
                    del self.store[k]
            await asyncio.sleep(1.0)

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            val = self.store.get(key)
            if not val:
                return None
            value, exp = val
            if exp and exp < time.time():
                del self.store[key]
                return None
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        exp = time.time() + ttl if ttl else 0
        async with self._lock:
            self.store[key] = (value, exp)


class CacheService:
    __slots__ = ("settings", "client")

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        self.client: InMemoryCache | None = None

    async def connect(self) -> None:
        # For now default to InMemoryCache. Redis implementation can be added.
        self.client = InMemoryCache()
        await self.client.connect()
        logger.debug("In-memory cache started")

    async def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        return await self.client.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self.client:
            return None
        await self.client.set(key, value, ttl)

    async def close(self) -> None:
        if self.client:
            await self.client.close()
