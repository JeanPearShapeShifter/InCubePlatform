# Feature: Phase 1 — Foundation

## Summary

Set up the complete project infrastructure from scratch: Docker Compose for development services (PostgreSQL 16, Redis 7, MinIO), FastAPI backend skeleton with async SQLAlchemy 2.0, all 17 database tables as SQLAlchemy models with Alembic migrations, Pydantic configuration, health check endpoint, and a Next.js 15 frontend scaffold with Tailwind CSS 4 and shadcn/ui. This is the bedrock phase — nothing else can be built until this passes validation.

## User Story

As a developer on the InCube project
I want the complete project foundation scaffolded with working infrastructure, database, API skeleton, and frontend shell
So that subsequent phases (Auth, Core Models, AI Agents, Frontend) can build on a verified, pattern-consistent base

## Problem Statement

The repository currently contains only documentation (PRD, CLAUDE.md, slash commands). Zero application code exists — no `backend/`, no `frontend/`, no `docker-compose.dev.yml`. Everything must be created from scratch following the patterns specified in the PRD.

## Solution Statement

Create the full development infrastructure and application scaffolding in a single phase:
1. Docker Compose for PostgreSQL (port 5434), Redis (port 6379), MinIO (ports 9000/9001)
2. FastAPI backend with async SQLAlchemy 2.0 + asyncpg, Pydantic v2 settings, error hierarchy
3. All 17 database tables + 11 enum types as SQLAlchemy models
4. Alembic async migrations
5. Health check endpoint verifying DB, Redis, MinIO connectivity
6. Next.js 15 + React 19 + Tailwind CSS 4 + shadcn/ui frontend scaffold
7. Tests proving the foundation works

## Metadata

| Field            | Value                                                          |
| ---------------- | -------------------------------------------------------------- |
| Type             | NEW_CAPABILITY                                                 |
| Complexity       | HIGH                                                           |
| Systems Affected | backend, frontend, infrastructure, database                    |
| Dependencies     | Docker, Python 3.12+, Node.js 20+, PostgreSQL 16, Redis 7     |
| Estimated Tasks  | 14                                                             |

---

## UX Design

### Before State

```
+-----------------------------------------------------------------------+
|                         REPOSITORY                                     |
|                                                                        |
|   .claude/         docs/         .gitignore      CLAUDE.md            |
|   (commands,       (PRD)                                               |
|    PRP hooks)                                                          |
|                                                                        |
|   DATA_FLOW: None. No application, no services, no database.          |
|   PAIN_POINT: Cannot start any feature development.                   |
+-----------------------------------------------------------------------+
```

### After State

```
+-----------------------------------------------------------------------+
|                         REPOSITORY                                     |
|                                                                        |
|   docker-compose.dev.yml                                               |
|       |                                                                |
|       +-- PostgreSQL :5434  <-- alembic upgrade head                  |
|       +-- Redis :6379                  |                               |
|       +-- MinIO :9000/9001             v                               |
|                              17 tables + 11 enums                      |
|                                                                        |
|   backend/                          frontend/                          |
|       app/                              src/                           |
|         main.py  -- FastAPI app           app/                         |
|         core/    -- config, middleware       layout.tsx                |
|         db/      -- session, base           globals.css               |
|         models/  -- 17 SQLAlchemy models    (auth)/ (app)/            |
|         api/routes/health.py              components/ui/               |
|         schemas/                          stores/                      |
|         services/                         hooks/                       |
|       alembic/                          package.json                   |
|       tests/test_health.py              next.config.ts                |
|       pyproject.toml                    tsconfig.json                  |
|                                                                        |
|   DATA_FLOW:                                                           |
|     docker compose up -> services ready                                |
|     alembic upgrade head -> 17 tables created                          |
|     uvicorn -> GET /api/health -> {status: healthy, checks: {db, redis, minio}}  |
|     npm run dev -> Next.js on :3001                                    |
|     npm run build -> clean build, zero errors                          |
|     pytest -> at least 1 test passes                                   |
+-----------------------------------------------------------------------+
```

