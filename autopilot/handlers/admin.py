"""Admin handlers placeholder."""
from __future__ import annotations

from ..router import router


async def admin_handler(update, context):
    return None


def register() -> None:
    router.add_handler("admin", admin_handler)
