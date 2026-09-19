"""Pydantic schemas shared across modules. Schema-as-contract."""
from typing import Optional

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    text: str
    source: str
    chunk_index: int
    metadata: dict = Field(default_factory=dict)


class IngestResponse(BaseModel):
    doc_id: str
    filename: str
    chunks: int
    chars: int


class RetrievedDoc(BaseModel):
    text: str
    source: str
    score: float
    metadata: dict = Field(default_factory=dict)


class ChatMessage(BaseModel):
    role: str  # system | user | assistant
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = Field(default_factory=list)
    top_k: Optional[int] = None
    session_id: Optional[str] = None


class SourceRef(BaseModel):
    source: str
    score: float
    snippet: str


# SSE event payloads emitted by /chat
class TokenEvent(BaseModel):
    type: str = "token"
    text: str


class SourcesEvent(BaseModel):
    type: str = "sources"
    sources: list[SourceRef]


class DoneEvent(BaseModel):
    type: str = "done"
    session_id: str


class HealthResponse(BaseModel):
    status: str
    version: str
    embedding_provider: str
    llm_provider: str
    vector_store: str
    documents: int = 0
