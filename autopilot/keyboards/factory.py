"""Keyboard factory for building Telegram keyboard payloads.

Provides helpers for inline and reply keyboards, pagination, dynamic buttons
and standard back buttons. Returns Python dicts suitable for Pyrogram's
reply_markup parameter.
"""
from __future__ import annotations

from typing import Any, List, Optional


class KeyboardFactory:
    __slots__ = ()

    @staticmethod
    def inline(rows: List[List[dict[str, Any]]]) -> dict:
        return {"inline_keyboard": rows}

    @staticmethod
    def reply(rows: List[List[dict[str, Any]]]) -> dict:
        return {"keyboard": rows, "resize_keyboard": True}

    @staticmethod
    def button(text: str, callback_data: Optional[str] = None, url: Optional[str] = None) -> dict:
        btn: dict[str, Any] = {"text": text}
        if callback_data is not None:
            btn["callback_data"] = callback_data
        if url is not None:
            btn["url"] = url
        return btn

    @staticmethod
    def back_button(prefix: str = "back") -> dict:
        return KeyboardFactory.button("Back", callback_data=f"{prefix}:home")

    @staticmethod
    def paginate(items: List[dict], page: int, per_page: int, prefix: str) -> dict:
        start = page * per_page
        chunk = items[start : start + per_page]
        rows: List[List[dict[str, Any]]] = []
        for item in chunk:
            rows.append([KeyboardFactory.button(item["text"], callback_data=f"{prefix}:{item.get('id', item['text'])}")])
        nav: List[dict[str, Any]] = []
        if page > 0:
            nav.append(KeyboardFactory.button("Prev", callback_data=f"{prefix}:page:{page-1}"))
        nav.append(KeyboardFactory.button("Home", callback_data=f"{prefix}:home"))
        # no next calculation here, handler can compute
        rows.append(nav)
        return KeyboardFactory.inline(rows)
