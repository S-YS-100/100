"""Developer utilities handlers placeholder."""
from __future__ import annotations

from ..router import router


async def developer_handler(update, context):
    return None


def register() -> None:
    router.add_handler("developer", developer_handler)
