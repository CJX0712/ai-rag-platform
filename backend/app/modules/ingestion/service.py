"""Ingestion service: orchestrates parse + chunk for one upload."""
import uuid

from app.core.config import get_settings
from app.modules.ingestion.chunker import split_text
from app.modules.ingestion.parsers import extract_text
from app.schemas.common import DocumentChunk, IngestResponse


def prepare_document(filename: str, data: bytes):
    """Parse + chunk a file.

    Returns ``(IngestResponse, list[DocumentChunk])``. Embedding and vector
    storage are intentionally left to the caller (single-responsibility).
    """
    settings = get_settings()
    text = extract_text(filename, data)
    pieces = split_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    doc_id = uuid.uuid4().hex
    chunks = [
        DocumentChunk(
            text=p,
            source=filename,
            chunk_index=i,
            metadata={"doc_id": doc_id},
        )
        for i, p in enumerate(pieces)
    ]
    resp = IngestResponse(
        doc_id=doc_id, filename=filename, chunks=len(chunks), chars=len(text)
    )
    return resp, chunks
