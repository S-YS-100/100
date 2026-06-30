"""Repository implementations providing a layer of data access behind the DAO pattern.

Each repository exposes create/update/delete/find methods and hides SQLAlchemy
session handling inside the repository.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.database import DatabaseManager
from ..database.models import User, Channel, Conversation, Setting, Statistic


class UserRepository:
    __slots__ = ("db",)

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def create(self, user_id: int, username: Optional[str] = None) -> User:
        async with self.db.get_session() as session:
            user = User(user_id=user_id, username=username)
            session.add(user)
            await session.flush()
            return user

    async def find(self, user_id: int) -> Optional[User]:
        async with self.db.get_session() as session:
            q = select(User).where(User.user_id == user_id)
            res = await session.execute(q)
            return res.scalars().first()

    async def update(self, user: User, **fields) -> User:
        async with self.db.get_session() as session:
            for k, v in fields.items():
                setattr(user, k, v)
            session.add(user)
            await session.flush()
            return user

    async def delete(self, user: User) -> None:
        async with self.db.get_session() as session:
            await session.delete(user)

    async def exists(self, user_id: int) -> bool:
        return (await self.find(user_id)) is not None

    async def list(self, limit: int = 100, offset: int = 0) -> List[User]:
        async with self.db.get_session() as session:
            q = select(User).limit(limit).offset(offset)
            res = await session.execute(q)
            return res.scalars().all()


class ChannelRepository:
    __slots__ = ("db",)

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def create(self, chat_id: int, title: Optional[str] = None) -> Channel:
        async with self.db.get_session() as session:
            ch = Channel(chat_id=chat_id, title=title)
            session.add(ch)
            await session.flush()
            return ch

    async def find(self, chat_id: int) -> Optional[Channel]:
        async with self.db.get_session() as session:
            q = select(Channel).where(Channel.chat_id == chat_id)
            res = await session.execute(q)
            return res.scalars().first()

    async def delete(self, channel: Channel) -> None:
        async with self.db.get_session() as session:
            await session.delete(channel)

    async def exists(self, chat_id: int) -> bool:
        return (await self.find(chat_id)) is not None


class HistoryRepository:
    __slots__ = ("db",)

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def create_conversation(self, user_id: int, title: Optional[str] = None) -> Conversation:
        async with self.db.get_session() as session:
            conv = Conversation(user_id=user_id, title=title)
            session.add(conv)
            await session.flush()
            return conv

    async def find_by_user(self, user_id: int) -> List[Conversation]:
        async with self.db.get_session() as session:
            q = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc())
            res = await session.execute(q)
            return res.scalars().all()


class SettingsRepository:
    __slots__ = ("db",)

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def set(self, key: str, value: str) -> Setting:
        async with self.db.get_session() as session:
            q = select(Setting).where(Setting.key == key)
            res = await session.execute(q)
            existing = res.scalars().first()
            if existing:
                existing.value = value
                session.add(existing)
                await session.flush()
                return existing
            s = Setting(key=key, value=value)
            session.add(s)
            await session.flush()
            return s

    async def get(self, key: str) -> Optional[Setting]:
        async with self.db.get_session() as session:
            q = select(Setting).where(Setting.key == key)
            res = await session.execute(q)
            return res.scalars().first()


class StatisticsRepository:
    __slots__ = ("db",)

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    async def increment(self, key: str, amount: int = 1) -> Statistic:
        async with self.db.get_session() as session:
            q = select(Statistic).where(Statistic.key == key)
            res = await session.execute(q)
            stat = res.scalars().first()
            if not stat:
                stat = Statistic(key=key, value=amount)
                session.add(stat)
            else:
                stat.value += amount
                session.add(stat)
            await session.flush()
            return stat
