"""Central application object and lifecycle management.

This Application class is responsible for initializing configuration, logging,
HTTP client, cache, database, ORM, AI providers, Telegram client and loading
handlers/middlewares/callback routers. All lifecycle hooks are asynchronous
and safe to call from `python -m autopilot`.
"""
from __future__ import annotations

import asyncio
import importlib
import inspect
import logging
import os
import pkgutil
import signal
import sys
import time
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional

from .config import get_settings, Settings
from .logging import configure_logging
from .database.database import DatabaseManager
from .services.http import HttpClient
from .services.cache import CacheService
from .services.ai.manager import AIManager
from .services.telegram.client import TelegramService
from .handlers.loader import load_handlers
from .callbacks import callback_router
from .router import router

logger = logging.getLogger("autopilot.core")


class Application:
    __slots__ = (
        "settings",
        "db",
        "http",
        "cache",
        "ai",
        "telegram",
        "loop",
        "stop_event",
        "handler_modules",
    )

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.db: Optional[DatabaseManager] = DatabaseManager(self.settings)
        self.http: Optional[HttpClient] = None
        self.cache: Optional[CacheService] = None
        self.ai: Optional[AIManager] = None
        self.telegram: Optional[TelegramService] = None
        self.loop = asyncio.get_event_loop()
        self.stop_event = asyncio.Event()
        self.handler_modules: List[ModuleType] = []

    async def _init_logging(self) -> None:
        configure_logging(self.settings)
        logging.getLogger(__name__).debug("Logging initialized")

    async def _init_http(self) -> None:
        self.http = HttpClient()
        await self.http.__aenter__()
        logging.getLogger(__name__).debug("HTTP client initialized")

    async def _init_cache(self) -> None:
        self.cache = CacheService(self.settings)
        await self.cache.connect()
        logging.getLogger(__name__).debug("Cache initialized")

    async def _init_ai(self) -> None:
        self.ai = AIManager(self.settings, http=self.http)
        await self.ai.initialize()
        logging.getLogger(__name__).debug("AI manager initialized")

    async def _init_db(self) -> None:
        await self.db.connect()
        await self.db.init_orm()
        logging.getLogger(__name__).debug("Database initialized")

    async def _init_telegram(self) -> None:
        self.telegram = TelegramService(self.settings, self.db, self.cache)
        await self.telegram.initialize()
        logging.getLogger(__name__).debug("Telegram service initialized")

    async def _discover_handlers(self) -> None:
        try:
            loaded = await load_handlers()
            self.handler_modules = [importlib.import_module(m) for m in loaded]
            logger.info("Loaded %d handler modules", len(loaded))
        except Exception:
            logger.exception("Error discovering handlers")

    async def _validate_startup(self) -> None:
        # Environment already validated by config; verify DB, HTTP, Telegram auth
        await self.db.test_connection()
        await self.http.ping()
        await self.telegram.test_authorization()

    async def start(self) -> None:
        start = time.time()
        await self._init_logging()
        await self._init_http()
        await self._init_cache()
        await self._init_db()
        await self._init_ai()
        await self._init_telegram()
        # discover and register handlers
        await self._discover_handlers()
        # register signals
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                self.loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self.stop()))
            except NotImplementedError:
                # signals not supported on Windows event loop
                pass
        # validate critical systems
        await self._validate_startup()
        logger.info("autopilot started in %.2fs", time.time() - start)
        # run forever until stop_event set
        await self.stop_event.wait()

    async def stop(self) -> None:
        logger.info("Shutdown requested — closing services")
        # set stop event so start() can return
        self.stop_event.set()
        # Stop telegram
        if self.telegram is not None:
            await self.telegram.shutdown()
        # Close AI
        if self.ai is not None:
            await self.ai.shutdown()
        # Close cache
        if self.cache is not None:
            await self.cache.close()
        # Close HTTP
        if self.http is not None:
            await self.http.__aexit__(None, None, None)
        # Close DB
        if self.db is not None:
            await self.db.close()
        logger.info("Shutdown complete")

    def run(self) -> int:
        try:
            self.loop.run_until_complete(self.start())
            return 0
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received — shutting down")
            self.loop.run_until_complete(self.stop())
            return 0
        except Exception:
            logger.exception("Unhandled exception in app run")
            try:
                self.loop.run_until_complete(self.stop())
            except Exception:
                logger.exception("Error during shutdown")
            return 2


def run_from_cli() -> None:
    app = Application()
    raise SystemExit(app.run())
