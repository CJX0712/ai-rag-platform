"""Offline smoke test: runs the full RAG chain with mock providers.

    python smoke.py

Proves ingestion -> embedding -> vector store -> retrieval -> LLM streaming
works end-to-end without any external service (Ollama / Qdrant / cloud API).
"""
import asyncio
import uuid

from qdrant_client.models import PointStruct

from app.modules.embedding.client import MockEmbedder
from app.modules.ingestion.service import prepare_document
from app.modules.llm_gateway.gateway import MockBackend
from app.modules.rag.orchestrator import RAGOrchestrator
from app.modules.retrieval.service import Retriever
from app.modules.vectorstore.client import QdrantStore


async def main():
    store = QdrantStore()  # in-memory
    embedder = MockEmbedder(dim=16)
    retriever = Retriever(embedder, store)
    rag = RAGOrchestrator(retriever, MockBackend())

    _, chunks = prepare_document(
        "demo.txt", "RAG 结合检索与生成。知识库检索提升回答准确性。".encode("utf-8")
    )
    vecs = await embedder.embed([c.text for c in chunks])
    store.upsert(
        [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=v,
                payload={"text": c.text, "source": c.source, "metadata": c.metadata},
            )
            for c, v in zip(chunks, vecs)
        ]
    )
    print(f"[smoke] ingested {len(chunks)} chunks")

    events = [e async for e in rag.ask("RAG 有什么用？")]
    for e in events:
        if e["type"] == "sources":
            print(f"[smoke] sources: {len(e['sources'])}")
        elif e["type"] == "token":
            print(e["text"], end="", flush=True)
        elif e["type"] == "done":
            print(f"\n[smoke] done session={e['session_id']}")
    print("[smoke] OK - full chain executed offline")


if __name__ == "__main__":
    asyncio.run(main())
