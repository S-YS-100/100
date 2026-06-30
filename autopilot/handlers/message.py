"""Generic message handler: registers users and stores lightweight statistics."""
from __future__ import annotations

import logging
from typing import Any

from ..router import router
from ..context import app

logger = logging.getLogger("autopilot.handlers.message")


async def message_handler(update: Any, client: Any) -> None:
    try:
        if app and app.db:
            user_repo = __import__("autopilot.database.repositories", fromlist=["UserRepository"]).UserRepository(app.db)
            existing = await user_repo.find(update.user_id)
            if not existing:
                await user_repo.create(update.user_id, username=getattr(update.message.from_user, "username", None) if update.message and getattr(update.message, "from_user", None) else None)
        # track simple statistic
        if app and app.db:
            stats_repo = __import__("autopilot.database.repositories", fromlist=["StatisticsRepository"]).StatisticsRepository(app.db)
            await stats_repo.increment("messages_received", 1)
    except Exception:
        logger.exception("Failed in generic message handler")


def register() -> None:
    router.add_handler("message", message_handler)
