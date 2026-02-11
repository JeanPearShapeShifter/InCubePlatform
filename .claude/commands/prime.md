---
description: "Understand the InCube codebase"
---

# Prime Workspace

Understand the InCube Platform codebase.

## What to Prime

**Ask the user what to focus on:**

1. **all** - Full project overview (recommended for first time)
2. **backend** - FastAPI backend (API, models, services, agents)
3. **frontend** - Next.js frontend (pages, components, stores)

Example: "What would you like to understand? (all/backend/frontend)"

## If "all" selected - Full Project Overview

### Run
```bash
cd /home/wkoch/github-repos/incube-portal
git ls-files | head -150
```

### Read
- `CLAUDE.md` - Architecture, commands, and patterns
- `docs/prd/incube-platform-v1.prd.md` - Product requirements document
- `backend/pyproject.toml` - Backend dependencies (if exists)
- `frontend/package.json` - Frontend dependencies (if exists)
- `docker-compose.dev.yml` - Development infrastructure (if exists)

### Explore Structure
```bash
ls -la /home/wkoch/github-repos/incube-portal/
ls -la /home/wkoch/github-repos/incube-portal/backend/ 2>/dev/null || echo "Backend not yet scaffolded"
ls -la /home/wkoch/github-repos/incube-portal/frontend/ 2>/dev/null || echo "Frontend not yet scaffolded"
ls -la /home/wkoch/github-repos/incube-portal/.claude/
ls -la /home/wkoch/github-repos/incube-portal/.claude/commands/
ls -la /home/wkoch/github-repos/incube-portal/docs/
```

### Summarize
Provide overview of:
1. Project structure and current state
2. Tech stack (backend + frontend)
3. InCube framework concepts (Dimensions, Phases, Agents)
4. Development workflow
5. Available commands
6. Implementation status (what's built vs what's planned)

## If "backend" selected

Focus on:
- `backend/app/main.py` - FastAPI entry point
- `backend/app/api/routes/` - API route handlers
- `backend/app/models/` - SQLAlchemy models
- `backend/app/schemas/` - Pydantic schemas
- `backend/app/services/` - Business logic and AI agent orchestration
- `backend/app/core/config.py` - Settings
- `backend/app/db/` - Database session
- `backend/alembic/` - Migrations
- `backend/tests/` - Test suite

Key patterns:
- FastAPI with async SQLAlchemy (asyncpg)
- Claude Agent SDK for 9 cognitive agents
- Pydantic v2 for validation
- Alembic for migrations
- SSE streaming for agent responses
- MinIO for file storage
- PostgreSQL on host port 5434

## If "frontend" selected

Focus on:
- `frontend/src/app/` - Next.js App Router pages
- `frontend/src/components/` - UI components
- `frontend/src/stores/` - Zustand state stores
- `frontend/src/hooks/` - Custom hooks
- `frontend/src/lib/` - Utilities
- `frontend/src/types/` - TypeScript types
- `frontend/package.json` - Dependencies

Key patterns:
- Next.js 15 with App Router
- Tailwind CSS 4 with custom design system
- shadcn/ui component library
- Zustand for client state
- React Query for server state
- Web Audio API for vibe recording

App routes:
- `(auth)/` - Login, register
- `(app)/dashboard` - Active journeys, usage stats
- `(app)/canvas` - Main workspace (the Cube)
- `(app)/bank` - Timeline of banked artefacts
- `(app)/vdbas` - Published assets dashboard
- `(app)/fundamentals` - Methodology documentation
- `(app)/settings` - API usage, voice, email config

## Quick Reference

| Component | Tech Stack | Port | Description |
|-----------|-----------|------|-------------|
| Backend | FastAPI + SQLAlchemy + Claude Agent SDK | 8000 | API server with AI agent orchestration |
| Frontend | Next.js 15 + React 19 + Tailwind 4 | 3001 | Web application |
| PostgreSQL | Docker | 5434 | Primary database |
| Redis | Docker | 6379 | Cache and job queue |
| MinIO | Docker | 9000/9001 | S3-compatible file storage |

## Custom Commands Available

| Command | Description |
|---------|-------------|
| `/commit` | Full git pipeline (commit → PR → merge) |
| `/prime` | Understand the codebase (this command) |
| `/install` | Install project dependencies |
| `/deploy` | Deploy to production |
