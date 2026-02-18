# CLAUDE.md - InCube Portal

## Project Overview
AI-powered business transformation framework. FastAPI backend (Python 3.12+, SQLAlchemy, asyncpg) + Next.js 15 frontend (React 19, Tailwind CSS 4). Features 9 AI agents across 3 dimensions x 4 phases with a banking/publishing system.

## Commands
```bash
# Backend
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
pytest
ruff check .

# Frontend
cd frontend && npm run dev    # http://localhost:3001
npm run build && npm run lint

# Infrastructure
docker compose -f docker-compose.dev.yml up -d   # PostgreSQL (5434) + Redis (6379) + MinIO (9000/9001)
cd backend && source .venv/bin/activate && alembic upgrade head
```

## Key Patterns
- 9 AI agents: 8 specialists + Axiom (adversarial reviewer), Claude Agent SDK
- Axiom uses bounded single-pass debate (max 3 LLM calls per challenge)
- All agent calls tracked in `agent_sessions` with token counts and costs
- Post-vibe analysis runs all 9 agents in parallel on transcript + documents
- Streaming via Server-Sent Events (SSE) for real-time agent responses
- Dev PostgreSQL on port 5434 to avoid conflicts

## Brain Vault References
- Architecture: `brain_search("incube portal architecture")`

## Credentials
All secrets in the encrypted vault. Use `credential_get("service name")`.
