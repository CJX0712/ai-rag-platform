# 系统架构

**作者**：晨星

本文描述 AI RAG 平台的模块边界、接口契约与调用关系。每个模块只做一件事，通过 Pydantic Schema 与函数签名耦合，可单独测试，也能协同组成端到端链路。

## 1. 总体数据流

```
用户上传 PDF/TXT/MD/HTML
      │
      ▼
[ingestion]  extract_text() → split_text()  → list[DocumentChunk]
      │
      ▼  embed(texts)
[embedding] 文本 → 向量（Ollama / OpenAI / mock）
      │
      ▼  upsert(points)
[vectorstore] Qdrant（或内存）持久化
      │
用户提问
      │
      ▼  retrieve(query)
[retrieval]  embed(query) → vectorstore.search() → list[RetrievedDoc]
      │
      ▼  ask(question)
[rag]        组装 system(上下文) → [llm_gateway].stream() → SSE 事件
      │
      ▼
[llm_gateway]  Ollama / OpenAI / mock 流式生成
      │
      ▼
[api]        /chat 以 SSE 推送 sources → token → done
      │
      ▼
[前端]        实时渲染答案与引用来源
```

## 2. 模块划分

| 模块 | 目录 | 职责 | 关键接口 | 依赖 |
|------|------|------|----------|------|
| API 网关 | `app/api/router.py` | 路由、可选鉴权、SSE 封装 | `POST /documents`、`POST /chat`、`GET /health` | 全部 |
| 摄取 | `modules/ingestion` | 解析 + 切片 | `prepare_document()` → `(IngestResponse, list[DocumentChunk])` | — |
| 嵌入 | `modules/embedding` | 文本→向量（可切换） | `Embedder.embed(texts) -> list[list[float]]` | httpx |
| 向量库 | `modules/vectorstore` | 写入 + 相似检索 | `QdrantStore.upsert() / search()` | qdrant-client |
| 检索 | `modules/retrieval` | query→embed→检索 | `Retriever.retrieve(query) -> list[RetrievedDoc]` | embedding, vectorstore |
| LLM 网关 | `modules/llm_gateway` | 流式生成（可切换） | `LLMBackend.stream(messages) -> AsyncIterator[str]` | httpx |
| RAG 编排 | `modules/rag` | 上下文组装 + 流式答案 | `RAGOrchestrator.ask() -> AsyncIterator[dict]` | retrieval, llm_gateway |

## 3. 接口契约（Schema）

所有跨模块数据结构定义在 `app/schemas/common.py`（Schema-as-Contract）：

- `DocumentChunk { text, source, chunk_index, metadata }`
- `IngestResponse { doc_id, filename, chunks, chars }`
- `RetrievedDoc { text, source, score, metadata }`
- `ChatRequest { question, history[], top_k?, session_id? }`
- `ChatEvent`（SSE）：`{type:"sources", sources[]}` / `{type:"token", text}` / `{type:"done", session_id}`

## 4. 可切换能力（Provider 抽象）

| 能力 | 实现 | 切换变量 |
|------|------|----------|
| 嵌入 | `OllamaEmbedder` / `OpenAIEmbedder` / `MockEmbedder` | `EMBEDDING_PROVIDER` |
| 生成 | `OllamaBackend` / `OpenAIBackend` / `MockBackend` | `LLM_PROVIDER` |
| 向量库 | Qdrant（`QDRANT_HOST` 设置）或内存（未设置） | `QDRANT_HOST` / `QDRANT_URL` |

抽象基类 `Embedder` / `LLMBackend` 让测试可注入 `MockEmbedder` / `MockBackend`，无需任何外部服务即可验证全链路（见 `app/tests/`）。

## 5. 前端架构

- `src/api/client.ts`：axios 封装 REST + 原生 `fetch` 消费 SSE。
- `src/hooks/useChat.ts`：管理消息流与引用来源状态。
- `src/components/Sidebar.tsx`：品牌、上传、运行状态、API Key。
- `src/components/ChatPanel.tsx`：对话区、引用来源、输入区。
- 设计令牌（Design Token）集中于 `tailwind.config.js` + `src/index.css` 的 CSS 变量；图标统一使用 `lucide-react`（SVG），无 emoji、无紫粉渐变。

## 6. 部署拓扑

```
                  ┌────────────┐
  浏览器 ─────────▶│  frontend  │ (React + nginx :8080)
                  └─────┬──────┘
                        │ /api
                  ┌─────▼──────┐
                  │  backend   │ (FastAPI :8000)
                  └──┬─────┬───┘
                     │     │
              ┌──────▼┐  ┌─▼──────┐
              │Qdrant │  │ Ollama │ (nomic-embed-text, qwen2.5)
              └───────┘  └────────┘
```

详见 [DEPLOY.md](DEPLOY.md) 与 [USAGE.md](USAGE.md)。
