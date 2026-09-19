"""Shared fixtures. Inject mock providers so the full chain runs offline."""
import pytest

from app.api import router as router_mod
from app.modules.embedding.client import MockEmbedder
from app.modules.llm_gateway.gateway import MockBackend
from app.modules.rag.orchestrator import RAGOrchestrator
from app.modules.retrieval.service import Retriever
from app.modules.vectorstore.client import QdrantStore


@pytest.fixture
def rag_stack():
    embedder = MockEmbedder(dim=16)
    store = QdrantStore()  # in-memory
    retriever = Retriever(embedder, store)
    rag = RAGOrchestrator(retriever, MockBackend())
    # inject into the API layer
    router_mod._embedder = embedder
    router_mod._store = store
    router_mod._retriever = retriever
    router_mod._llm = rag.llm
    router_mod._rag = rag
    yield rag
    # reset so other tests start clean
    router_mod._embedder = None
    router_mod._store = None
    router_mod._retriever = None
    router_mod._llm = None
    router_mod._rag = None


@pytest.fixture
def client(rag_stack):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
