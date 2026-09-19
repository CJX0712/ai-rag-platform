"""Deterministic, overlap-based text chunking (no external tokenizer needed)."""
from typing import List


def split_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """Split ``text`` into overlapping windows of ``chunk_size`` characters.

    Whitespace is normalised first so chunks are clean. Overlap keeps context
    that would otherwise be cut at window boundaries.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 4)

    text = " ".join(text.split())
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap
    return chunks