### Interaction Changes
| Location | Before | After | User Impact |
|----------|--------|-------|-------------|
| `docker compose` | No compose file | 3 services running | Dev infrastructure ready |
| `GET /api/health` | No backend | Returns health status of all 3 services | API is live and verifiable |
| `alembic upgrade head` | No migrations | 17 tables + 11 enums created | Database schema ready |
| `http://localhost:3001` | No frontend | Next.js app shell renders | Frontend scaffold visible |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File | Lines | Why Read This |
|----------|------|-------|---------------|
| P0 | `CLAUDE.md` | all | Project structure, commands, architecture, mandatory rules |
| P0 | `.claude/PRPs/prds/platform/incube-platform-v1-v1.prd.md` | 200-557 | Complete database schema DDL (17 tables, 11 enums, all indexes) |
| P0 | `.claude/PRPs/prds/platform/incube-platform-v1-v1.prd.md` | 1998-2210 | Project scaffolding: folder structure, entry points, env vars, base patterns |
| P1 | `.claude/PRPs/prds/platform/incube-platform-v1-v1.prd.md` | 934-950 | Health endpoint specification |
| P1 | `.claude/PRPs/prds/platform/incube-platform-v1-v1.prd.md` | 149-200 | Tech stack decisions and Docker Compose spec |
| P1 | `.claude/PRPs/prds/platform/incube-platform-v1-v1.prd.md` | 1153-1189 | Phase validation criteria |
| P2 | `.claude/PRPs/prds/platform/incube-platform-v1-v1.prd.md` | 1206-1261 | Design tokens (colors, typography, effects) |

---

## Patterns to Mirror

### Base SQLAlchemy Model (PRD Section 16.5)
```python
# backend/app/db/base.py
import uuid
from datetime import datetime
from sqlalchemy import MetaData, func
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, server_default=func.now(), onupdate=func.now())
```

### Pydantic Settings (PRD Section 16.4)
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str
    # ...20 env vars per PRD section 16.3
```

### Error Hierarchy (PRD Section 16.5)
```python
class AppError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"

class ValidationError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"

class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"

class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
```

### Async Session Factory (Research Pattern)
```python
# backend/app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(settings.database_url, pool_size=10, pool_pre_ping=True)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### FastAPI Lifespan (Deprecated on_event pattern)
```python
# backend/app/main.py
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(title="InCube API", version="1.0.0", lifespan=lifespan)
```

### Tailwind CSS 4 + shadcn/ui Pattern
```css
/* frontend/src/app/globals.css */
@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:where(.dark, .dark *));

:root { /* design tokens */ }
.dark { /* dark mode overrides */ }

@theme inline { /* tailwind utility mappings */ }
```

---

## Files to Change

### Infrastructure
| File                             | Action | Justification                            |
| -------------------------------- | ------ | ---------------------------------------- |
| `docker-compose.dev.yml`         | CREATE | PostgreSQL 16 + Redis 7 + MinIO          |

### Backend — Core
| File                                    | Action | Justification                               |
| --------------------------------------- | ------ | ------------------------------------------- |
| `backend/pyproject.toml`                | CREATE | Python dependencies, build config, tool config |
| `backend/alembic.ini`                   | CREATE | Alembic configuration                        |
| `backend/.env.example`                  | CREATE | Environment variable template (20 vars)      |
| `backend/app/__init__.py`               | CREATE | Package init                                 |
| `backend/app/main.py`                   | CREATE | FastAPI app, lifespan, middleware, router     |
| `backend/app/core/__init__.py`          | CREATE | Package init                                 |
| `backend/app/core/config.py`            | CREATE | Pydantic BaseSettings (20 env vars)          |
| `backend/app/core/errors.py`            | CREATE | AppError hierarchy (5 error classes)          |
| `backend/app/core/middleware.py`        | CREATE | Request ID middleware, CORS config            |

### Backend — Database
| File                                    | Action | Justification                               |
| --------------------------------------- | ------ | ------------------------------------------- |
| `backend/app/db/__init__.py`            | CREATE | Package init                                 |
| `backend/app/db/session.py`             | CREATE | AsyncSession factory, engine, get_db dep     |
| `backend/app/db/base.py`               | CREATE | Base model with UUID, timestamps, naming conventions |

