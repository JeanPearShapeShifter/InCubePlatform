---
description: "Install InCube Platform dependencies"
---

# Install Workspace

Install InCube Platform dependencies for development.

## Workspace Selection

**Ask the user which workspace to install:**

1. **backend** - FastAPI backend (Python + Docker services)
2. **frontend** - Next.js frontend (Node.js)
3. **all** - Install everything

Example: "Which workspace do you want to install? (backend/frontend/all)"

## Installation Instructions

### If backend selected:
```bash
# Create virtualenv and install Python dependencies
cd /home/wkoch/github-repos/incube-portal/backend && python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"

# Copy environment file (if not already present)
cd /home/wkoch/github-repos/incube-portal/backend && cp -n .env.example .env 2>/dev/null || true

# Start dev services (PostgreSQL + Redis + MinIO)
cd /home/wkoch/github-repos/incube-portal && docker compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
sleep 5

# Run database migrations
cd /home/wkoch/github-repos/incube-portal/backend && source .venv/bin/activate && alembic upgrade head
```

### If frontend selected:
```bash
cd /home/wkoch/github-repos/incube-portal/frontend && npm install
```

### If all selected:
Execute each in order:
1. Backend venv: `cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`
2. Backend env: `cd backend && cp -n .env.example .env`
3. Docker services: `docker compose -f docker-compose.dev.yml up -d && sleep 5`
4. Migrations: `cd backend && source .venv/bin/activate && alembic upgrade head`
5. Frontend: `cd frontend && npm install`

## Quick Reference

| Workspace | Type | Key Dependencies |
|-----------|------|------------------|
| backend | FastAPI + SQLAlchemy | Python 3.12+, Docker |
| frontend | Next.js 15 + React 19 | Node.js 18+, npm |
| infrastructure | PostgreSQL + Redis + MinIO | Docker |

## Notes

- Backend requires Python 3.12+ and Docker (for PostgreSQL, Redis, MinIO)
- Dev PostgreSQL exposes on host port **5434** (not 5432) to avoid conflicts
- MinIO console available at http://localhost:9001 (incube/incube_dev)
- Frontend requires Node.js 18+
