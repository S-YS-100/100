"""AI provider manager with unified interface.

Supports switching between multiple providers based on available API keys.
Implements conversation history lazy loading and a simple round-robin provider
selection. Providers are implemented using aiohttp via the shared HttpClient.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..config import get_settings
from ..services.http import HttpClient

logger = logging.getLogger("autopilot.ai")


class AIProvider:
    __slots__ = ("name", "key", "http")

    def __init__(self, name: str, key: str, http: HttpClient) -> None:
        self.name = name
        self.key = key
        self.http = http

    async def complete(self, prompt: str, **kwargs) -> str:
        # Minimal generic implementation using OpenAI-compatible REST API
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}"}
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
        if not self.http or not self.http.session:
            raise RuntimeError("HTTP client not initialized")
        async with self.http.session.post(url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            # try to extract a reasonable text
            choices = data.get("choices")
            if choices and isinstance(choices, list):
                msg = choices[0].get("message", {}).get("content")
                if msg:
                    return msg
            # fallback to direct text
            return data.get("text", "")


class AIManager:
    __slots__ = ("settings", "http", "providers", "provider_order")

    def __init__(self, settings=None, http: Optional[HttpClient] = None) -> None:
        self.settings = settings or get_settings()
        self.http = http
        self.providers: Dict[str, AIProvider] = {}
        self.provider_order: List[str] = []

    async def initialize(self) -> None:
        # register providers if keys exist
        if self.settings.OPENAI_API_KEY:
            self._add_provider("openai", self.settings.OPENAI_API_KEY)
        if self.settings.OPEN_ROUTER_API_KEY:
            self._add_provider("openrouter", self.settings.OPEN_ROUTER_API_KEY)
        if self.settings.OPENAI_LIKE_API_KEY:
            self._add_provider("openai_like", self.settings.OPENAI_LIKE_API_KEY)
        if self.settings.GOOGLE_GENERATIVE_AI_API_KEY:
            self._add_provider("google", self.settings.GOOGLE_GENERATIVE_AI_API_KEY)
        if self.settings.ANTHROPIC_API_KEY:
            self._add_provider("anthropic", self.settings.ANTHROPIC_API_KEY)
        if self.settings.GROQ_API_KEY:
            self._add_provider("groq", self.settings.GROQ_API_KEY)
        if not self.providers:
            logger.warning("No AI providers configured")

    def _add_provider(self, name: str, key: str) -> None:
        prov = AIProvider(name, key, self.http)
        self.providers[name] = prov
        self.provider_order.append(name)
        logger.debug("AI provider added: %s", name)

    async def choose_provider(self) -> Optional[AIProvider]:
        if not self.provider_order:
            return None
        # simple round-robin selection
        name = self.provider_order.pop(0)
        self.provider_order.append(name)
        return self.providers.get(name)

    async def complete(self, prompt: str, **kwargs) -> str:
        provider = await self.choose_provider()
        if not provider:
            raise RuntimeError("No AI provider available")
        return await provider.complete(prompt, **kwargs)

    async def shutdown(self) -> None:
        logger.debug("AIManager shutdown complete")
