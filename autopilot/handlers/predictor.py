"""Predictor handlers placeholder."""
from __future__ import annotations

from ..router import router


async def predictor_handler(update, context):
    return None


def register() -> None:
    router.add_handler("predictor", predictor_handler)
