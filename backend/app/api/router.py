"""REST + SSE API router.

Endpoints:
  GET  /api/v1/health    -> service status
  POST /api/v1/documents  -> upload + ingest + embed + store (auth optional)
  POST /api/v1/chat       -> SSE stream of {sources, token, done} events
"""
import json
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.core.security import require_api_key
from app.modules.embedding.client import build_embedder
from app.modules.ingestion.service import prepare_document
from app.modules.llm_gateway.gateway import build_llm
from app.modules.rag.orchestrator import RAGOrchestrator
from app.modules.retrieval.service import Retriever
from app.modules.vectorstore.client import QdrantStore
from app.schemas.common import ChatRequest, HealthResponse, IngestResponse
from qdrant_client.models import PointStruct

router = APIRouter(prefix="/api/v1")
settings = get_settings()

# Lazily-initialised singletons (one per process). Tests override these.
_embedder = None
_store = None
_retriever = None
_llm = None
_rag = None


def _get_rag() -> RAGOrchestrator:
    global _embedder, _store, _retriever, _llm, _rag
    if _rag is None:
        _embedder = build_embedder(settings)
        _store = QdrantStore(settings)
        _retriever = Retriever(_embedder, _store, settings)
        _llm = build_llm(settings)
        _rag = RAGOrchestrator(_retriever, _llm, settings)
    return _rag


@router.get("/health", response_model=HealthResponse)
async def health():
    store = QdrantStore(settings)
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        llm_provider=settings.LLM_PROVIDER,
        vector_store="memory" if not (settings.QDRANT_URL or settings.QDRANT_HOST) else "qdrant",
        documents=store.count(),
    )


@router.post(
    "/documents",
    response_model=IngestResponse,
    dependencies=[Depends(require_api_key)],
)
async def upload_document(file: UploadFile = File(...)):
    data = await file.read()
    max_bytes = settings.MAX_FILE_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File too large (max {settings.MAX_FILE_MB}MB)")

    resp, chunks = prepare_document(file.filename or "unknown", data)
    rag = _get_rag()
    texts = [c.text for c in chunks]
    if texts:
        vecs = await _embedder.embed(texts)
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=v,
                payload={"text": c.text, "source": c.source, "metadata": c.metadata},
            )
            for c, v in zip(chunks, vecs)
        ]
        _store.upsert(points)
    return resp


@router.post("/chat")
async def chat(req: ChatRequest):
    rag = _get_rag()

    async def event_gen():
        async for ev in rag.ask(req.question, req.history, req.top_k, req.session_id or "default"):
            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        yield "data: {\"type\":\"end\"}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