### Backend — Models (17 tables)
| File                                           | Action | Justification                      |
| ---------------------------------------------- | ------ | ---------------------------------- |
| `backend/app/models/__init__.py`               | CREATE | Re-exports all models (critical for Alembic autogenerate) |
| `backend/app/models/enums.py`                  | CREATE | 11 PostgreSQL enum types           |
| `backend/app/models/organization.py`           | CREATE | organizations table                |
| `backend/app/models/user.py`                   | CREATE | users table                        |
| `backend/app/models/auth_token.py`             | CREATE | auth_tokens table                  |
| `backend/app/models/goal.py`                   | CREATE | goals table                        |
| `backend/app/models/journey.py`                | CREATE | journeys table                     |
| `backend/app/models/perspective.py`            | CREATE | perspectives table                 |
| `backend/app/models/agent_session.py`          | CREATE | agent_sessions table               |
| `backend/app/models/axiom_challenge.py`        | CREATE | axiom_challenges table             |
| `backend/app/models/document.py`               | CREATE | documents table                    |
| `backend/app/models/vibe_session.py`           | CREATE | vibe_sessions table                |
| `backend/app/models/vibe_analysis.py`          | CREATE | vibe_analyses table                |
| `backend/app/models/bank_instance.py`          | CREATE | bank_instances table               |
| `backend/app/models/vdba.py`                   | CREATE | vdbas table                        |
| `backend/app/models/email_log.py`              | CREATE | email_log table                    |
| `backend/app/models/api_usage.py`              | CREATE | api_usage table                    |
| `backend/app/models/setting.py`                | CREATE | settings table                     |
| `backend/app/models/notification.py`           | CREATE | notifications table                |

### Backend — API
| File                                          | Action | Justification                       |
| --------------------------------------------- | ------ | ----------------------------------- |
| `backend/app/api/__init__.py`                 | CREATE | Package init                         |
| `backend/app/api/deps.py`                     | CREATE | Dependency injection (get_db)        |
| `backend/app/api/routes/__init__.py`          | CREATE | Package init                         |
| `backend/app/api/routes/health.py`            | CREATE | GET /api/health endpoint             |
| `backend/app/schemas/__init__.py`             | CREATE | Package init                         |
| `backend/app/schemas/health.py`               | CREATE | Health response schema               |
| `backend/app/services/__init__.py`            | CREATE | Package init                         |

### Backend — Alembic
| File                                          | Action | Justification                       |
| --------------------------------------------- | ------ | ----------------------------------- |
| `backend/alembic/env.py`                      | CREATE | Async Alembic env (imports all models) |
| `backend/alembic/script.py.mako`              | CREATE | Migration template                   |
| `backend/alembic/versions/`                   | CREATE | Initial migration (autogenerated)    |

### Backend — Tests
| File                                          | Action | Justification                       |
| --------------------------------------------- | ------ | ----------------------------------- |
| `backend/tests/__init__.py`                   | CREATE | Package init                         |
| `backend/tests/conftest.py`                   | CREATE | Test fixtures (test DB, client)      |
| `backend/tests/test_health.py`                | CREATE | Health endpoint tests                |

### Frontend
| File                                          | Action | Justification                       |
| --------------------------------------------- | ------ | ----------------------------------- |
| `frontend/package.json`                       | CREATE | Node dependencies (via npx create-next-app + shadcn init) |
| `frontend/next.config.ts`                     | CREATE | Port 3001, API rewrites              |
| `frontend/postcss.config.mjs`                 | CREATE | @tailwindcss/postcss plugin only     |
| `frontend/tsconfig.json`                      | CREATE | TypeScript config (via create-next-app) |
| `frontend/src/app/globals.css`                | CREATE | Tailwind v4 imports + design tokens  |
| `frontend/src/app/layout.tsx`                 | CREATE | Root layout (fonts, theme)           |
| `frontend/src/app/page.tsx`                   | CREATE | Landing page placeholder             |
| `frontend/src/app/(auth)/login/page.tsx`      | CREATE | Login page placeholder               |
| `frontend/src/app/(auth)/register/page.tsx`   | CREATE | Register page placeholder            |
| `frontend/src/app/(app)/layout.tsx`           | CREATE | App shell layout placeholder         |
| `frontend/src/app/(app)/dashboard/page.tsx`   | CREATE | Dashboard page placeholder           |
| `frontend/src/app/(app)/canvas/page.tsx`      | CREATE | Canvas page placeholder              |
| `frontend/src/app/(app)/bank/page.tsx`        | CREATE | Bank page placeholder                |
| `frontend/src/app/(app)/vdbas/page.tsx`       | CREATE | VDBAs page placeholder               |
| `frontend/src/app/(app)/fundamentals/page.tsx`| CREATE | Fundamentals page placeholder        |
| `frontend/src/app/(app)/settings/page.tsx`    | CREATE | Settings page placeholder            |
| `frontend/src/lib/utils.ts`                   | CREATE | Utility functions (via shadcn init)  |
| `frontend/src/types/index.ts`                 | CREATE | TypeScript type stubs                |
| `frontend/components.json`                    | CREATE | shadcn/ui config for Tailwind v4     |

