"""History service that lazily loads and stores conversation history.

History is loaded on demand from the HistoryRepository and never cached long
term in memory. After a handler finishes, history references are released.
"""
from __future__ import annotations

from typing import List

from ..database.repositories import HistoryRepository


class HistoryService:
    __slots__ = ("history_repo",)

    def __init__(self, history_repo: HistoryRepository) -> None:
        self.history_repo = history_repo

    async def load_user_history(self, user_id: int) -> List[str]:
        convs = await self.history_repo.find_by_user(user_id)
        # return titles as a simple history representation for now
        return [c.title or "" for c in convs]

    async def save_message(self, user_id: int, message: str) -> None:
        # create a new conversation record for every message (simple model)
        await self.history_repo.create_conversation(user_id, title=message[:200])
