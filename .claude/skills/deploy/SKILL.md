---
name: deploy
description: Deploy InCube Platform to production on Motion Mind Linode VPS using Docker containers with Caddy reverse proxy. Handles backup, build, migrations, health checks, and cleanup.
disable-model-invocation: true
---


# Production Deployment Command

Deploy InCube Platform to the Motion Mind Linode VPS using Docker containers with Caddy reverse proxy.

## Usage

```
/deploy
```

## Server Information

| Detail | Value |
|--------|-------|
| **Production URL** | https://incube.motionmind.antikythera.co.za |
| **VPS IP Address** | 159.223.208.109 |
| **SSH User** | root |
| **SSH Command** | `ssh root@159.223.208.109` |
| **Docker Status** | Installed and running |
| **Reverse Proxy** | Caddy (existing on server, Docker container) |
| **Docker Network** | `n8n-docker-caddy_motionmind-network` |
| **Install Directory** | `/mnt/motionmind_volume/incube/repo` |

## Deployment Layout

| Container | Image | Port (internal) | VPS Data Directory |
|-----------|-------|------------------|-------------------|
| `incube-postgres` | postgres:16-alpine | 5432 | `/mnt/motionmind_volume/incube/pgdata` |
| `incube-redis` | redis:7-alpine | 6379 | Ephemeral |
| `incube-backend` | Built from `deploy/Dockerfile.backend` | 8000 | -- |
| `incube-frontend` | Built from `deploy/Dockerfile.frontend` | 3001 | -- |
| `incube-minio` | minio/minio | 9000 | `/mnt/motionmind_volume/incube/minio_data` |
| `caddy` | *(existing, shared)* | 80/443 | Routes `incube.motionmind.antikythera.co.za` |

All containers join the external `n8n-docker-caddy_motionmind-network`. No ports are exposed to host -- Caddy handles all external traffic.

## What It Does

1. **Pre-Flight Checks**: Validates SSH connectivity and Docker status
2. **Disk Space Check**: Ensures sufficient space and cleans old images
3. **Backup Current Version**: Creates backup before deployment (keeps last 5)
4. **Code Preparation**: Ensures all changes are committed and pushed
5. **Environment Validation**: Ensures all required variables are set
6. **Build & Deploy**: Pulls code on server, builds Docker images, starts services
7. **Database Migrations**: Runs Alembic migrations
8. **MinIO Bucket**: Ensures `incube-documents` bucket exists
9. **Caddy Configuration**: Ensures reverse proxy is properly configured
10. **Health Verification**: Confirms all services are running
11. **Cleanup**: Removes old Docker images and temporary files

## Instructions for Claude

Execute ALL steps in order without pausing. The entire flow should complete in one go. Do NOT stop to ask questions between steps.

### Step 1: Pre-Flight Validation

**Verify SSH access and Docker:**
```bash
ssh -o ConnectTimeout=10 root@159.223.208.109 "echo 'SSH connection successful' && docker --version && docker compose version"
```

**If SSH fails, STOP and tell the user to check connectivity.**

### Step 2: Disk Space Check and Cleanup

**CRITICAL**: Check disk space and clean up to prevent disk full issues.

```bash
# Check disk space on production server
ssh root@159.223.208.109 "df -h /mnt/motionmind_volume"

# Check Docker disk usage
ssh root@159.223.208.109 "docker system df"
```

**Clean up old Docker images:**
```bash
ssh root@159.223.208.109 "docker image prune -f"
```

**If disk space is critically low (< 2GB free), STOP and alert user:**
```bash
ssh root@159.223.208.109 'bash -s' << 'CHECK_SPACE'
FREE_SPACE=$(df /mnt/motionmind_volume | awk 'NR==2 {print $4}')
FREE_GB=$((FREE_SPACE / 1024 / 1024))

if [ $FREE_GB -lt 2 ]; then
  echo "ERROR: Insufficient disk space! Only ${FREE_GB}GB free."
  echo "Manual cleanup required before deployment."
  echo "Run: docker system prune -a -f"
  exit 1
else
  echo "OK: ${FREE_GB}GB free space available."
fi
CHECK_SPACE
```

### Step 3: Backup Current Deployment

**Create backup of current deployment before making changes.**

