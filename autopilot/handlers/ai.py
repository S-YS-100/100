"""AI message handler.

Handles messages beginning with /ai and forwards them to the AIManager.
The response is sent back to the user and persisted in conversation history.
"""
from __future__ import annotations

import logging
from typing import Any

from ..router import router
from ..context import app

logger = logging.getLogger("autopilot.handlers.ai")


async def ai_handler(update: Any, client: Any) -> None:
    text = (update.text or "").strip()
    if not text:
        return
    # remove command prefix if present
    if text.startswith("/ai"):
        prompt = text[3:].strip()
    else:
        prompt = text
    if not prompt:
        await client.send_message(update.chat_id, "Please provide a prompt after /ai")
        return
    try:
        ai = app.ai
        if ai is None:
            await client.send_message(update.chat_id, "AI service is not available.")
            return
        # Lazy load history
        history = []
        if app.db:
            history_repo = __import__("autopilot.database.repositories", fromlist=["HistoryRepository"]).HistoryRepository(app.db)
            recent = await history_repo.find_by_user(update.user_id)
            # build a compact prompt from recent conversation titles
            history = [c.title for c in recent if c.title]
        prompt_with_history = "\n".join(history[-5:] + [prompt]) if history else prompt
        response = await ai.complete(prompt_with_history)
        # send response
        await client.send_message(update.chat_id, response)
        # persist in history
        if app.db:
            await history_repo.create_conversation(update.user_id, title=(prompt[:200] + " -> " + (response[:200] if response else "")))
    except Exception:
        logger.exception("AI handler failed")
        await client.send_message(update.chat_id, "AI request failed. Try again later.")


def register() -> None:
    router.add_handler("ai", ai_handler)
