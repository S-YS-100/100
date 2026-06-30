"""Entry point for the autopilot package.

Runs the asynchronous application.
"""
import asyncio

from .app import main

if __name__ == "__main__":
    asyncio.run(main())
