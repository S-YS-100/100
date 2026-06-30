"""Utility helpers used across the codebase.

Keep helpers small and focused. Avoid heavy dependencies to ensure import-time
safety.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class UserSession:
    user_id: int
    history: list[str]
    language: str | None
    created_at: float
