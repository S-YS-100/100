"""Cache service placeholder. Implement TTL-backed caches here (Redis).

The cache must be lightweight and never store large datasets. Provide a small
async client wrapper that other services can import without side effects.
"""
from __future__ import annotations

from typing import Any, Optional


class Cache:
    async def get(self, key: str) -> Optional[Any]:
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        return None
