# AI RAG 知识问答平台

<p align="center">
  <a href="https://github.com/CJX0712/ai-rag-platform-9jkaa/actions/workflows/ci.yml"><img src="https://github.com/CJX0712/ai-rag-platform-9jkaa/actions/workflows/ci.yml/badge.svg" alt="ci"></a>
  <a href="https://github.com/CJX0712/ai-rag-platform-9jkaa/releases"><img src="https://img.shields.io/github/v/release/CJX0712/ai-rag-platform-9jkaa?sort=semver" alt="release"></a>
  <img src="https://img.shields.io/badge/author-%E6%99%A8%E6%98%9F-1f6feb" alt="author">
</p>

> 端到端可运行的检索增强生成（RAG）系统：文档摄取 → 向量化 → 检索 → LLM 生成流式回答。
> 复用业界领先开源成果（FastAPI / Qdrant / Ollama / React），模块按单一职责划分，可独立验证、可协同组成完整链路。

**作者**：晨星

---

## 特性

- **单职责模块**：摄取 / 嵌入 / 向量库 / 检索 / LLM 网关 / RAG 编排，各自清晰接口，可独立测试。
- **可切换模型**：嵌入与生成默认本地 **Ollama**（nomic-embed-text + qwen2.5），一键切 **OpenAI 兼容 API**，或 **mock** 离线演示。
- **端到端流式**：`/chat` 以 SSE 返回 `sources → token → done` 事件，前端实时渲染答案与引用来源。
- **零外部依赖兜底**：未配置 Qdrant 时自动用内存向量库；`mock` 模式下无需任何模型服务即可跑通全链路。
- **一键复现**：`docker compose up --build` 起整套；干净环境中 `requirements.txt` + `package-lock.json` 版本锁定。

## 架构

```
[React 前端] ──HTTP/SSE──▶ [FastAPI 网关]
        │
        ├─ ingestion   解析/切片
        ├─ embedding   文本→向量（Ollama/OpenAI/mock）
        ├─ vectorstore Qdrant（或内存）
        ├─ retrieval   embed+检索+重排
        ├─ llm_gateway 流式生成（Ollama/OpenAI/mock）
        └─ rag         组装上下文→流式答案+引用
```

详见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 快速开始（Docker）

```bash
cp .env.example .env        # 按需修改（模型/API Key/端口）
docker compose up --build   # 自动拉取模型并启动全部服务
```

- 前端：http://localhost:8080
- 后端 API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/v1/health

## 本地开发（无 Docker）

```bash
# 后端
cd backend && python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --port 8000

# 前端（另开终端，默认代理 /api 到 :8000）
cd frontend && npm install && npm run dev
```

> 注意：若本机 npm 被指向非官方镜像（如 ohpm），请加 `--registry https://registry.npmjs.org/` 安装。详见 [docs/DEPLOY.md](docs/DEPLOY.md)。

## 验证

```bash
# 后端单元 + 集成测试（mock 离线跑通全链路）
cd backend && .venv/Scripts/python -m pytest -q

# 离线 smoke（无需 Ollama/Qdrant/API）
cd backend && .venv/Scripts/python smoke.py
```

## 文档

| 文档 | 内容 |
|------|------|
| [README.md](README.md) | 总览与快速开始 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系统架构、模块接口、调用关系 |
| [docs/DEPLOY.md](docs/DEPLOY.md) | 部署指南（Docker / 本地 / 云端切换 / 故障排查） |
| [docs/USAGE.md](docs/USAGE.md) | 使用指南（上传 / 对话 / API / 配置） |

## 许可证

MIT
