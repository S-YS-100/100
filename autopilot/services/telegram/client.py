"""Telegram service that manages the Pyrogram client lifecycle.

Client creation is lazy and uses the token from settings. The service exposes
initialize(), test_authorization() and shutdown() methods used by the app
lifecycle.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from pyrogram import Client
from pyrogram.errors import RPCError

from ..config import get_settings
from ..database.database import DatabaseManager
from ..services.cache import CacheService

logger = logging.getLogger("autopilot.telegram")


class TelegramService:
    __slots__ = ("settings", "client", "db", "cache")

    def __init__(self, settings=None, db: Optional[DatabaseManager] = None, cache: Optional[CacheService] = None) -> None:
        self.settings = settings or get_settings()
        self.client: Optional[Client] = None
        self.db = db
        self.cache = cache

    async def initialize(self) -> None:
        token = self.settings.TOKEN
        # create Pyrogram client
        self.client = Client("autopilot_client", bot_token=token, workdir=".pyrogram")
        # pyrogram Client.start() is sync-like but can be awaited
        await self.client.start()
        logger.info("Pyrogram client started")

    async def test_authorization(self) -> None:
        if not self.client:
            raise RuntimeError("Telegram client not initialized")
        try:
            me = await self.client.get_me()
            logger.info("Telegram authorized as %s (%s)", me.username or me.first_name, me.id)
        except RPCError as exc:
            logger.exception("Telegram authorization failed: %s", exc)
            raise

    async def shutdown(self) -> None:
        if self.client is not None:
            await self.client.stop()
            logger.info("Pyrogram client stopped")
