"""Telegram service abstractions and lazy client factory.

We intentionally avoid importing any Telegram client libraries at module import
time. The real client will be created lazily at runtime when required.
"""
from __future__ import annotations

from typing import Any, Optional


class TelegramClientFactory:
    """Factory that produces Telegram client instances lazily.

    Concrete implementations will be added in the feature stage. This abstraction
    prevents top-level imports of pyrogram/aiogram and keeps startup lightweight.
    """

    async def create(self) -> Any:
        """Create and return an async Telegram client.

        Should be implemented to return a client configured with credentials from
        the settings object.
        """
        raise NotImplementedError
