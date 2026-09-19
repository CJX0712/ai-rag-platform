# 使用指南

**作者**：晨星

## 1. 上传知识文档

- 在左侧边栏点击 **上传知识文档**，选择 `.pdf / .txt / .md / .html` 文件（≤20MB）。
- 系统自动：解析 → 切片（默认 800 字符 / 120 重叠）→ 向量化 → 写入向量库。
- 响应示例：

```json
{ "doc_id": "a1b2c3...", "filename": "kb.txt", "chunks": 6, "chars": 4200 }
```

- 边栏“已存文档”数值会通过 `/health` 实时刷新。

## 2. 提问与引用

- 在底部输入框输入问题，`Enter` 发送，`Shift+Enter` 换行。
- 答案以流式逐字显示；回答下方展示 **引用来源**（文件名 + 相关度 + 片段）。
- 多轮对话：输入框历史会自动带入，RAG 编排取最近 6 条作为上下文。

## 3. REST API

基础路径：`/api/v1`

### `GET /health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "embedding_provider": "ollama",
  "llm_provider": "ollama",
  "vector_store": "qdrant",
  "documents": 6
}
```

### `POST /documents`（multipart/form-data，`file` 字段）

受 `API_KEY` 保护（若已设置）。返回 `IngestResponse`。

### `POST /chat`（JSON，SSE 流式）

请求：

```json
{ "question": "RAG 是什么？", "history": [], "top_k": 5 }
```

响应（`text/event-stream`，每行 `data: {...}`）：

```
data: {"type":"sources","sources":[{"source":"kb.txt","score":0.82,"snippet":"..."}]}
data: {"type":"token","text":"RAG 是"}
data: {"type":"token","text":"检索增强生成..."}
data: {"type":"done","session_id":"default"}
data: {"type":"end"}
```

curl 示例：

```bash
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"RAG 是什么？"}'
```

## 4. 配置项速查

| 变量 | 默认 | 说明 |
|------|------|------|
| `EMBEDDING_PROVIDER` | `ollama` | `ollama` / `openai` / `mock` |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Ollama 嵌入模型 |
| `LLM_PROVIDER` | `ollama` | `ollama` / `openai` / `mock` |
| `LLM_MODEL` | `qwen2.5:7b` | 生成模型 |
| `QDRANT_HOST` | 空（内存） | 设置后改用 Qdrant 服务 |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `800` / `120` | 切片参数 |
| `RETRIEVE_TOP_K` | `5` | 每问召回片段数 |
| `API_KEY` | 空 | 设置后保护 `/documents` |

完整变量见 [`.env.example`](../.env.example)。

## 5. 常见用法组合

| 场景 | 配置 |
|------|------|
| 本机纯演示（无 GPU / 无 API） | `EMBEDDING_PROVIDER=mock` `LLM_PROVIDER=mock` |
| 本机隐私优先 | `EMBEDDING_PROVIDER=ollama` `LLM_PROVIDER=ollama`（本地 Ollama） |
| 云端高质量 | `EMBEDDING_PROVIDER=openai` `LLM_PROVIDER=openai` + `OPENAI_API_KEY` |
