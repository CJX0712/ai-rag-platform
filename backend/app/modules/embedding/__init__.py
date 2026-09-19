"""Embedding module: provider-agnostic text -> vector."""
from app.modules.embedding.client import (
    Embedder,
    MockEmbedder,
    OllamaEmbedder,
    OpenAIEmbedder,
    build_embedder,
)

__all__ = [
    "Embedder",
    "OllamaEmbedder",
    "OpenAIEmbedder",
    "MockEmbedder",
    "build_embedder",
]
