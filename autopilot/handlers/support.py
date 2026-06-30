"""Support handlers placeholder."""
from __future__ import annotations

from ..router import router


async def support_handler(update, context):
    return None


def register() -> None:
    router.add_handler("support", support_handler)
