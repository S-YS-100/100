"""Image service for upload/processing images.

This module provides an async interface to process or proxy images. The
implementation is minimal and uses the shared HTTP client when needed.
"""
from __future__ import annotations

import logging
from typing import Optional

from ..services.http import HttpClient

logger = logging.getLogger("autopilot.images")


class ImageService:
    __slots__ = ("http",)

    def __init__(self, http: Optional[HttpClient] = None) -> None:
        self.http = http

    async def fetch_image_bytes(self, url: str) -> bytes:
        if not self.http or not self.http.session:
            raise RuntimeError("HTTP client not initialized")
        async with self.http.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.read()
