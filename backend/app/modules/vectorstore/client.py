"""Qdrant-backed vector store.

Uses an in-process ``:memory:`` client when neither QDRANT_URL nor
QDRANT_HOST is configured, so the backend runs with zero external services.
The collection is created lazily on first upsert, with its dimension inferred
from the first vector - no need to pre-declare it.
"""
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import get_settings


class QdrantStore:
    def __init__(self, settings=None):
        settings = settings or get_settings()
        self.collection = settings.QDRANT_COLLECTION
        if settings.QDRANT_URL:
            self.client = QdrantClient(
                url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
            )
        elif settings.QDRANT_HOST:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
                api_key=settings.QDRANT_API_KEY,
            )
        else:
            self.client = QdrantClient(location=":memory:")

    def _ensure(self, dim: int) -> None:
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=dim, distance=Distance.COSINE
                ),
            )

    def upsert(self, points: List[PointStruct]) -> int:
        if not points:
            return 0
        dim = len(points[0].vector)
        self._ensure(dim)
        self.client.upsert(collection_name=self.collection, points=points)
        return len(points)

    def search(
        self, vector, top_k: int = 5, score_threshold: Optional[float] = None
    ) -> List[dict]:
        if not self.client.collection_exists(self.collection):
            return []
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            score_threshold=score_threshold,
        )
        return [
            {
                "text": h.payload.get("text", ""),
                "source": h.payload.get("source", ""),
                "score": float(h.score),
                "metadata": h.payload.get("metadata", {}),
            }
            for h in hits
        ]

    def count(self) -> int:
        if not self.client.collection_exists(self.collection):
            return 0
        return self.client.count(self.collection).count

    def clear(self) -> None:
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
