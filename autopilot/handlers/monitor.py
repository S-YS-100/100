"""Monitor handlers placeholder."""
from __future__ import annotations

from ..router import router


async def monitor_handler(update, context):
    return None


def register() -> None:
    router.add_handler("monitor", monitor_handler)
