import time

import redis.asyncio as aioredis
from fastapi import APIRouter, Response
from miniopy_async import Minio
from sqlalchemy import text

from app.core.config import settings
from app.db.session import async_session_factory
from app.schemas.health import HealthResponse, ServiceCheck

router = APIRouter()

_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response) -> HealthResponse:
    checks: dict[str, ServiceCheck] = {}
    all_healthy = True

    # Database check
    try:
        start = time.monotonic()
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        latency = (time.monotonic() - start) * 1000
        checks["database"] = ServiceCheck(status="up", latency_ms=round(latency, 1))
    except Exception:
        checks["database"] = ServiceCheck(status="down", latency_ms=0)
        all_healthy = False

    # Redis check
    try:
        start = time.monotonic()
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        latency = (time.monotonic() - start) * 1000
        checks["redis"] = ServiceCheck(status="up", latency_ms=round(latency, 1))
    except Exception:
        checks["redis"] = ServiceCheck(status="down", latency_ms=0)
        all_healthy = False

    # MinIO check
    try:
        start = time.monotonic()
        client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,
        )
        await client.list_buckets()
        latency = (time.monotonic() - start) * 1000
        checks["minio"] = ServiceCheck(status="up", latency_ms=round(latency, 1))
    except Exception:
        checks["minio"] = ServiceCheck(status="down", latency_ms=0)
        all_healthy = False

    status = "healthy" if all_healthy else "degraded"
    if not all_healthy:
        response.status_code = 503

    return HealthResponse(
        status=status,
        checks=checks,
        version="1.0.0",
        uptime_seconds=round(time.time() - _start_time, 1),
    )
