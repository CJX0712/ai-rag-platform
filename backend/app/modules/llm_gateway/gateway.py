"""LLM gateway with streaming backends.

A ``LLMBackend`` exposes an async ``stream(messages, ...)`` generator that
yields text deltas. Three implementations: Ollama (local), OpenAI-compatible
(cloud), and Mock (offline demo).
"""
import json
from abc import ABC, abstractmethod
from typing import AsyncIterator, List

import httpx

from app.core.config import get_settings


class LLMBackend(ABC):
    @abstractmethod
    def stream(
        self, messages: List[dict], temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        ...


class OllamaBackend(LLMBackend):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def stream(self, messages, temperature, max_tokens):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        async with httpx.AsyncClient(timeout=180) as client:
            async with client.stream(
                "POST", f"{self.base_url}/api/chat", json=payload
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    delta = obj.get("message", {}).get("content", "")
                    if delta:
                        yield delta


class OpenAIBackend(LLMBackend):
    def __init__(self, base_url: str, model: str, api_key: str | None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    async def stream(self, messages, temperature, max_tokens):
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        headers["Content-Type"] = "application/json"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=180) as client:
            async with client.stream(
                "POST", f"{self.base_url}/chat/completions", headers=headers, json=payload
            ) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:"):].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                    except Exception:
                        continue
                    delta = obj["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta


class MockBackend(LLMBackend):
    """Echo-style backend so the full chain runs without a model server."""

    async def stream(self, messages, temperature, max_tokens):
        user_q = ""
        for m in messages:
            if m["role"] == "user":
                user_q = m["content"]
        answer = (
            "[DEMO] 已基于检索上下文组织答案。\n"
            f"针对问题「{user_q}」，知识库返回了相关片段（见 sources 事件）。\n"
            "当前为 Mock 模式：切换 EMBEDDING_PROVIDER/LLM_PROVIDER 为 ollama 或 "
            "openai 即可获得真实向量化与生成能力。"
        )
        for ch in answer:
            yield ch


def build_llm(settings=None) -> LLMBackend:
    settings = settings or get_settings()
    provider = settings.LLM_PROVIDER
    if provider == "ollama":
        return OllamaBackend(settings.OLLAMA_BASE_URL, settings.LLM_MODEL)
    if provider == "openai":
        base = settings.LLM_BASE_URL or "https://api.openai.com/v1"
        return OpenAIBackend(base, settings.LLM_MODEL, settings.LLM_API_KEY)
    return MockBackend()
