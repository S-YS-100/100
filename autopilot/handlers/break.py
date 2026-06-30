"""Break handlers placeholder."""
from __future__ import annotations

from ..router import router


async def break_handler(update, context):
    return None


def register() -> None:
    router.add_handler("break", break_handler)
