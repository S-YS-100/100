"""Application startup and lifecycle management for autopilot.

This module wires together configuration, logging, database and services and exposes
an async `main()` entrypoint which is safe to call from `python -m autopilot`.

No Telegram-specific network clients are started at this stage — that will be done
in feature-specific modules later. This keeps the initial startup lightweight
and safe for environments where secrets or external services are not available.
"""
from __future__ import annotations

import asyncio
import contextlib
import sys
import time
from typing import Any

from .config import get_settings
from .logging import configure_logging
from .database.database import init_db, close_db


async def _startup() -> None:
    settings = get_settings()
    configure_logging(settings)
    # Initialize DB (will be a no-op if DATABASE_URL is not provided)
    await init_db(settings)


async def _shutdown() -> None:
    await close_db()


async def main(argv: list[str] | None = None) -> int:
    """Main async entrypoint for the application.

    Return code follows UNIX conventions: 0 on success.
    """
    argv = argv or sys.argv[1:]
    start = time.time()
    try:
        await _startup()
        # For this stage we don't start the bot — just validate startup sequence.
        # Keep the process alive briefly to surface any async initialization errors.
        await asyncio.sleep(0.1)
        return 0
    except Exception as exc:  # pragma: no cover - top level guard
        # This will already be configured by configure_logging(); keep it simple here.
        print("Fatal startup error:", exc, file=sys.stderr)
        return 2
    finally:
        await _shutdown()
        elapsed = time.time() - start
        print(f"autopilot shutdown (startup took {elapsed:.2f}s)")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
