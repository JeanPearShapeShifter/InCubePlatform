---
description: "Deploy InCube Platform to production"
---

# Production Deployment Command

Deploy InCube Platform to production using Docker containers.

## Usage

```
/deploy
```

## Project Selection

**FIRST**: Ask the user which component to deploy:
- **backend** - FastAPI API server
- **frontend** - Next.js web application
- **all** - Deploy everything

Example: "Which component do you want to deploy? (backend/frontend/all)"

## Server Information

| Detail | Value |
|--------|-------|
| **Production URL** | TBD |
| **VPS IP Address** | TBD |
| **SSH User** | root |
| **Docker Status** | Required |
| **Reverse Proxy** | Caddy (automatic SSL) |

## Deployment Directories

| Component | Port | Container Name | VPS Directory |
|-----------|------|----------------|---------------|
| **backend** | 8000 | incube-backend | /opt/incube/backend |
| **frontend** | 3001 | incube-frontend | /opt/incube/frontend |
| **postgresql** | 5432 | incube-db | /opt/incube/data |
| **redis** | 6379 | incube-redis | Docker volume |
| **minio** | 9000 | incube-minio | /opt/incube/storage |

## What It Does

1. **Pre-Flight Checks**: Validates SSH connectivity and Docker status
2. **Disk Space Check**: Ensures sufficient space and cleans old backups
3. **Backup Current Version**: Creates backup before deployment (keeps last 5)
4. **Environment Validation**: Ensures all required variables are set
5. **Build & Deploy**: Copies files to server, builds Docker images, starts services
6. **Health Verification**: Confirms all services are running
7. **Caddy Configuration**: Ensures reverse proxy is properly configured
8. **Cleanup**: Removes old Docker images and temporary files

## Instructions for Claude

Execute the following steps in order. DO NOT skip any step.

### Step 1: Pre-Flight Validation

```bash
# Test SSH connectivity
ssh -o ConnectTimeout=10 root@<PRODUCTION_HOST> "echo 'SSH connection successful'"

# Check Docker
ssh root@<PRODUCTION_HOST> "docker --version && docker compose version"
```

### Step 2: Disk Space Check

```bash
ssh root@<PRODUCTION_HOST> "df -h / && du -sh /root/backups/ 2>/dev/null || echo 'No backups'"
```

### Step 3: Backup Current Deployment

```bash
ssh root@<PRODUCTION_HOST> 'bash -s' << 'BACKUP_SCRIPT'
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
for COMPONENT in backend frontend; do
  BACKUP_DIR="/root/backups/incube-${COMPONENT}"
  SOURCE_DIR="/opt/incube/${COMPONENT}"
  mkdir -p "$BACKUP_DIR"
  if [ -d "$SOURCE_DIR" ]; then
    tar -czf "${BACKUP_DIR}/backup-${TIMESTAMP}.tar.gz" -C "$(dirname $SOURCE_DIR)" "$(basename $SOURCE_DIR)"
    # Keep only last 5 backups
    cd "$BACKUP_DIR" && ls -1t backup-*.tar.gz | tail -n +6 | xargs -r rm
  fi
done
BACKUP_SCRIPT
```

### Step 4: Environment Validation

**Required Variables:**

Backend (`.env.production`):
- `DATABASE_URL` - PostgreSQL connection string
- `ANTHROPIC_API_KEY` - Claude API key
- `JWT_SECRET` - Authentication secret
- `REDIS_URL` - Redis connection string
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
- `RESEND_API_KEY` - Email service key
- `CORS_ORIGINS` - Allowed frontend origins

Frontend (`.env.production`):
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NODE_ENV=production`

### Step 5: Execute Deployment

#### Backend:
```bash
rsync -azP --delete \
    --exclude '.venv' --exclude '.git' --exclude '__pycache__' \
    --exclude '.env' --exclude '.pytest_cache' --exclude '.ruff_cache' \
    backend/ root@<PRODUCTION_HOST>:/opt/incube/backend/src/

ssh root@<PRODUCTION_HOST> 'bash -s' << 'DEPLOY'
cd /opt/incube/backend
docker compose down 2>/dev/null || true
docker compose build --no-cache
docker compose up -d
sleep 15
docker compose exec backend alembic upgrade head
docker compose ps
docker compose logs --tail=30
DEPLOY
```

#### Frontend:
```bash
rsync -azP --delete \
    --exclude 'node_modules' --exclude '.next' --exclude '.git' \
    frontend/ root@<PRODUCTION_HOST>:/opt/incube/frontend/src/

ssh root@<PRODUCTION_HOST> 'bash -s' << 'DEPLOY'
cd /opt/incube/frontend
docker compose down 2>/dev/null || true
docker compose build --no-cache
docker compose up -d
sleep 15
docker compose ps
docker compose logs --tail=30
DEPLOY
```

### Step 6: Health Verification

```bash
ssh root@<PRODUCTION_HOST> "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep incube"
ssh root@<PRODUCTION_HOST> "curl -sf http://localhost:8000/api/health && echo 'Backend: OK'"
ssh root@<PRODUCTION_HOST> "curl -sf http://localhost:3001/ > /dev/null && echo 'Frontend: OK'"
```

### Step 7: Cleanup

```bash
ssh root@<PRODUCTION_HOST> "docker image prune -f && docker builder prune -f && df -h /"
```

## Rollback

```bash
# List backups
ssh root@<PRODUCTION_HOST> "ls -lht /root/backups/incube-*/"

# Restore (replace TIMESTAMP)
ssh root@<PRODUCTION_HOST> "docker compose -f /opt/incube/backend/docker-compose.yml down"
ssh root@<PRODUCTION_HOST> "rm -rf /opt/incube/backend"
ssh root@<PRODUCTION_HOST> "tar -xzf /root/backups/incube-backend/backup-TIMESTAMP.tar.gz -C /opt/incube/"
ssh root@<PRODUCTION_HOST> "cd /opt/incube/backend && docker compose up -d"
```

## Post-Deployment Checklist

- [ ] All containers running
- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] SSL certificate valid
- [ ] No errors in logs
- [ ] Disk space > 2GB free

**NOTE**: Production server details (IP, domain) to be configured once infrastructure is provisioned.
