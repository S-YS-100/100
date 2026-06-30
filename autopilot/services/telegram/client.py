"""Telegram service that manages the Pyrogram client lifecycle and routes updates to local handlers.

This service creates the Pyrogram client, registers lightweight message and
callback listeners that translate Pyrogram objects into small `update` objects
consumed by application handlers (which are registered in the central router
or callback_router).

FloodWait and RPC errors are handled with backoff to avoid crashing.
"""
from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace
from typing import Any, Optional

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from ..config import get_settings
from ..database.database import DatabaseManager
from ..services.cache import CacheService
from ..router import router
from ..callbacks import callback_router

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
        await self.client.start()
        logger.info("Pyrogram client started")

        # register internal handlers for messages and callbacks
        async def _on_message(client: Client, message: Any) -> None:
            text = (message.text or message.caption or "")
            # build a small update object consumed by registered handlers
            update = SimpleNamespace(
                user_id=(message.from_user.id if message.from_user else None),
                chat_id=message.chat.id,
                text=text,
                message=message,
                chat_type=(message.chat.type if message.chat else None),
            )
            try:
                # command routing
                if text.startswith("/start"):
                    handlers = router.get_handlers("start")
                    for h in handlers:
                        await h(update, client)
                elif text.startswith("/broadcast"):
                    handlers = router.get_handlers("broadcast")
                    for h in handlers:
                        await h(update, client)
                elif text.startswith("/ai"):
                    handlers = router.get_handlers("ai")
                    for h in handlers:
                        await h(update, client)
                else:
                    # generic message handlers
                    handlers = router.get_handlers("message")
                    for h in handlers:
                        await h(update, client)
            except Exception:
                logger.exception("Error while dispatching message")

        async def _on_callback(client: Client, callback_query: Any) -> None:
            data = callback_query.data or ""
            handler = callback_router.route(data)
            update = SimpleNamespace(
                user_id=(callback_query.from_user.id if callback_query.from_user else None),
                chat_id=(callback_query.message.chat.id if callback_query.message and callback_query.message.chat else None),
                data=data,
                callback_query=callback_query,
            )
            if handler is None:
                try:
                    await callback_query.answer("غير معروف", show_alert=False)
                except Exception:
                    logger.exception("Failed to answer unknown callback")
                return
            try:
                await handler(update, client)
            except Exception:
                logger.exception("Error while handling callback %s", data)

        # register with pyrogram
        self.client.add_handler(MessageHandler(_on_message, filters=filters.text))
        self.client.add_handler(CallbackQueryHandler(_on_callback))

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

    async def send_text(self, chat_id: int, text: str, **kwargs) -> Any:
        """Send a text message with basic FloodWait handling."""
        if not self.client:
            raise RuntimeError("Client not initialized")
        attempts = 0
        while True:
            try:
                return await self.client.send_message(chat_id, text, **kwargs)
            except FloodWait as fw:
                wait = int(fw.x) + 1
                logger.warning("FloodWait for %s seconds, sleeping", wait)
                await asyncio.sleep(wait)
                attempts += 1
                if attempts > 3:
                    logger.error("Too many FloodWait retries")
                    raise
            except RPCError:
                logger.exception("RPCError while sending message to %s", chat_id)
                raise
