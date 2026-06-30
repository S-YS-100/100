"""Gifts handlers placeholder."""
from __future__ import annotations

from ..router import router


async def gifts_handler(update, context):
    return None


def register() -> None:
    router.add_handler("gifts", gifts_handler)
