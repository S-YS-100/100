"""Updates handlers placeholder."""
from __future__ import annotations

from ..router import router


async def updates_handler(update, context):
    return None


def register() -> None:
    router.add_handler("updates", updates_handler)
