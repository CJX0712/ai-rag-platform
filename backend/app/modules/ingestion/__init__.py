"""Ingestion module: parse uploaded files and split into chunks."""
from app.modules.ingestion.service import prepare_document

__all__ = ["prepare_document"]