```bash
ssh root@159.223.208.109 'bash -s' << 'BACKUP_SCRIPT'
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/mnt/motionmind_volume/incube/backups"
SOURCE_DIR="/mnt/motionmind_volume/incube/repo"

mkdir -p "$BACKUP_DIR"

if [ -d "$SOURCE_DIR/.git" ]; then
  CURRENT_COMMIT=$(cd "$SOURCE_DIR" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  echo "Current deployed commit: $CURRENT_COMMIT"

  # Backup database
  if docker exec incube-postgres pg_isready -U incube -d incube >/dev/null 2>&1; then
    echo "Creating database backup..."
    docker exec incube-postgres pg_dump -U incube incube | gzip > "${BACKUP_DIR}/db-${TIMESTAMP}.sql.gz"
    echo "Database backup: $(du -h "${BACKUP_DIR}/db-${TIMESTAMP}.sql.gz" | cut -f1)"
  fi

  # Keep only last 5 database backups
  cd "$BACKUP_DIR" && ls -1t db-*.sql.gz 2>/dev/null | tail -n +6 | xargs -r rm -v
else
  echo "No existing deployment found - skipping backup (first deployment)"
fi
BACKUP_SCRIPT
```

### Step 4: Code Preparation

**Ensure all changes are committed and pushed:**
```bash
git status
git diff --stat
```

**If there are uncommitted changes, STOP and tell the user to run `/commit` first.**

**Verify code is pushed to GitHub:**
```bash
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "none")
echo "Local:  $LOCAL"
echo "Remote: $REMOTE"
```

**If local and remote differ, STOP and tell the user to run `/commit` first.**

### Step 5: Environment Validation

**Check .env.production exists on the server:**
```bash
ssh root@159.223.208.109 'bash -s' << 'SCRIPT'
ENV_FILE="/mnt/motionmind_volume/incube/repo/deploy/.env.production"
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE does not exist."
    echo "Create it from .env.production.example and fill in real values."
    exit 1
fi
echo "-> .env.production exists"
# Validate required keys are set (not placeholder values)
for KEY in POSTGRES_PASSWORD JWT_SECRET ANTHROPIC_API_KEY MINIO_ACCESS_KEY MINIO_SECRET_KEY; do
    VAL=$(grep "^${KEY}=" "$ENV_FILE" | cut -d= -f2-)
    if [ -z "$VAL" ] || echo "$VAL" | grep -qi "CHANGE_ME\|REPLACE_ME"; then
        echo "WARNING: $KEY is not configured in .env.production"
    else
        echo "  $KEY: set"
    fi
done
SCRIPT
```

**If .env.production is missing, STOP and tell the user to create it on the server:**
```
ssh root@159.223.208.109
cp /mnt/motionmind_volume/incube/repo/deploy/.env.production.example /mnt/motionmind_volume/incube/repo/deploy/.env.production
nano /mnt/motionmind_volume/incube/repo/deploy/.env.production
```

### Step 6: Pull Latest Code on Server

```bash
ssh root@159.223.208.109 'bash -s' << 'SCRIPT'
set -e
INSTALL_DIR="/mnt/motionmind_volume/incube"
REPO_URL="https://github.com/JeanPearShapeShifter/InCubePlatform.git"

if [ -d "$INSTALL_DIR/repo/.git" ]; then
    echo "-> Pulling latest..."
    cd "$INSTALL_DIR/repo"
    git fetch origin
    git reset --hard origin/main
else
    echo "-> Cloning..."
    mkdir -p "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR/repo"
fi
echo "-> HEAD: $(cd $INSTALL_DIR/repo && git log --oneline -1)"
SCRIPT
```

### Step 7: Build and Deploy Containers

```bash
ssh root@159.223.208.109 'bash -s' << 'SCRIPT'
set -e
cd /mnt/motionmind_volume/incube/repo

echo "=== Stopping existing containers ==="
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production down 2>/dev/null || true

echo "=== Building Docker images ==="
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production build --no-cache

echo "=== Starting services ==="
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production up -d

echo "=== Waiting for services to start ==="
sleep 15

echo "=== Container status ==="
docker compose -f deploy/docker-compose.prod.yml ps
SCRIPT
```

### Step 8: Run Database Migrations

```bash
ssh root@159.223.208.109 'bash -s' << 'SCRIPT'
set -e
echo "-> Waiting for PostgreSQL..."
for i in $(seq 1 30); do
    if docker exec incube-postgres pg_isready -U incube -d incube >/dev/null 2>&1; then
        echo "  PostgreSQL ready."
        break
    fi
    sleep 2
done
echo "-> Running Alembic migrations..."
docker exec incube-backend alembic upgrade head
SCRIPT
```

### Step 9: Ensure MinIO Bucket

