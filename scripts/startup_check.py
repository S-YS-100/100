"""Startup validation script to check environment, DB, HTTP and Telegram connectivity.

This script is intended to run in CI or as a dry-run check before starting the
bot in production. It will exit with code 0 on success.
"""
from __future__ import annotations

import asyncio
import sys

from autopilot.config import get_settings
from autopilot.database.database import DatabaseManager
from autopilot.services.http import HttpClient
from autopilot.services.telegram.client import TelegramService


async def main() -> int:
    settings = get_settings()
    db = DatabaseManager(settings)
    # DB connect
    try:
        await db.connect()
        await db.test_connection()
        await db.init_orm()
    except Exception as exc:
        print("Database check failed:", exc, file=sys.stderr)
        return 2
    # HTTP
    http = HttpClient()
    await http.__aenter__()
    try:
        await http.ping()
    except Exception as exc:
        print("HTTP check failed:", exc, file=sys.stderr)
        await http.__aexit__(None, None, None)
        return 3
    # Telegram
    tg = TelegramService(settings, db, None)
    try:
        await tg.initialize()
        await tg.test_authorization()
        await tg.shutdown()
    except Exception as exc:
        print("Telegram check failed:", exc, file=sys.stderr)
        await http.__aexit__(None, None, None)
        return 4
    await http.__aexit__(None, None, None)
    await db.close()
    print("Startup check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
