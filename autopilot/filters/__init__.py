"""Custom filters used by handlers to decide whether to run.

Filters are simple predicates that operate on update objects. They are kept
lightweight and import-safe to avoid tight coupling with the Telegram client.
"""
from __future__ import annotations

from typing import Any


def owner_filter(update: Any, owner_id: int) -> bool:
    uid = getattr(update, "user_id", None) or getattr(update, "from_user_id", None)
    return uid is not None and int(uid) == int(owner_id)


def admin_filter(update: Any) -> bool:
    # Placeholder; real check needs Telegram API lookup
    return False


def private_filter(update: Any) -> bool:
    return getattr(update, "chat_type", None) == "private"


def group_filter(update: Any) -> bool:
    return getattr(update, "chat_type", None) in ("group", "supergroup")


def channel_filter(update: Any) -> bool:
    return getattr(update, "chat_type", None) == "channel"