```bash
ssh root@159.223.208.109 'docker exec incube-backend python -c "
import asyncio
from miniopy_async import Minio
import os

async def ensure_bucket():
    client = Minio(
        os.environ[\"MINIO_ENDPOINT\"],
        access_key=os.environ[\"MINIO_ACCESS_KEY\"],
        secret_key=os.environ[\"MINIO_SECRET_KEY\"],
        secure=False,
    )
    bucket = os.environ.get(\"MINIO_BUCKET\", \"incube-documents\")
    if not await client.bucket_exists(bucket):
        await client.make_bucket(bucket)
        print(f\"  Created bucket: {bucket}\")
    else:
        print(f\"  Bucket exists: {bucket}\")

asyncio.run(ensure_bucket())
"'
```

### Step 10: Configure Caddy (First Deploy Only)

```bash
ssh root@159.223.208.109 'bash -s' << 'SCRIPT'
CADDY_CONFIG="/root/n8n-docker-caddy/caddy_config/Caddyfile"
DOMAIN="incube.motionmind.antikythera.co.za"

if grep -q "$DOMAIN" "$CADDY_CONFIG" 2>/dev/null; then
    echo "-> Caddy already configured for $DOMAIN"
else
    echo "-> Adding InCube block to Caddyfile..."
    cat >> "$CADDY_CONFIG" <<'CADDYEOF'

incube.motionmind.antikythera.co.za {
    handle /api/* {
        reverse_proxy incube-backend:8000
    }
    handle {
        reverse_proxy incube-frontend:3001
    }
}
CADDYEOF
    echo "-> Reloading Caddy..."
    docker exec $(docker ps -q -f name=caddy) caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile 2>/dev/null \
        || echo "  WARNING: Could not auto-reload Caddy. Reload manually."
fi
SCRIPT
```

### Step 11: Health Verification

**Execute health checks to verify deployment:**

```bash
# Check container status on server
ssh root@159.223.208.109 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep incube"

# Check backend health (internal)
ssh root@159.223.208.109 "docker exec incube-backend python -c \"import httpx; r = httpx.get('http://localhost:8000/api/health'); print(f'Backend: {r.status_code}'); assert r.status_code == 200\""

# Check frontend (internal)
ssh root@159.223.208.109 "docker exec incube-frontend wget -q -O /dev/null http://localhost:3001/ && echo 'Frontend: OK' || echo 'Frontend: FAILED'"

# Check recent logs for errors
ssh root@159.223.208.109 "docker logs incube-backend --tail=20 2>&1 | grep -i error || echo 'Backend: No errors'"
ssh root@159.223.208.109 "docker logs incube-frontend --tail=20 2>&1 | grep -i error || echo 'Frontend: No errors'"

# Test public URL (may fail if DNS not yet propagated)
curl -sf https://incube.motionmind.antikythera.co.za/api/health && echo "Public API: OK" || echo "Public API: Check DNS/Caddy"
curl -sf -o /dev/null -w '%{http_code}' https://incube.motionmind.antikythera.co.za/ && echo "Public Frontend: OK" || echo "Public Frontend: Check DNS/Caddy"
```

**Expected Results:**
- All containers show status "Up" or "Up (healthy)"
- Backend health check returns 200
- Frontend loads correctly
- Caddy automatically handles SSL via Let's Encrypt

### Step 12: Post-Deployment Cleanup

```bash
# Remove dangling images (from previous builds)
ssh root@159.223.208.109 "docker image prune -f"

# Remove unused build cache
ssh root@159.223.208.109 "docker builder prune -f --filter 'until=24h'"

# Show disk space after deployment
ssh root@159.223.208.109 "df -h /mnt/motionmind_volume"

# Show Docker disk usage
ssh root@159.223.208.109 "docker system df"
```

### Step 13: Report

Report to the user:
- Deployed commit hash and message
- Container statuses (all should be "Up")
- Health check results
- URL: `https://incube.motionmind.antikythera.co.za`
- Any warnings (DNS not propagated, .env.production keys missing, etc.)

## First-Time Setup Checklist

If this is the first deployment, remind the user:

1. **DNS**: Ensure A record `incube.motionmind.antikythera.co.za` -> `159.223.208.109` exists (or wildcard `*.motionmind.antikythera.co.za`)
2. **Secrets**: Create `.env.production` on the server -- generate all credentials fresh with `openssl rand -hex`
3. **ANTHROPIC_API_KEY**: Add the API key to `.env.production` if AI agent features are needed

## Common Issues & Solutions

