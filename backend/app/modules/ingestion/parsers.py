"""Format-specific text extraction. New formats plug in via ``extract_text``."""
import io
import re


def extract_text(filename: str, data: bytes) -> str:
    """Return plain text from an uploaded file based on its extension."""
    lower = (filename or "").lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(data)
    if lower.endswith((".md", ".markdown")):
        return data.decode("utf-8", errors="ignore")
    if lower.endswith((".txt", ".text")):
        return data.decode("utf-8", errors="ignore")
    if lower.endswith((".html", ".htm")):
        return _strip_html(data.decode("utf-8", errors="ignore"))
    # unknown: best-effort decode
    return data.decode("utf-8", errors="ignore")


def _extract_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("pypdf is required to parse PDF files") from exc
    reader = PdfReader(io.BytesIO(data))
    parts = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(parts)


def _strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = re.sub(r"&nbsp;", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()
