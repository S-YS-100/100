"""HTTP client singleton to be reused across services.

Provides an async context manager wrapping a single aiohttp.ClientSession.
"""
from __future__ import annotations

import aiohttp
import logging

logger = logging.getLogger("autopilot.http")


class HttpClient:
    __slots__ = ("session",)

    def __init__(self) -> None:
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "HttpClient":
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore
        if self.session:
            await self.session.close()
            self.session = None

    async def get(self, url: str, **kwargs):
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        async with self.session.get(url, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def post_json(self, url: str, json: dict, **kwargs):
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        async with self.session.post(url, json=json, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def ping(self) -> None:
        # lightweight network check
        try:
            await self.get("https://api.ipify.org?format=json")
        except Exception:
            logger.warning("HTTP ping failed; network may be restricted")
