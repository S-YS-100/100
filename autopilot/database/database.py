"""Database manager using asyncpg pool and SQLAlchemy async engine.

Provides connection pooling, simple retry logic, ORM initialization and a
session context manager for use throughout the application.
"""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncpg

from ..config import Settings
from . import models

logger = logging.getLogger("autopilot.database")


class DatabaseManager:
    __slots__ = ("settings", "_engine", "_Session", "_pool")

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._engine: Optional[AsyncEngine] = None
        self._Session: Optional[sessionmaker] = None
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self, retries: int = 3, delay: float = 2.0) -> None:
        database_url = self.settings.DATABASE_URL
        if not database_url:
            raise RuntimeError("DATABASE_URL must be set")

        last_exc: Optional[Exception] = None
        for attempt in range(1, retries + 1):
            try:
                # create asyncpg pool for non-ORM operations
                self._pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=10)
                # create SQLAlchemy async engine
                self._engine = create_async_engine(database_url, echo=False, future=True)
                self._Session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)
                logger.info("Connected to database")
                return
            except Exception as exc:
                last_exc = exc
                logger.warning("Database connection attempt %d failed: %s", attempt, exc)
                await asyncio.sleep(delay * attempt)
        raise last_exc  # type: ignore

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
        logger.info("Database connections closed")

    async def test_connection(self) -> None:
        if self._pool is None:
            raise RuntimeError("Database pool not initialized")
        async with self._pool.acquire() as conn:
            await conn.fetchrow("SELECT 1 AS test")
        logger.debug("Database test query succeeded")

    async def init_orm(self) -> None:
        # Create tables if they don't exist (use SQLAlchemy metadata create)
        if self._engine is None:
            raise RuntimeError("Engine not initialized")
        async with self._engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        logger.debug("ORM initialization complete")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._Session is None:
            raise RuntimeError("Database not initialized")
        async with self._Session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def acquire_raw(self):
        if self._pool is None:
            raise RuntimeError("Pool not initialized")
        return await self._pool.acquire()

