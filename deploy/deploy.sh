#!/usr/bin/env bash
set -euo pipefail

# InCube Platform — Production Deployment Script
# Run on the Linode VPS: bash deploy.sh

REPO_URL="git@github.com:JeanPearShapeShifter/InCubePlatform.git"
INSTALL_DIR="/mnt/motionmind_volume/incube"
CADDY_CONFIG="/root/n8n-docker-caddy/caddy_config/Caddyfile"
CADDY_BLOCK="incube.motionmind.antikythera.co.za"

echo "=== InCube Platform Deployment ==="

# ── 1. Clone or update repo ──────────────────────────────────────────
if [ -d "$INSTALL_DIR/repo" ]; then
    echo "→ Updating existing repo..."
    cd "$INSTALL_DIR/repo"
    git pull --ff-only
else
    echo "→ Cloning repository..."
    mkdir -p "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR/repo"
    cd "$INSTALL_DIR/repo"
fi

# ── 2. Check for .env.production ─────────────────────────────────────
if [ ! -f "$INSTALL_DIR/repo/deploy/.env.production" ]; then
    echo ""
    echo "ERROR: deploy/.env.production not found."
    echo "Copy deploy/.env.production.example to deploy/.env.production"
    echo "and fill in real values before running this script."
    exit 1
fi

# ── 3. Create data directories ──────────────────────────────────────
mkdir -p "$INSTALL_DIR/pgdata"
mkdir -p "$INSTALL_DIR/minio_data"

# ── 4. Build and start containers ───────────────────────────────────
echo "→ Building and starting containers..."
cd "$INSTALL_DIR/repo"
docker compose -f deploy/docker-compose.prod.yml --env-file deploy/.env.production up -d --build

# ── 5. Wait for postgres to be healthy ──────────────────────────────
echo "→ Waiting for PostgreSQL..."
for i in $(seq 1 30); do
    if docker exec incube-postgres pg_isready -U incube -d incube >/dev/null 2>&1; then
        echo "  PostgreSQL is ready."
        break
    fi
    sleep 2
done

# ── 6. Run Alembic migrations ──────────────────────────────────────
echo "→ Running database migrations..."
docker exec incube-backend alembic upgrade head

# ── 7. Create MinIO bucket (if needed) ─────────────────────────────
echo "→ Ensuring MinIO bucket exists..."
docker exec incube-backend python -c "
import asyncio
from miniopy_async import Minio
import os

async def ensure_bucket():
    client = Minio(
        os.environ['MINIO_ENDPOINT'],
        access_key=os.environ['MINIO_ACCESS_KEY'],
        secret_key=os.environ['MINIO_SECRET_KEY'],
        secure=False,
    )
    bucket = os.environ.get('MINIO_BUCKET', 'incube-documents')
    if not await client.bucket_exists(bucket):
        await client.make_bucket(bucket)
        print(f'  Created bucket: {bucket}')
    else:
        print(f'  Bucket already exists: {bucket}')

asyncio.run(ensure_bucket())
"

# ── 8. Update Caddy config ─────────────────────────────────────────
if grep -q "$CADDY_BLOCK" "$CADDY_CONFIG" 2>/dev/null; then
    echo "→ Caddy config already contains InCube block, skipping."
else
    echo "→ Appending InCube block to Caddyfile..."
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
    echo "  Reloading Caddy..."
    docker exec $(docker ps -q -f name=caddy) caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile 2>/dev/null \
        || echo "  WARNING: Could not auto-reload Caddy. Reload manually."
fi

# ── 9. Verify ──────────────────────────────────────────────────────
echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Containers:"
docker compose -f deploy/docker-compose.prod.yml ps
echo ""
echo "Next steps:"
echo "  1. Ensure DNS A record: incube.motionmind.antikythera.co.za → 159.223.208.109"
echo "  2. Test: curl https://incube.motionmind.antikythera.co.za/api/health"
echo "  3. Open: https://incube.motionmind.antikythera.co.za"
