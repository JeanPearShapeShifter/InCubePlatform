from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://incube:incube_dev@localhost:5435/incube_dev"

    # Redis
    redis_url: str = "redis://localhost:6380"

    # Environment
    environment: str = "development"

    # Auth
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 7

    # AI
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_agent_model: str = "claude-haiku-4-5-20251001"

    # Email
    resend_api_key: str = ""
    resend_from_email: str = "noreply@incube.ai"

    # MinIO
    minio_endpoint: str = "localhost:9002"
    minio_access_key: str = "incube"
    minio_secret_key: str = "incube_dev"
    minio_bucket: str = "incube-documents"

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: str = "http://localhost:3001,https://incube.motionmind.antikythera.co.za"


settings = Settings()
