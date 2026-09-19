"""Retrieval service: turns a user query into ranked source documents."""
from typing import List

from app.core.config import get_settings
from app.modules.embedding.client import Embedder
from app.modules.vectorstore.client import QdrantStore
from app.schemas.common import RetrievedDoc


class Retriever:
    def __init__(
        self, embedder: Embedder, store: QdrantStore, settings=None
    ):
        self.embedder = embedder
        self.store = store
        self.settings = settings or get_settings()

    async def retrieve(
        self, query: str, top_k: int | None = None
    ) -> List[RetrievedDoc]:
        k = top_k or self.settings.RETRIEVE_TOP_K
        vector = (await self.embedder.embed([query]))[0]
        hits = self.store.search(vector, top_k=k, score_threshold=self.settings.SCORE_THRESHOLD)
        return [RetrievedDoc(**h) for h in hits]