---

## NOT Building (Scope Limits)

- **Authentication/JWT** — Phase 2 scope. No auth middleware, no login API, no user creation.
- **CRUD endpoints** — Phase 3 scope. Only the health endpoint in this phase.
- **AI Agent integration** — Phase 4 scope. No Claude SDK, no agent service.
- **Frontend components** — Phase 5/6 scope. Only placeholder pages with route stubs.
- **Seed data** — Not needed for Phase 1 validation. Can be added in Phase 2/3.
- **Background workers (arq)** — Phase 8+ scope. No Redis queue setup beyond Redis availability.
- **Production Docker Compose** — Only dev compose. Production deployment is Phase 14+.

---

## Step-by-Step Tasks

### Task 1: Create Docker Compose for Dev Services
**Action:** Create `docker-compose.dev.yml` with PostgreSQL 16 (port 5434), Redis 7 (port 6379), MinIO (ports 9000/9001)
**MIRROR:** PRD Section 5.2 — exact YAML spec (lines 173-199)
**Key details:**
- PostgreSQL: `postgres:16-alpine`, DB name `incube_dev`, user `incube`, password `incube_dev`, port `5434:5432`
- Redis: `redis:7-alpine`, port `6379:6379`
- MinIO: `minio/minio`, ports `9000:9000` and `9001:9001`, command `server /data --console-address ":9001"`, user `incube`, password `incube_dev`
- Named volumes: `pgdata`, `minio_data`
- Add healthchecks for all 3 services so `depends_on: condition: service_healthy` works in future phases
**VALIDATE:**
```bash
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml ps  # All 3 services healthy
docker compose -f docker-compose.dev.yml down
```

