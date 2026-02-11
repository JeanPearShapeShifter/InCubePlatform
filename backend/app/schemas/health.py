from pydantic import BaseModel


class ServiceCheck(BaseModel):
    status: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    checks: dict[str, ServiceCheck]
    version: str
    uptime_seconds: float
