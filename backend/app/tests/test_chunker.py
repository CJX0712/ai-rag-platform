from app.modules.ingestion.chunker import split_text


def test_basic_split():
    chunks = split_text("a" * 100, 30, 0)
    assert chunks
    assert all(len(c) <= 30 for c in chunks)


def test_overlap_produces_multiple():
    chunks = split_text("x" * 100, 40, 10)
    assert len(chunks) > 1


def test_empty_returns_empty():
    assert split_text("   \n\t ") == []


def test_whitespace_normalised():
    chunks = split_text("hello   world\nfoo", 100, 0)
    assert chunks[0] == "hello world foo"


def test_invalid_chunk_size():
    import pytest

    with pytest.raises(ValueError):
        split_text("abc", 0, 0)
