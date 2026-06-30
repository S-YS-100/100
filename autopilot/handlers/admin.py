"""Admin handlers such as broadcast and statistics.

These handlers are owner-only and will validate the OWNER_ID before executing.
They use the Application context to access repositories and services.
"""
from __future__ import annotations

import logging
from typing import Any

from ..router import router
from ..config import get_settings
from ..context import app

logger = logging.getLogger("autopilot.handlers.admin")


async def broadcast_handler(update: Any, client: Any) -> None:
    settings = get_settings()
    uid = update.user_id
    if int(uid) != int(settings.OWNER_ID):
        await client.send_message(update.chat_id, "You are not authorized to run this command.")
        return
    # parse message to broadcast
    text = (update.text or "").strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await client.send_message(update.chat_id, "Usage: /broadcast <message>")
        return
    message = parts[1]
    # fetch all users via repository
    try:
        user_repo = app.db and __import__("autopilot.database.repositories", fromlist=["UserRepository"]).UserRepository(app.db)
        users = await user_repo.list(limit=10000)
        sent = 0
        for u in users:
            try:
                await app.telegram.send_text(u.user_id, message)
                sent += 1
            except Exception:
                logger.exception("Failed to send broadcast to %s", u.user_id)
        await client.send_message(update.chat_id, f"Broadcast sent to {sent} users.")
    except Exception:
        logger.exception("Broadcast failed")
        await client.send_message(update.chat_id, "Broadcast failed. See logs.")


def register() -> None:
    router.add_handler("broadcast", broadcast_handler)
