import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data["checks"]
    assert "redis" in data["checks"]
    assert "minio" in data["checks"]
    assert data["version"] == "1.0.0"
    assert "uptime_seconds" in data


@pytest.mark.asyncio
async def test_health_response_schema(client):
    response = await client.get("/api/health")
    data = response.json()
    for service in ["database", "redis", "minio"]:
        check = data["checks"][service]
        assert "status" in check
        assert "latency_ms" in check


@pytest.mark.asyncio
async def test_config_loads():
    from app.core.config import Settings

    settings = Settings()
    assert settings.database_url
    assert settings.redis_url
