"""DAO layer providing typed database operations.

All database interactions must go through DAO methods to centralize SQL and
transaction handling. This file contains a few core examples and will be
expanded by feature modules in later stages.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_session
from .models import Channel, User


class UserDAO:
    __slots__ = ("_session",)

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user(self, user_id: int, username: Optional[str] = None) -> User:
        user = User(user_id=user_id, username=username)
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_user(self, user_id: int) -> Optional[User]:
        q = select(User).where(User.user_id == user_id)
        result = await self._session.execute(q)
        return result.scalars().first()

    async def update_user(self, user: User, **fields) -> User:
        for k, v in fields.items():
            setattr(user, k, v)
        self._session.add(user)
        await self._session.flush()
        return user

    async def delete_user(self, user: User) -> None:
        await self._session.delete(user)
        await self._session.flush()


class ChannelDAO:
    __slots__ = ("_session",)

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_channel(self, chat_id: int, title: Optional[str] = None) -> Channel:
        ch = Channel(chat_id=chat_id, title=title)
        self._session.add(ch)
        await self._session.flush()
        return ch

    async def get_channel(self, chat_id: int) -> Optional[Channel]:
        q = select(Channel).where(Channel.chat_id == chat_id)
        res = await self._session.execute(q)
        return res.scalars().first()

