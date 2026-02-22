---
name: prime
description: Understand the InCube Portal codebase or a specific workspace. Explores structure, dependencies, architecture, and available tools for backend or frontend workspaces.
context: fork
argument-hint: [all|backend|frontend]
---


# Prime Workspace

Understand the InCube Portal codebase or a specific workspace.

## Workspace Selection

**Ask the user what to prime:**

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
- `docs/prd/incube-platform-v1.prd.md` - Product requirements document (if exists)
- `backend/pyproject.toml` - Backend dependencies
- `frontend/package.json` - Frontend dependencies
- `docker-compose.dev.yml` - Development infrastructure

### Explore Structure
```bash
ls -la /home/wkoch/github-repos/incube-portal/
ls -la /home/wkoch/github-repos/incube-portal/backend/
ls -la /home/wkoch/github-repos/incube-portal/backend/app/
ls -la /home/wkoch/github-repos/incube-portal/frontend/
ls -la /home/wkoch/github-repos/incube-portal/frontend/src/
```

### Explore Claude Code Configuration
```bash
ls -la /home/wkoch/github-repos/incube-portal/.claude/
ls -la /home/wkoch/github-repos/incube-portal/.claude/skills/
ls -la /home/wkoch/github-repos/incube-portal/.claude/hooks/ 2>/dev/null || echo "No hooks configured"
ls -la /home/wkoch/github-repos/incube-portal/.claude/PRPs/ 2>/dev/null || echo "No PRPs yet"
ls -la /home/wkoch/github-repos/incube-portal/.claude/PRPs/plans/ 2>/dev/null
ls -la /home/wkoch/github-repos/incube-portal/.claude/PRPs/reports/ 2>/dev/null
```

### Read Key Entry Points
- `backend/app/main.py` - FastAPI application entry point
- `frontend/src/app/` - Next.js App Router structure
- `deploy/` - Production deployment configuration

### Summarize
Provide overview of:
1. Project structure and current state
2. Tech stack (backend + frontend)
3. InCube framework concepts (Dimensions, Phases, Agents)
4. Development workflow
5. Available skills
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
- Claude Agent SDK for 9 cognitive agents (8 specialists + Axiom adversarial reviewer)
- Axiom uses bounded single-pass debate (max 3 LLM calls per challenge)
- All agent calls tracked in `agent_sessions` with token counts and costs
- Post-vibe analysis runs all 9 agents in parallel on transcript + documents
- Pydantic v2 for validation
- Alembic for migrations
- SSE streaming for real-time agent responses
- MinIO for file storage
- PostgreSQL on host port 5435 (Docker maps 5435:5432)
- Redis on host port 6380 (Docker maps 6380:6379)
- MinIO on host ports 9002/9003 (Docker maps 9002:9000 and 9003:9001)

## If "frontend" selected

Focus on:
- `frontend/src/app/` - Next.js App Router pages
- `frontend/src/components/` - UI components
- `frontend/src/stores/` - Zustand state stores
- `frontend/src/lib/` - Utilities
- `frontend/src/types/` - TypeScript types
- `frontend/package.json` - Dependencies

Key patterns:
- Next.js 15 with App Router
- Tailwind CSS 4 with custom design system
- shadcn/ui component library
- Zustand for client state
- React Query (TanStack) for server state
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
| PostgreSQL | Docker | 5435 | Primary database |
| Redis | Docker | 6380 | Cache and job queue |
| MinIO | Docker | 9002/9003 | S3-compatible file storage |

## Project Structure

```
incube-portal/
├── .claude/                    # Claude Code configuration
│   ├── hooks/                  # Hook scripts
│   ├── skills/                 # Skill definitions (SKILL.md format)
│   │   ├── at-plan-bug/        # Bug fix planning
│   │   ├── at-plan-chore/      # Maintenance planning
│   │   ├── at-plan-feature/    # Feature planning
│   │   ├── browse/             # Visual testing
│   │   ├── commit/             # Commit + PR + merge
│   │   ├── deploy/             # Deploy to production
│   │   ├── install/            # Install dependencies
│   │   ├── prime/              # This skill
│   │   └── startup/            # Start dev services
│   └── PRPs/                   # Plans and reports
│       ├── plans/              # Implementation plans
│       └── reports/            # Implementation reports
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/routes/         # API route handlers
│   │   ├── core/               # Config and settings
│   │   ├── db/                 # Database session
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/           # Business logic + AI agents
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Test suite
│   └── pyproject.toml          # Python dependencies
├── frontend/                   # Next.js 15 frontend
│   └── src/
│       ├── app/                # Next.js App Router
│       │   ├── (auth)/         # Auth pages (login, register)
│       │   └── (app)/          # Protected app pages
│       ├── components/         # UI components
│       ├── stores/             # Zustand state stores
│       ├── lib/                # Utilities
│       └── types/              # TypeScript types
├── deploy/                     # Production deployment
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.prod.yml
│   └── .env.production.example
├── docs/                       # Documentation
└── docker-compose.dev.yml      # Dev infrastructure (PostgreSQL + Redis + MinIO)
```

## Available Skills

| Skill | Description |
|-------|-------------|
| `/commit` | Commit + PR + merge to main |
| `/prime` | Understand the codebase (this skill) |
| `/install` | Install project dependencies |
| `/startup` | Start development services in tmux |
| `/deploy` | Deploy to production |
| `/browse` | Visual testing with agent-browser |
| `/at-plan-feature` | Create a feature implementation plan |
| `/at-plan-bug` | Create a bug fix plan |
| `/at-plan-chore` | Create a maintenance plan |

## Production URLs

| Project | Local | Production |
|---------|-------|------------|
| Backend | http://localhost:8000 | https://incube.motionmind.antikythera.co.za/api |
| Frontend | http://localhost:3001 | https://incube.motionmind.antikythera.co.za |

**Server:** Motion Mind Linode VPS `159.223.208.109`
