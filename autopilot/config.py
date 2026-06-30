"""Configuration and environment settings for autopilot.

Uses Pydantic BaseSettings to centralize environment handling and provide typed
access to configuration values. Secrets are loaded from an .env file when
present.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment.

    All secrets and environment-specific values should be accessed through an
    instance of this class.
    """

    # Bot / Telegram
    TOKEN: Optional[str] = Field(None, description="Telegram bot token")
    OWNER_ID: Optional[int] = Field(None, description="Bot owner user id")

    # Database
    DATABASE_URL: Optional[str] = Field(None, description="Async PG database url")

    # Third-party APIs
    OPENAI_API_KEY: Optional[str] = None
    OPEN_ROUTER_API_KEY: Optional[str] = None
    GOOGLE_GENERATIVE_AI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENAI_LIKE_API_KEY: Optional[str] = None

    # Infrastructure
    REDIS_URL: Optional[str] = None
    RAILWAY_ENVIRONMENT: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using lru_cache avoids re-parsing the environment multiple times and keeps
    a single canonical configuration object across the process lifetime.
    """
    return Settings()
