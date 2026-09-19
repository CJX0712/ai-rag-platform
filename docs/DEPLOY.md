# 部署指南

**作者**：晨星

三种部署方式，按环境与需求选择。

## 方式 A：Docker Compose（推荐，一键全套）

```bash
cp .env.example .env
docker compose up --build
```

启动顺序：`ollama` → `ollama-pull`（拉取 `nomic-embed-text` + `qwen2.5:7b`）→ `qdrant` → `backend` → `frontend`。
访问：前端 `http://localhost:8080`，API 文档 `http://localhost:8000/docs`。

常用命令：

```bash
docker compose down                 # 停止
docker compose down -v             # 停止并清除卷（Qdrant/Ollama 数据）
docker compose logs -f backend     # 看后端日志
```

## 方式 B：本地无 Docker（开发）

后端：

```bash
cd backend && python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --port 8000 --reload
```

未配置 `QDRANT_HOST` 时后端自动使用内存向量库，可直接联调。
前端（另开终端）：

```bash
cd frontend && npm install && npm run dev
```

Vite 在 `:5173` 启动并把 `/api` 代理到 `:8000`。

## 方式 C：切换为云端模型（无需本地 GPU）

编辑 `.env`：

```
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
# 可选：自定义兼容端点
LLM_BASE_URL=https://api.openai.com/v1
OPENAI_EMBED_BASE_URL=https://api.openai.com/v1
OPENAI_EMBED_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
```

支持任意 OpenAI 兼容服务（DeepSeek、通义等）：把 `LLM_BASE_URL` / `OPENAI_EMBED_BASE_URL` 指向其地址即可。

## 依赖与构建复现

| 层 | 锁定文件 | 验证 |
|----|----------|------|
| 后端 Python | `backend/requirements.txt`（精确 `==`） | `pip install -r requirements.txt` → `pytest` |
| 前端 Node | `frontend/package.json` + `package-lock.json` | `npm ci` → `npm run build` |

干净环境中按上述命令即可得到一致构建。本仓库已实测：后端 `pytest` 8 passed、离线 `smoke.py` 全链路通过、前端 `vite build` + `tsc --noEmit` 全绿。

## 故障排查

| 现象 | 原因 / 处理 |
|------|-------------|
| `pip install` 报某个包 404 | 镜像源缺少标准包。换官方源：`pip install -r requirements.txt -i https://pypi.org/simple` |
| `npm install` 报 `@types/react` 404 | 本机 npm 指向非官方镜像（如 ohpm）。加 `--registry https://registry.npmjs.org/` |
| 启动后 `/chat` 无回答 | 确认 `LLM_PROVIDER` 对应的服务可达（Ollama `:11434` 或 OpenAI Key 有效）；可先设 `LLM_PROVIDER=mock` 验证链路 |
| 向量检索为空 | 先 `POST /api/v1/documents` 上传文档；`mock` 模式下仍可检索（内存库） |
| 跨域报错 | 开发用 Vite 代理已处理；生产由 nginx 反代 `/api`，无需额外 CORS |

## 安全

- 生产请在 `.env` 设置 `API_KEY`，前端侧“API Key”输入框填写；未设置则接口开放。
- 当前鉴权为轻量共享 Key，正式多租户请前置身份网关并启用 HTTPS。
