"""CallbackQuery router and parser utilities.

At this stage we only provide parsing helpers and a registration API for
future callback-based handlers.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, Match, Optional

CallbackHandler = Callable[..., Any]


class CallbackRouter:
    _pattern: re.Pattern

    def __init__(self, pattern: str = r"^(?P<action>[a-z_]+)(?:\:(?P<data>.+))?$") -> None:
        self._pattern = re.compile(pattern)
        self._handlers: Dict[str, CallbackHandler] = {}

    def register(self, name: str, handler: CallbackHandler) -> None:
        self._handlers[name] = handler

    def parse(self, callback_data: str) -> Optional[Match[str]]:
        return self._pattern.match(callback_data)

    def route(self, callback_data: str) -> Optional[CallbackHandler]:
        m = self.parse(callback_data)
        if not m:
            return None
        action = m.group("action")
        return self._handlers.get(action)


callback_router = CallbackRouter()