### Issue 1: Disk Space Full

**Symptom**: Deployment fails with "No space left on device"

**Solution**:
```bash
# Clean up Docker (aggressive)
ssh root@159.223.208.109 "docker system prune -a -f --volumes"

# Clean up old database backups (keep only last 3 in emergency)
ssh root@159.223.208.109 "cd /mnt/motionmind_volume/incube/backups && ls -1t db-*.sql.gz | tail -n +4 | xargs -r rm -v"
```

### Issue 2: Docker Build Fails

**Symptom**: Build fails with missing files or dependency errors

**Solution**:
```bash
# Verify directory structure on server
ssh root@159.223.208.109 "ls -la /mnt/motionmind_volume/incube/repo/deploy/"

# Rebuild with fresh pull
ssh root@159.223.208.109 "cd /mnt/motionmind_volume/incube/repo && git fetch origin && git reset --hard origin/main"
```

### Issue 3: Database Connection Issues

**Symptom**: Backend fails to connect to PostgreSQL

**Solution**:
```bash
ssh root@159.223.208.109 "docker exec incube-postgres psql -U incube -d incube -c 'SELECT 1'"
ssh root@159.223.208.109 "docker logs incube-postgres --tail=30"
```

### Issue 4: Caddy Not Routing

**Symptom**: Public URL returns 502 or connection refused

**Solution**:
```bash
# Validate Caddy config
ssh root@159.223.208.109 "docker exec \$(docker ps -q -f name=caddy) caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile"

# Check Caddy logs
ssh root@159.223.208.109 "docker logs \$(docker ps -q -f name=caddy) --tail=30"

# Verify containers are on the same network
ssh root@159.223.208.109 "docker network inspect n8n-docker-caddy_motionmind-network --format '{{range .Containers}}{{.Name}} {{end}}'"
```

### Issue 5: SSL Certificate Issues

**Symptom**: Browser shows SSL warning

**Solution**:
```bash
# Check Caddy certificate status
ssh root@159.223.208.109 "docker exec \$(docker ps -q -f name=caddy) caddy list-certificates"

# Verify DNS points to server
dig incube.motionmind.antikythera.co.za +short
```

## Rollback Procedure

```bash
# 1. List available database backups
ssh root@159.223.208.109 "ls -lht /mnt/motionmind_volume/incube/backups/"

# 2. Roll back to a previous commit
ssh root@159.223.208.109 'bash -s' << 'SCRIPT'
cd /mnt/motionmind_volume/incube/repo
git log --oneline -10  # Find the commit to roll back to
git reset --hard <COMMIT_HASH>
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production down
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production up -d --build
sleep 15
docker exec incube-backend alembic upgrade head
SCRIPT

# 3. Restore database from backup (if needed)
ssh root@159.223.208.109 "gunzip -c /mnt/motionmind_volume/incube/backups/db-TIMESTAMP.sql.gz | docker exec -i incube-postgres psql -U incube -d incube"
```

## Useful Management Commands

**View Live Logs:**
```bash
ssh root@159.223.208.109 "docker compose -f /mnt/motionmind_volume/incube/repo/deploy/docker-compose.prod.yml logs -f"
```

**Restart Services:**
```bash
ssh root@159.223.208.109 "docker compose -f /mnt/motionmind_volume/incube/repo/deploy/docker-compose.prod.yml restart"
```

**Check Resource Usage:**
```bash
ssh root@159.223.208.109 "docker stats --no-stream | grep incube"
ssh root@159.223.208.109 "df -h /mnt/motionmind_volume"
```

**Rebuild from Scratch:**
```bash
ssh root@159.223.208.109 'bash -s' << 'SCRIPT'
cd /mnt/motionmind_volume/incube/repo
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production down -v
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production up -d --build
sleep 15
docker exec incube-backend alembic upgrade head
SCRIPT
```

## Post-Deployment Checklist

- [ ] All containers running (docker ps shows healthy status)
- [ ] Backend health check passes (`/api/health` returns 200)
- [ ] Frontend loads at https://incube.motionmind.antikythera.co.za
- [ ] SSL certificate is valid (green padlock)
- [ ] No errors in container logs
- [ ] Disk space > 2GB free on volume
- [ ] Docker images cleaned up

## Security Reminders

- Never commit `deploy/.env.production` with real secrets to Git
- `.env.production` is gitignored -- secrets only exist on the server
- Rotate JWT_SECRET and API keys regularly
- Use SSH key authentication (not passwords)
- Keep Docker and system packages updated
