"""Embedding client with pluggable providers.

An ``Embedder`` exposes a single async ``embed(texts)`` returning a list of
equal-length float vectors. Three implementations ship: Ollama (local),
OpenAI-compatible (cloud), and a deterministic Mock used for tests/demos.
"""
import hashlib
import json
from abc import ABC, abstractmethod
from typing import List

import httpx

from app.core.config import get_settings


class Embedder(ABC):
    dim: int = 0

    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        ...


class OllamaEmbedder(Embedder):
    def __init__(self, base_url: str, model: str, dim: int = 768):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.dim = dim

    async def embed(self, texts: List[str]) -> List[List[float]]:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": texts},
            )
            r.raise_for_status()
            return [vec for vec in r.json()["embeddings"]]


class OpenAIEmbedder(Embedder):
    def __init__(self, base_url: str, model: str, api_key: str | None, dim: int):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.dim = dim

    async def embed(self, texts: List[str]) -> List[List[float]]:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json={"model": self.model, "input": texts},
            )
            r.raise_for_status()
            return [d["embedding"] for d in r.json()["data"]]


class MockEmbedder(Embedder):
    """Deterministic hash-based embedder for offline tests and demos."""

    def __init__(self, dim: int = 768):
        self.dim = dim

    async def embed(self, texts: List[str]) -> List[List[float]]:
        out: List[List[float]] = []
        for t in texts:
            vec = []
            for i in range(self.dim):
                h = hashlib.md5(f"{t}::{i}".encode()).digest()
                val = (int.from_bytes(h[:4], "big") / 2 ** 32) * 2 - 1
                vec.append(round(val, 6))
            out.append(vec)
        return out


def build_embedder(settings=None) -> Embedder:
    settings = settings or get_settings()
    provider = settings.EMBEDDING_PROVIDER
    if provider == "ollama":
        return OllamaEmbedder(
            settings.OLLAMA_BASE_URL, settings.EMBEDDING_MODEL, settings.VECTOR_SIZE
        )
    if provider == "openai":
        dim = 1536 if "3-small" in settings.OPENAI_EMBED_MODEL else settings.VECTOR_SIZE
        return OpenAIEmbedder(
            settings.OPENAI_EMBED_BASE_URL,
            settings.OPENAI_EMBED_MODEL,
            settings.OPENAI_API_KEY,
            dim,
        )
    return MockEmbedder(settings.VECTOR_SIZE)
