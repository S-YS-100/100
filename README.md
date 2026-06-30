"""README with instructions and architecture overview updated for the implementation."""

# autopilot

Enterprise-grade Telegram bot scaffolded for Python 3.12. This repository
contains an async-first architecture, SQLAlchemy Async database integration,
structured logging and a clear module separation for handlers, services, and
database access.

## Running

1. Copy `.env.example` to `.env` and set required variables (TOKEN, OWNER_ID, DATABASE_URL, LOG_LEVEL, etc.)
2. Install dependencies: `pip install -r requirements.txt`
3. Start: `python -m autopilot`

## Architecture

- Application orchestrator: `autopilot.core.Application`
- Database manager: `autopilot.database.database.DatabaseManager`
- Repositories: `autopilot.database.repositories`
- Services: HTTP, Cache, AI, Telegram, Images
- Handler auto-discovery: `autopilot.handlers.loader`
