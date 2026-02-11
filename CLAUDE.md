# CLAUDE.md

## Project Overview

InCube Platform — AI-powered business transformation framework. Two components:
- **Backend** — FastAPI API server (Python 3.12+, SQLAlchemy, asyncpg)
- **Frontend** — Next.js 15 web application (React 19, Tailwind CSS 4)

## Commands

**Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
pytest
ruff check .
```

**Frontend:**
```bash
cd frontend
npm run dev      # http://localhost:3001
npm run build
npm run lint
```

**Infrastructure:**
```bash
docker compose -f docker-compose.dev.yml up -d   # PostgreSQL (5434) + Redis (6379) + MinIO (9000/9001)
cd backend && source .venv/bin/activate && alembic upgrade head   # Run migrations
```

## Project Structure

```
incube-portal/
├── .claude/                    # Claude Code configuration
│   └── commands/               # Custom slash commands
│       ├── commit.md           # Commit → PR → Merge pipeline
│       ├── prime.md            # Understand the codebase
│       ├── install.md          # Install dependencies
│       └── deploy.md           # Deploy to production
├── docs/
│   └── prd/                    # Product requirement documents
│       └── incube-platform-v1.prd.md
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/routes/         # API route handlers
│   │   ├── core/               # Config, security, dependencies
│   │   ├── db/                 # Database session, seed scripts
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/           # Business logic, agent orchestration
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Test suite
│   ├── pyproject.toml          # Python dependencies
│   └── .env.example            # Environment template
├── frontend/                   # Next.js 15 application
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   │   ├── (auth)/         # Login, register pages
│   │   │   ├── (app)/          # Protected app pages
│   │   │   │   ├── dashboard/  # Active journeys, usage stats
│   │   │   │   ├── canvas/     # Main workspace (the Cube)
│   │   │   │   ├── bank/       # Timeline of banked artefacts
│   │   │   │   ├── vdbas/      # Published assets dashboard
│   │   │   │   ├── fundamentals/ # Methodology documentation
│   │   │   │   └── settings/   # API usage, voice, email config
│   │   │   ├── globals.css     # Design system
│   │   │   └── layout.tsx      # Root layout
│   │   ├── components/
│   │   │   ├── canvas/         # Canvas workspace components
│   │   │   ├── agents/         # Agent card, conversation components
│   │   │   ├── editors/        # Document editors (Word, Spreadsheet, etc.)
│   │   │   ├── vibe/           # Voice recording, waveform components
│   │   │   ├── bank/           # Bank timeline, synopsis components
│   │   │   ├── layout/         # Header, sidebar, navigation
│   │   │   └── ui/             # shadcn/ui components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── stores/             # Zustand state stores
│   │   ├── lib/                # Utilities
│   │   └── types/              # TypeScript type definitions
│   └── package.json
├── docker-compose.dev.yml      # Dev PostgreSQL + Redis + MinIO
└── CLAUDE.md                   # This file
```

## Architecture

### The InCube Framework
- **3 Dimensions**: Architecture, Design, Engineering
- **4 Phases**: Generate, Review, Validate, Summarize
- **12 Perspectives**: Each dimension x phase intersection
- **9 AI Agents**: 8 specialists + Axiom (challenger/adversarial reviewer)
- **Banking System**: Bankable → Film → Film Reel → Published VDBA

### AI Agent System
- **SDK**: Claude Agent SDK (Python)
- **Default Model**: Haiku (configurable per agent in settings)
- **Orchestration**: Parallel specialist execution → Axiom review → Synthesis
- **Streaming**: Server-Sent Events (SSE) for real-time agent responses

### Key Services
| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3001 | Next.js web application |
| Backend | 8000 | FastAPI API server |
| PostgreSQL | 5434 | Primary database (Docker) |
| Redis | 6379 | Cache and job queue (Docker) |
| MinIO | 9000/9001 | S3-compatible file storage (Docker) |

## Database Strategy

| Environment | Database | Connection |
|-------------|----------|------------|
| **Development** | `incube_dev` | `localhost:5434` (Docker) |
| **Production** | `incube` | Docker internal network |

- ORM: SQLAlchemy 2.0 + asyncpg
- Migrations: Alembic
- Dev port 5434 to avoid conflicts with local PostgreSQL

## Key Patterns

- All AI agent calls tracked in `agent_sessions` with token counts and costs
- Axiom uses bounded single-pass debate (max 3 LLM calls per challenge)
- Post-vibe analysis runs all 9 agents in parallel on transcript + documents
- Decision audit trail attached to every bank instance
- API usage aggregated in `api_usage` table for settings dashboard

## Production

| Service | Local | Production |
|---------|-------|------------|
| Frontend | :3001 | TBD |
| Backend | :8000 | TBD |

## GitHub

- **Repository**: github.com/JeanPearShapeShifter/InCubePlatform
- **Push Account**: `antikythera-agent-zero`
