"""AI provider adapters for various providers.

Each provider exposes a `.complete(prompt)` coroutine that returns text.
Adapters handle provider-specific request/response formats. They use the
shared HttpClient to perform network calls.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..http import HttpClient

logger = logging.getLogger("autopilot.ai.providers")


class BaseProvider:
    __slots__ = ("name", "key", "http")

    def __init__(self, name: str, key: str, http: HttpClient) -> None:
        self.name = name
        self.key = key
        self.http = http

    async def complete(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError


class OpenAIProvider(BaseProvider):
    async def complete(self, prompt: str, **kwargs) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {"model": kwargs.get("model", "gpt-4o-mini"), "messages": [{"role": "user", "content": prompt}]}
        session = self.http.session
        if session is None:
            raise RuntimeError("HTTP client not initialized")
        async with session.post(url, json=payload, headers=headers, timeout=kwargs.get("timeout", 30)) as resp:
            resp.raise_for_status()
            data = await resp.json()
            choices = data.get("choices")
            if choices and isinstance(choices, list):
                msg = choices[0].get("message", {}).get("content")
                if msg:
                    return msg
            return data.get("text") or ""


class OpenRouterProvider(BaseProvider):
    async def complete(self, prompt: str, **kwargs) -> str:
        url = "https://api.openrouter.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {"model": kwargs.get("model", "gpt-4o-mini"), "messages": [{"role": "user", "content": prompt}]}
        session = self.http.session
        if session is None:
            raise RuntimeError("HTTP client not initialized")
        async with session.post(url, json=payload, headers=headers, timeout=kwargs.get("timeout", 30)) as resp:
            resp.raise_for_status()
            data = await resp.json()
            choices = data.get("choices")
            if choices and isinstance(choices, list):
                msg = choices[0].get("message", {}).get("content")
                if msg:
                    return msg
            return data.get("text") or ""


class AnthropicProvider(BaseProvider):
    async def complete(self, prompt: str, **kwargs) -> str:
        # Anthropic Claude requires a different API shape; implement minimal compatible call
        url = "https://api.anthropic.com/v1/complete"
        headers = {"x-api-key": self.key, "Content-Type": "application/json"}
        payload = {"model": kwargs.get("model", "claude-2"), "prompt": prompt, "max_tokens": kwargs.get("max_tokens", 512)}
        session = self.http.session
        if session is None:
            raise RuntimeError("HTTP client not initialized")
        async with session.post(url, json=payload, headers=headers, timeout=kwargs.get("timeout", 30)) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("completion") or data.get("text") or ""


class GoogleProvider(BaseProvider):
    async def complete(self, prompt: str, **kwargs) -> str:
        # Placeholder minimal implementation for Google Generative API REST
        url = "https://generative.googleapis.com/v1/models/text-bison-001:generate"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {"prompt": {"text": prompt}, "maxOutputTokens": kwargs.get("max_tokens", 512)}
        session = self.http.session
        if session is None:
            raise RuntimeError("HTTP client not initialized")
        async with session.post(url, json=payload, headers=headers, timeout=kwargs.get("timeout", 30)) as resp:
            resp.raise_for_status()
            data = await resp.json()
            candidates = data.get("candidates")
            if candidates and isinstance(candidates, list):
                return candidates[0].get("content", "")
            return data.get("output", "")


class GroqProvider(BaseProvider):
    async def complete(self, prompt: str, **kwargs) -> str:
        url = "https://api.groq.com/v1/complete"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {"prompt": prompt}
        session = self.http.session
        if session is None:
            raise RuntimeError("HTTP client not initialized")
        async with session.post(url, json=payload, headers=headers, timeout=kwargs.get("timeout", 30)) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("text") or ""
