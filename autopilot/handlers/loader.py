"""Automatic handler loader invoked during application startup.

The loader imports every module in autopilot.handlers and calls its register()
callable if present. Handlers should register with the central router.
"""
from __future__ import annotations

import importlib
import pkgutil
import logging
import inspect
from typing import List

logger = logging.getLogger("autopilot.handlers.loader")


async def load_handlers() -> List[str]:
    pkg = "autopilot.handlers"
    package = importlib.import_module(pkg)
    package_path = package.__path__
    loaded: List[str] = []
    for finder, name, ispkg in pkgutil.iter_modules(package_path):
        full_name = f"{pkg}.{name}"
        try:
            module = importlib.import_module(full_name)
        except Exception:
            logger.exception("Failed to import handler %s", full_name)
            continue
        if hasattr(module, "register"):
            try:
                func = getattr(module, "register")
                if inspect.iscoroutinefunction(func):
                    await func()
                else:
                    func()
                loaded.append(full_name)
                logger.debug("Loaded handler %s", full_name)
            except Exception:
                logger.exception("Failed to register handler %s", full_name)
    return loaded
