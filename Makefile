# AI RAG Platform - convenience targets
# (Requires Docker / Make on the host. The repo is also runnable without Docker.)

.PHONY: up down build logs test smoke backend-dev frontend-dev

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

# --- local backend (no Docker): venv + uvicorn on :8000 ---
backend-dev:
	cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt && .venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

# --- local frontend (no Docker): vite dev server on :5173 (proxies /api) ---
frontend-dev:
	cd frontend && npm install && npm run dev

# run the offline smoke test (mock providers, no external services)
smoke:
	cd backend && .venv/Scripts/python smoke.py

# backend unit + integration tests
test:
	cd backend && .venv/Scripts/python -m pytest -q
