---
name: startup
description: Start InCube Portal development services in background tmux sessions. Supports backend (port 8000), frontend (port 3001), or all services including Docker infrastructure.
argument-hint: [backend|frontend|all]
allowed-tools: Bash(tmux *), Bash(docker *)
---


# Start Workspace

High-level orchestrator for starting InCube Portal development servers.

## Usage

```
/startup
```

## Workspace Selection

**Ask the user which workspace to start:**

1. **backend** - FastAPI backend (http://localhost:8000)
2. **frontend** - Next.js frontend (http://localhost:3001)
3. **all** - Start all services (Docker + backend + frontend)

Example: "Which workspace(s) do you want to start? (backend/frontend/all)"

## What It Does

1. Starts selected services in detached tmux sessions
2. **Returns control to terminal immediately** - services run in background
3. You can continue working while services run
4. Services run until manually stopped
5. Logs are accessible via tmux capture

## Service Ports

| Service | Port | tmux Session | Description |
|---------|------|--------------|-------------|
| PostgreSQL (Docker) | 5435 | N/A (Docker) | Primary database |
| Redis (Docker) | 6380 | N/A (Docker) | Cache and job queue |
| MinIO (Docker) | 9002/9003 | N/A (Docker) | S3-compatible file storage |
| Backend (FastAPI) | 8000 | incube-backend | API server with AI agents |
| Frontend (Next.js) | 3001 | incube-frontend | Web application |

## Instructions for Claude

### Prerequisites Check

```bash
# Check tmux is installed
which tmux || echo "ERROR: tmux not installed. Run: sudo apt install tmux"

# Check npm is available
npm --version

# Check Python is available (for backend)
python3 --version

# Check Docker is available (for databases)
docker --version

# Check dependencies installed
ls -la /home/wkoch/github-repos/incube-portal/backend/.venv/bin/activate 2>/dev/null || echo "WARNING: Backend venv not found. Run /install first."
ls -la /home/wkoch/github-repos/incube-portal/frontend/node_modules/ 2>/dev/null | head -5 || echo "WARNING: Frontend node_modules not found. Run /install first."
```

If dependencies not installed, run `/install` first.

### Start Backend Only

```bash
echo "=== InCube Backend Startup ==="
echo ""

# 1. Start dev services (PostgreSQL + Redis + MinIO)
echo "Step 1/3: Starting dev services (PostgreSQL + Redis + MinIO)..."
cd /home/wkoch/github-repos/incube-portal && docker compose -f docker-compose.dev.yml up -d
sleep 5

# 2. Run database migrations
echo ""
echo "Step 2/3: Running database migrations..."
cd /home/wkoch/github-repos/incube-portal/backend && source .venv/bin/activate && alembic upgrade head

# 3. Start backend in tmux
echo ""
echo "Step 3/3: Starting FastAPI backend..."
tmux kill-session -t incube-backend 2>/dev/null || true
tmux new-session -d -s incube-backend -c /home/wkoch/github-repos/incube-portal/backend \
  "source .venv/bin/activate && uvicorn app.main:app --reload --port 8000 2>&1 | tee /tmp/incube-backend.log"

sleep 3

# Status report
echo ""
echo "=== Startup Status ==="
echo ""

# Backend status
if tmux has-session -t incube-backend 2>/dev/null; then
  echo "[OK] Backend: http://localhost:8000"
  echo "[OK] API Docs: http://localhost:8000/docs"
else
  echo "[!!] Backend: FAILED TO START"
fi

# Docker status
if docker ps | grep -q incube; then
  echo "[OK] Databases: PostgreSQL (5435) + Redis (6380)"
  echo "[OK] MinIO: http://localhost:9003 (console)"
else
  echo "[!!] Docker services: NOT RUNNING"
fi

echo ""
echo "=== Quick Commands ==="
echo "View backend logs:  tmux attach -t incube-backend"
echo ""
```

### Start Frontend Only

```bash
# Kill existing session if running
tmux kill-session -t incube-frontend 2>/dev/null || true

# Start frontend in tmux
tmux new-session -d -s incube-frontend -c /home/wkoch/github-repos/incube-portal/frontend \
  "npm run dev 2>&1 | tee /tmp/incube-frontend.log"

# Wait for startup
sleep 3

# Check if running
if tmux has-session -t incube-frontend 2>/dev/null; then
  echo "Frontend started successfully on http://localhost:3001"
  tmux capture-pane -t incube-frontend -p -S -20 | tail -10
else
  echo "ERROR: Frontend failed to start"
  cat /tmp/incube-frontend.log | tail -20
fi
```

### Start All Services

```bash
echo "=== InCube Portal Full Startup ==="
echo ""

# 1. Start dev services (PostgreSQL + Redis + MinIO)
echo "Step 1/4: Starting dev services (PostgreSQL + Redis + MinIO)..."
cd /home/wkoch/github-repos/incube-portal && docker compose -f docker-compose.dev.yml up -d
sleep 5

# 2. Run database migrations
echo ""
echo "Step 2/4: Running database migrations..."
cd /home/wkoch/github-repos/incube-portal/backend && source .venv/bin/activate && alembic upgrade head

# 3. Start backend in tmux
echo ""
echo "Step 3/4: Starting FastAPI backend..."
tmux kill-session -t incube-backend 2>/dev/null || true
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
tmux new-session -d -s incube-backend -c /home/wkoch/github-repos/incube-portal/backend \
  "source .venv/bin/activate && uvicorn app.main:app --reload --port 8000 2>&1 | tee /tmp/incube-backend.log"

# 4. Start frontend in tmux
echo ""
echo "Step 4/4: Starting Next.js frontend..."
tmux kill-session -t incube-frontend 2>/dev/null || true
lsof -ti:3001 2>/dev/null | xargs kill -9 2>/dev/null || true
tmux new-session -d -s incube-frontend -c /home/wkoch/github-repos/incube-portal/frontend \
  "npm run dev 2>&1 | tee /tmp/incube-frontend.log"

sleep 3

# Final status report
echo ""
echo "=== Startup Status ==="
echo ""

# Backend status
if tmux has-session -t incube-backend 2>/dev/null; then
  echo "[OK] Backend: http://localhost:8000"
  echo "[OK] API Docs: http://localhost:8000/docs"
else
  echo "[!!] Backend: FAILED TO START"
fi

# Frontend status
if tmux has-session -t incube-frontend 2>/dev/null; then
  echo "[OK] Frontend: http://localhost:3001"
else
  echo "[!!] Frontend: FAILED TO START"
fi

# Docker status
if docker ps | grep -q incube; then
  echo "[OK] Databases: PostgreSQL (5435) + Redis (6380)"
  echo "[OK] MinIO: http://localhost:9003 (console)"
else
  echo "[!!] Docker services: NOT RUNNING"
fi

echo ""
echo "=== Quick Commands ==="
echo "View backend logs:  tmux attach -t incube-backend"
echo "View frontend logs: tmux attach -t incube-frontend"
echo ""
```

## Available Management Commands

**Check status of all services:**
```bash
# List all incube tmux sessions
tmux list-sessions | grep incube

# Or check with ports
lsof -i :8000 2>/dev/null | grep LISTEN && echo "Backend: Running" || echo "Backend: Not running"
lsof -i :3001 2>/dev/null | grep LISTEN && echo "Frontend: Running" || echo "Frontend: Not running"
```

**Stop all services:**
```bash
# Kill all incube tmux sessions
tmux kill-session -t incube-backend 2>/dev/null || true
tmux kill-session -t incube-frontend 2>/dev/null || true

# Stop Docker dev services
cd /home/wkoch/github-repos/incube-portal && docker compose -f docker-compose.dev.yml down 2>/dev/null || true

echo "All services stopped"
```

**Stop specific service:**
```bash
# Stop backend only
tmux kill-session -t incube-backend

# Stop frontend only
tmux kill-session -t incube-frontend

# Stop Docker services only
cd /home/wkoch/github-repos/incube-portal && docker compose -f docker-compose.dev.yml down
```

## Viewing Logs

**Attach to service logs** (Ctrl+B then D to detach):
```bash
# Backend
tmux attach -t incube-backend

# Frontend
tmux attach -t incube-frontend
```

**Capture logs without attaching:**
```bash
# Last 100 lines from any service
tmux capture-pane -t incube-backend -p -S -100
tmux capture-pane -t incube-frontend -p -S -100
```

**Filter logs:**
```bash
# Errors only
tmux capture-pane -t incube-backend -p -S -1000 | grep -i 'error\|ERROR'

# API requests (backend)
tmux capture-pane -t incube-backend -p -S -500 | grep -i 'api\|POST\|GET'
```

## Requirements

- tmux must be installed (`sudo apt install tmux`)
- Node.js 18+ installed
- Python 3.12+ installed (for backend)
- Docker installed (for databases)
- Backend dependencies installed (`cd backend && python3 -m venv .venv && pip install -e ".[dev]"`)
- Frontend dependencies installed (`cd frontend && npm install`)

## Troubleshooting

If the command fails:

1. **Check tmux is installed:**
   ```bash
   which tmux
   ```

2. **Check port is free:**
   ```bash
   lsof -ti:8000  # Backend port
   lsof -ti:3001  # Frontend port
   ```

3. **Check dependencies are installed:**
   ```bash
   cd /home/wkoch/github-repos/incube-portal/backend && source .venv/bin/activate && pip list | head -20
   cd /home/wkoch/github-repos/incube-portal/frontend && npm ls --depth=0
   ```

4. **View error logs:**
   ```bash
   cat /tmp/incube-backend.log | tail -50
   cat /tmp/incube-frontend.log | tail -50
   ```

5. **Kill zombie processes:**
   ```bash
   # Find and kill processes on specific ports
   lsof -ti:8000 | xargs kill -9
   lsof -ti:3001 | xargs kill -9
   ```

## Why Non-Blocking?

The user works in Claude Code within their terminal. If startup blocks, they can't:
- Continue working on other tasks
- Run other commands
- Use the terminal while services run

**Solution**: Services run in background tmux sessions, terminal is immediately available.

Each service logs to both:
- tmux session (accessible via attach)
- Log file (accessible via cat/tail)

This allows full debugging capabilities while maintaining non-blocking operation.
