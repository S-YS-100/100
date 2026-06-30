"""AI handlers placeholder."""
from __future__ import annotations

from ..router import router


async def ai_handler(update, context):
    return None


def register() -> None:
    router.add_handler("ai", ai_handler)
