"""RAG orchestrator: ties retrieval + LLM into a streamed answer.

``ask`` yields dict events (``{"type": "sources"|"token"|"done", ...}``) which
the API layer serialises into Server-Sent Events. Keeping the event shape
here - not in the transport - makes the orchestrator independently testable.
"""
import json
from typing import AsyncIterator, List, Optional

from app.core.config import get_settings
from app.modules.llm_gateway.gateway import LLMBackend
from app.modules.retrieval.service import Retriever
from app.schemas.common import ChatMessage, RetrievedDoc, SourceRef

SYSTEM_PROMPT = (
    "你是一个严谨的知识问答助手。请仅基于[检索上下文]中的资料回答问题；"
    "若上下文不足以回答，请明确说明。使用中文回答，并在可行时标注引用来源。"
)


def _build_system(context: List[RetrievedDoc]) -> str:
    if not context:
        return SYSTEM_PROMPT + "\n\n[检索上下文] 无相关文档。"
    lines = [SYSTEM_PROMPT, "\n[检索上下文]"]
    for i, d in enumerate(context, 1):
        lines.append(f"[{i}] 来源: {d.source}\n{d.text}")
    return "\n".join(lines)


class RAGOrchestrator:
    def __init__(self, retriever: Retriever, llm: LLMBackend, settings=None):
        self.retriever = retriever
        self.llm = llm
        self.settings = settings or get_settings()

    async def ask(
        self,
        question: str,
        history: Optional[List[ChatMessage]] = None,
        top_k: Optional[int] = None,
        session_id: str = "default",
    ) -> AsyncIterator[dict]:
        history = history or []
        docs = await self.retriever.retrieve(question, top_k=top_k)

        system = _build_system(docs)
        messages = [{"role": "system", "content": system}]
        for m in history[-6:]:
            messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": question})

        sources = [
            SourceRef(source=d.source, score=round(d.score, 4), snippet=d.text[:160])
            for d in docs
        ]
        yield {"type": "sources", "sources": [s.model_dump() for s in sources]}

        async for delta in self.llm.stream(
            messages, self.settings.LLM_TEMPERATURE, self.settings.LLM_MAX_TOKENS
        ):
            yield {"type": "token", "text": delta}

        yield {"type": "done", "session_id": session_id}
