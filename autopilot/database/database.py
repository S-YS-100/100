"""Database connection and session management using SQLAlchemy Async and asyncpg.

This module exposes an AsyncEngine and a session factory. It also provides a
convenient async context manager `get_session()` which yields an AsyncSession.

Connections are pooled by SQLAlchemy/asyncpg and should be reused across the
application lifetime.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..config import get_settings

logger = logging.getLogger("autopilot.database")

_engine: Optional[AsyncEngine] = None
_Session: Optional[sessionmaker] = None


async def init_db(settings=None) -> None:
    """Initialize the global engine and session factory.

    This function is idempotent and safe to call multiple times.
    """
    global _engine, _Session
    settings = settings or get_settings()
    database_url = settings.DATABASE_URL
    if not database_url:
        logger.info("DATABASE_URL not provided; skipping DB initialization")
        return

    if _engine is not None:
        return

    # Expect DATABASE_URL to be in the form compatible with SQLAlchemy asyncpg:
    # postgresql+asyncpg://user:pass@host:port/dbname
    _engine = create_async_engine(database_url, echo=False, future=True)
    _Session = sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    logger.info("Initialized database engine")


async def close_db() -> None:
    global _engine
    if _engine is None:
        return
    await _engine.dispose()
    _engine = None


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session. Caller must `await` the context manager.

    Example:
        async with get_session() as session:
            await session.execute(...)
    """
    global _Session
    if _Session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session: AsyncSession
    async with _Session() as session:
        try:
            yield session
        finally:
            # session is closed by context manager; nothing else required.
            pass
