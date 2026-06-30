"""Start command handler placeholder."""
from __future__ import annotations

from ..router import router


async def start_handler(update, context):
    """Placeholder async start handler."""
    # Real implementation will interact with database and services.
    return None


def register() -> None:
    router.add_handler("start", start_handler)
