import uuid

import pytest
from qdrant_client.models import PointStruct

from app.modules.ingestion.service import prepare_document


@pytest.mark.asyncio
async def test_ingest_retrieve_ask(rag_stack):
    resp, chunks = prepare_document(
        "kb.txt", "RAG 是检索增强生成技术。它先检索知识再生成答案。".encode("utf-8")
    )
    assert resp.chunks >= 1
    assert chunks

    vecs = await rag_stack.retriever.embedder.embed([c.text for c in chunks])
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=v,
            payload={"text": c.text, "source": c.source, "metadata": c.metadata},
        )
        for c, v in zip(chunks, vecs)
    ]
    rag_stack.retriever.store.upsert(points)

    docs = await rag_stack.retriever.retrieve("什么是 RAG")
    assert len(docs) >= 1

    events = [e async for e in rag_stack.ask("什么是 RAG？")]
    types = [e["type"] for e in events]
    assert "sources" in types
    assert "token" in types
    assert "done" in types
