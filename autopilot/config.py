"""Enhanced configuration using Pydantic BaseSettings with validation.

This module enforces presence of required environment variables and prints a
readable error followed by graceful exit if validation fails.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    TOKEN: str = Field(..., description="Telegram bot token")
    OWNER_ID: int = Field(..., description="Bot owner user id")
    DATABASE_URL: str = Field(..., description="Async PG database url (postgresql+asyncpg://)")

    OPENAI_API_KEY: Optional[str] = Field(None)
    OPEN_ROUTER_API_KEY: Optional[str] = Field(None)
    OPENAI_LIKE_API_KEY: Optional[str] = Field(None)
    GOOGLE_GENERATIVE_AI_API_KEY: Optional[str] = Field(None)
    ANTHROPIC_API_KEY: Optional[str] = Field(None)
    GROQ_API_KEY: Optional[str] = Field(None)

    LOG_LEVEL: str = Field("INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        val = v.upper()
        if val not in allowed:
            raise ValueError("LOG_LEVEL must be one of: %s" % ", ".join(sorted(allowed)))
        return val


@lru_cache()
def get_settings() -> Settings:
    try:
        settings = Settings()
    except Exception as exc:  # pydantic validation error
        print("Failed to load environment configuration:", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    return settings