### Task 2: Scaffold Backend Python Project
**Action:** Create `backend/pyproject.toml` with all dependencies, create `.env.example`, create Python virtual environment
**Key dependencies (pin versions):**
- `fastapi>=0.128.0,<1.0.0`
- `uvicorn[standard]>=0.34.0`
- `sqlalchemy>=2.0.45,<2.1.0` (avoid 2.1 beta)
- `asyncpg>=0.30.0,<0.32.0`
- `alembic>=1.18.0,<2.0.0`
- `pydantic>=2.10.0,<3.0.0`
- `pydantic-settings>=2.12.0,<3.0.0`
- `redis>=7.0.0,<8.0.0` (NOT `aioredis` — it's abandoned)
- `miniopy-async>=1.21` (async MinIO client)
- `python-jose[cryptography]` (JWT, for Phase 2 readiness)
- `passlib[bcrypt]` (password hashing, for Phase 2 readiness)
- `httpx` (for testing)
- `python-multipart` (for file uploads)
- Dev dependencies: `ruff`, `pytest`, `pytest-asyncio`, `httpx`, `respx`
**MIRROR:** PRD Section 16.3 for env vars
**VALIDATE:**
```bash
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
```

### Task 3: Create Backend Core — Config, Errors, Middleware
**Action:** Create `backend/app/core/config.py`, `backend/app/core/errors.py`, `backend/app/core/middleware.py`
**Config:** Pydantic `Settings` class with all 20 env vars from PRD Section 16.3. Include `@property` for `async_database_url` that constructs the asyncpg connection string. Use `SettingsConfigDict(env_file=".env", extra="ignore")`.
**Errors:** `AppError` base + `NotFoundError`, `ValidationError`, `ForbiddenError`, `ConflictError` per PRD Section 16.5
**Middleware:** Request ID middleware (UUID per request, set in response `X-Request-ID` header). CORS middleware setup using `settings.cors_origins`.
**GOTCHA:** Pydantic v2 uses `model_config = ConfigDict(...)`, NOT nested `class Config`
**GOTCHA:** Fields cannot start with `model_` (Pydantic v2 reserves this prefix)
**VALIDATE:**
```bash
cd backend && source .venv/bin/activate && python -c "from app.core.config import Settings; print('Config OK')"
```

### Task 4: Create Database Session and Base Model
**Action:** Create `backend/app/db/session.py` and `backend/app/db/base.py`
**Base model:** Includes `MetaData(naming_convention=...)` for predictable constraint names (critical for Alembic). UUID primary key, `created_at` with `server_default=func.now()`, `updated_at` with `server_default=func.now()` and `onupdate=func.now()`.
**Session factory:** `create_async_engine` with `pool_size=10`, `pool_pre_ping=True`. `async_sessionmaker` with `expire_on_commit=False` (MANDATORY for async — prevents `MissingGreenlet`).
**GOTCHA:** `expire_on_commit=False` is critical — without it, accessing attributes after commit raises `MissingGreenlet`
**GOTCHA:** Naming conventions MUST be set on MetaData BEFORE any model classes are defined
**VALIDATE:**
```bash
cd backend && source .venv/bin/activate && python -c "from app.db.base import Base; from app.db.session import engine; print('DB OK')"
```

### Task 5: Create All SQLAlchemy Models (17 Tables + 11 Enums)
**Action:** Create `backend/app/models/enums.py` (11 enum types) and one file per table model (17 files). Create `backend/app/models/__init__.py` that imports ALL models (critical for Alembic autogenerate).
**MIRROR:** PRD Section 5.3 (lines 202-557) — exact SQL DDL for every table
**Enums (11):** `user_role`, `goal_type`, `journey_status`, `dimension_type`, `phase_type`, `perspective_status`, `challenge_severity`, `challenge_resolution`, `bank_type`, `api_service`, `email_template`, `notification_channel`
**Tables (17):** `organizations`, `users`, `auth_tokens`, `goals`, `journeys`, `perspectives`, `agent_sessions`, `axiom_challenges`, `documents`, `vibe_sessions`, `vibe_analyses`, `bank_instances`, `vdbas`, `email_log`, `api_usage`, `settings`, `notifications`
**Key constraints:** All foreign keys, UNIQUE constraints, CHECK constraints, partial indexes per PRD
**GOTCHA:** Every model file MUST be imported in `models/__init__.py` or Alembic will miss it and generate DROP TABLE migrations
**GOTCHA:** Use `lazy="selectin"` or `lazy="raise"` on relationships to prevent MissingGreenlet errors
**VALIDATE:**
```bash
cd backend && source .venv/bin/activate && python -c "from app.models import *; from app.db.base import Base; print(f'Tables: {len(Base.metadata.tables)}'); assert len(Base.metadata.tables) == 17"
```

### Task 6: Configure Alembic for Async
**Action:** Create `backend/alembic.ini` and `backend/alembic/env.py` (async template), `backend/alembic/script.py.mako`
**GOTCHA:** Must use async Alembic template (NOT default sync template). Use `async_engine_from_config` with `pool.NullPool`.
**GOTCHA:** `env.py` must import `Base` from `app.db.base` AND import all models from `app.models` so autogenerate detects all tables.
**GOTCHA:** Set `target_metadata = Base.metadata` in env.py
**Configuration:** `sqlalchemy.url` in alembic.ini should be overridden by env.py from `settings.database_url`
**VALIDATE:**
```bash
cd backend && source .venv/bin/activate && python -c "from alembic.config import Config; print('Alembic config OK')"
```

### Task 7: Generate Initial Migration
**Action:** Start Docker services, generate initial Alembic migration, run it
**Prereq:** Tasks 1, 4, 5, 6 complete. Docker services running.
**Steps:**
1. `docker compose -f docker-compose.dev.yml up -d`
2. `cd backend && source .venv/bin/activate`
3. Create `.env` file from `.env.example` with dev defaults
4. `alembic revision --autogenerate -m "initial_schema"`
5. Review generated migration — verify all 17 tables, 11 enums, all indexes present
6. `alembic upgrade head`
7. Verify: connect to DB and check tables exist
**VALIDATE:**
```bash
docker compose -f docker-compose.dev.yml up -d
cd backend && source .venv/bin/activate && alembic upgrade head
python -c "
import asyncio
from sqlalchemy import text
from app.db.session import engine
async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text(\"SELECT tablename FROM pg_tables WHERE schemaname='public'\"))
        tables = [r[0] for r in result.fetchall()]
        print(f'Tables in DB: {len(tables)}')
        assert len(tables) >= 17, f'Expected 17 tables, got {len(tables)}'
        print('Migration verified!')
asyncio.run(check())
"
```

### Task 8: Create FastAPI App Entry Point
**Action:** Create `backend/app/main.py` with FastAPI app, lifespan handler, middleware registration, health route inclusion
**Details:**
- Use `lifespan` context manager (NOT deprecated `@app.on_event`)
- Startup: verify DB connectivity with `SELECT 1`
- Shutdown: `await engine.dispose()`
- Register CORS middleware using `settings.cors_origins`
- Register request ID middleware
- Register error handlers for `AppError` subclasses
- Mount health route at `/api`
- Include response envelope format from PRD Section 5.4.1
**VALIDATE:**
```bash
cd backend && source .venv/bin/activate && python -c "from app.main import app; print(f'Routes: {len(app.routes)}')"
```

### Task 9: Create Health Check Endpoint
**Action:** Create `backend/app/api/routes/health.py` and `backend/app/schemas/health.py`
**MIRROR:** PRD Section 5.4.15 — exact response format
**Checks:**
1. Database: `SELECT 1` via async session, measure latency
2. Redis: `PING` command via `redis.asyncio`, measure latency
3. MinIO: `list_buckets()` via `miniopy-async`, measure latency
**Response:** `{"status": "healthy"|"degraded", "checks": {...}, "version": "1.0.0", "uptime_seconds": N}`
**Return 503** if any check fails
**VALIDATE:**
```bash
docker compose -f docker-compose.dev.yml up -d
cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8000 &
sleep 3
curl -s http://localhost:8000/api/health | python -m json.tool
kill %1
```

### Task 10: Create API Dependencies
**Action:** Create `backend/app/api/deps.py` with `get_db` dependency
**Details:** Async generator that yields an `AsyncSession`, commits on success, rolls back on exception
**VALIDATE:**
```bash
cd backend && source .venv/bin/activate && python -c "from app.api.deps import get_db; print('Deps OK')"
```

### Task 11: Create Test Infrastructure and Health Test
**Action:** Create `backend/tests/conftest.py` with test fixtures and `backend/tests/test_health.py`
**conftest.py:**
- Test database setup (use same DB for simplicity in Phase 1, or create test DB)
- Async test client using `httpx.AsyncClient`
- Use `pytest-asyncio` with `asyncio_mode = "auto"`
**test_health.py:**
- Test `GET /api/health` returns 200 when all services up
- Test response contains `status`, `checks`, `version` fields
- At minimum 1 test that passes with Docker services running
**VALIDATE:**
```bash
docker compose -f docker-compose.dev.yml up -d
cd backend && source .venv/bin/activate && pytest -v
```

### Task 12: Scaffold Next.js 15 Frontend
**Action:** Create Next.js 15 project with React 19, Tailwind CSS 4, TypeScript
**Steps:**
1. `npx create-next-app@15 frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias`
2. Configure port 3001 in `next.config.ts` (or `package.json` scripts)
3. Configure API proxy rewrites to `localhost:8000` in `next.config.ts`
4. Replace `postcss.config.mjs` — only `@tailwindcss/postcss` plugin (remove `autoprefixer`)
5. Remove `tailwind.config.ts` if generated (Tailwind v4 uses CSS-first config)
**GOTCHA:** Verify Tailwind CSS 4 is installed, NOT v3. The `@import "tailwindcss"` syntax is v4-only.
**GOTCHA:** `autoprefixer` is no longer needed — Tailwind v4 handles it internally
**VALIDATE:**
```bash
cd frontend && npm run build && npm run lint
```

### Task 13: Initialize shadcn/ui and Design System
**Action:** Initialize shadcn/ui, set up design tokens in `globals.css`, create placeholder pages
**Steps:**
1. `cd frontend && npx shadcn@latest init` — select new-york style, CSS variables, neutral base color
2. Verify `components.json` has empty `tailwind.config` field (signals Tailwind v4)
3. Install `tw-animate-css` (NOT `tailwindcss-animate` — incompatible with v4)
4. Set up `globals.css` with:
   - `@import "tailwindcss"` and `@import "tw-animate-css"`
   - `@custom-variant dark (&:where(.dark, .dark *))` for class-based dark mode
   - `:root` with InCube Space theme design tokens (PRD Section 10.1 + 10.5)
   - `.dark` class with dark mode values (Space theme IS dark by default)
   - `@theme inline` block mapping CSS vars to Tailwind utilities
   - Custom agent colors as CSS variables
5. Set up `layout.tsx` with Inter + JetBrains Mono fonts via `next/font/google`
6. Create placeholder pages for all routes: `(auth)/login`, `(auth)/register`, `(app)/dashboard`, `(app)/canvas`, `(app)/bank`, `(app)/vdbas`, `(app)/fundamentals`, `(app)/settings`
7. Create `(app)/layout.tsx` as app shell wrapper (placeholder)
8. Create `src/types/index.ts` with empty type stubs
9. Create `src/lib/utils.ts` (shadcn creates this, add `cn()` helper)
**GOTCHA:** `tailwindcss-animate` is incompatible with Tailwind v4. Use `tw-animate-css` instead.
**GOTCHA:** Font variables use `--font-inter` not `--font-sans` directly — mapped via `@theme inline`
**GOTCHA:** All shadow/rounded/blur sizes shifted down in v4 (e.g., `shadow-sm` is now `shadow-xs`)
**GOTCHA:** Default border color changed to `currentColor` — need explicit border colors
**VALIDATE:**
```bash
cd frontend && npm run build && npm run lint
```

### Task 14: Verify Full Phase 1 Validation Criteria
**Action:** Run the complete validation suite from PRD Section 8.1 Phase 1
**Steps:**
1. `docker compose -f docker-compose.dev.yml up -d` — all 3 services start
2. `cd backend && source .venv/bin/activate && alembic upgrade head` — migrations run clean
3. `uvicorn app.main:app --port 8000` — server starts
4. `curl http://localhost:8000/api/health` — returns 200 with all checks passing
5. `pytest` — at least 1 test passes
6. `ruff check .` — no lint errors
7. `cd frontend && npm run build` — clean build
8. `npm run lint` — no lint errors
**VALIDATE:**
```bash
# Full validation script
docker compose -f docker-compose.dev.yml up -d && sleep 5
cd backend && source .venv/bin/activate && alembic upgrade head && ruff check . && pytest -v
cd ../frontend && npm run lint && npm run build
echo "Phase 1 PASSED"
```

---

## Testing Strategy

### Unit Tests (Phase 1 scope)
| Test | File | What It Verifies |
|------|------|-----------------|
| Health endpoint returns 200 | `tests/test_health.py` | GET /api/health with all services up → 200, correct schema |
| Health endpoint returns 503 on failure | `tests/test_health.py` | GET /api/health with service down → 503, degraded status |
| Config loads from env | `tests/test_health.py` | Settings class loads without error |

### Edge Cases
- Health check with Redis down → status: degraded, redis check shows error
- Health check with MinIO down → status: degraded, minio check shows error
- Missing required env var → app fails fast on startup (Pydantic validation)

---

## Validation Commands

### Level 1: STATIC_ANALYSIS

Backend:
```bash
cd backend && source .venv/bin/activate && ruff check .
```

Frontend:
```bash
cd frontend && npm run lint
```

### Level 2: UNIT_TESTS

Backend:
```bash
cd backend && source .venv/bin/activate && pytest -v
```

### Level 3: FULL_SUITE

```bash
docker compose -f docker-compose.dev.yml up -d && sleep 5
cd backend && source .venv/bin/activate && alembic upgrade head && ruff check . && pytest -v
cd ../frontend && npm run lint && npm run build
```

---

## Critical Gotchas Summary

| # | Area | Gotcha | Mitigation |
|---|------|--------|------------|
| 1 | SQLAlchemy | `expire_on_commit=False` mandatory for async | Set in `async_sessionmaker()` — prevents MissingGreenlet |
| 2 | SQLAlchemy | Naming conventions must be on MetaData before models | Define in `Base` class before importing any model |
| 3 | SQLAlchemy | Lazy loading raises MissingGreenlet | Use `selectinload()` or `lazy="raise"` on relationships |
| 4 | Alembic | Must use async template | Use `async_engine_from_config` + `pool.NullPool` in env.py |
| 5 | Alembic | All models must be imported in env.py | Import `*` from `app.models` in `env.py` |
| 6 | FastAPI | `@app.on_event()` deprecated | Use `lifespan` context manager |
| 7 | FastAPI | Must dispose engine on shutdown | `await engine.dispose()` in lifespan cleanup |
| 8 | Pydantic | `orm_mode` gone, use `from_attributes=True` | Use `model_config = ConfigDict(from_attributes=True)` |
| 9 | Pydantic | Fields cannot start with `model_` | Rename any such fields |
| 10 | Redis | `aioredis` is abandoned | Use `redis.asyncio` from `redis>=7.0` |
| 11 | Tailwind | v4 uses `@import "tailwindcss"` not `@tailwind` directives | CSS-first config, no tailwind.config.js |
| 12 | Tailwind | `tailwindcss-animate` incompatible with v4 | Use `tw-animate-css` instead |
| 13 | Tailwind | Default border color changed to `currentColor` | Always specify border colors explicitly |
| 14 | Tailwind | Shadow/rounded sizes shifted down | `shadow-sm` → `shadow-xs`, `shadow` → `shadow-sm` |
| 15 | shadcn | Must leave `tailwind.config` empty in components.json | Empty string signals Tailwind v4 mode |
| 16 | Next.js 15 | `cookies()`, `headers()`, `params` are now async | Use `await` or `React.use()` |
| 17 | Next.js 15 | `forwardRef` deprecated in React 19 | `ref` is now a regular prop |
| 18 | PostCSS | Only use `@tailwindcss/postcss` plugin | Remove `autoprefixer` and `postcss-import` |

---

## Acceptance Criteria

- [x] `docker compose -f docker-compose.dev.yml up -d` starts PostgreSQL, Redis, MinIO — all healthy
- [x] `alembic upgrade head` creates all 17 tables + 11 enum types + all indexes cleanly
- [x] `GET /api/health` returns 200 with `status: "healthy"` and all 3 service checks passing
- [x] `pytest` passes with at least 1 test (3 tests pass)
- [x] `ruff check .` reports zero errors
- [x] `npm run build` completes with zero errors (13 pages generated)
- [x] `npm run lint` reports zero errors
- [x] All route placeholders render at `http://localhost:3001`
- [x] Design tokens from PRD Section 10.1 are defined in `globals.css`
- [x] Code follows all patterns specified in PRD Section 16.5

---

## Completion Checklist

- [x] Task 1: Docker Compose dev services created and verified
- [x] Task 2: Backend Python project scaffolded with all dependencies
- [x] Task 3: Core config, errors, middleware created
- [x] Task 4: Database session and base model created
- [x] Task 5: All 17 SQLAlchemy models + 11 enums created
- [x] Task 6: Alembic async configuration created
- [x] Task 7: Initial migration generated and verified (18 tables in DB incl. alembic_version)
- [x] Task 8: FastAPI app entry point with lifespan and middleware
- [x] Task 9: Health check endpoint working (DB + Redis + MinIO)
- [x] Task 10: API dependencies module created
- [x] Task 11: Test infrastructure + health test passing (3/3 tests pass)
- [x] Task 12: Next.js 15 frontend scaffolded with Tailwind CSS 4
- [x] Task 13: shadcn/ui initialized, design tokens, placeholder pages
- [x] Task 14: Full validation suite passes (Level 1 + 2 + 3)
- [x] Level 1: Static analysis passes (ruff + eslint)
- [x] Level 2: Unit tests pass (pytest — 3/3)
- [x] Level 3: Full test suite + build succeeds
- [x] All acceptance criteria met
