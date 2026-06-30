"""Rate limiter service using CacheService to throttle user requests.

Provides an async API to check and increment request counters with TTL and
temporary bans.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from ..services.cache import CacheService

logger = logging.getLogger("autopilot.rate_limiter")


class RateLimiter:
    __slots__ = ("cache", "limit", "window", "ban_ttl")

    def __init__(self, cache: CacheService, limit: int = 5, window: int = 10, ban_ttl: int = 60) -> None:
        self.cache = cache
        self.limit = limit
        self.window = window
        self.ban_ttl = ban_ttl

    async def is_banned(self, user_id: int) -> bool:
        b = await self.cache.get(f"ban:{user_id}")
        return bool(b)

    async def check(self, user_id: int) -> bool:
        if await self.is_banned(user_id):
            return False
        key = f"rl:{user_id}"
        cnt = await self.cache.get(key) or 0
        if cnt >= self.limit:
            # ban
            await self.cache.set(f"ban:{user_id}", True, ttl=self.ban_ttl)
            logger.warning("User %s banned for %s seconds due to rate limit", user_id, self.ban_ttl)
            return False
        await self.cache.set(key, cnt + 1, ttl=self.window)
        return True
