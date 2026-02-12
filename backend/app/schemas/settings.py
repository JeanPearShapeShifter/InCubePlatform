from datetime import date

from pydantic import BaseModel, Field

ALLOWED_SETTINGS = {
    "default_model": str,
    "anthropic_api_key": str,
    "voice_provider": str,
    "voice_language": str,
    "theme": str,
    "export_format": str,
    "monthly_budget_cents": int,
    "budget_alert_thresholds": list,
}

VALID_MODELS = ["claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929"]
VALID_THEMES = ["space", "forest", "blackhole"]
VALID_EXPORT_FORMATS = ["pdf", "docx", "json"]
VALID_VOICE_PROVIDERS = ["whisper", "deepgram", "assemblyai"]


class SettingUpdate(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str | int | list = Field()


class SettingsResponse(BaseModel):
    default_model: str = "claude-haiku-4-5-20251001"
    anthropic_api_key: str = ""
    voice_provider: str = "whisper"
    voice_language: str = "en"
    theme: str = "space"
    export_format: str = "pdf"
    monthly_budget_cents: int = 0
    budget_alert_thresholds: list[int] = [50, 80, 100]


class DailyUsage(BaseModel):
    date: date
    cost_cents: float
    tokens_in: int
    tokens_out: int


class UsageSummaryResponse(BaseModel):
    total_cost_cents: float
    total_tokens_in: int
    total_tokens_out: int
    total_calls: int
    by_date: list[DailyUsage]


class UsageEntry(BaseModel):
    name: str
    cost_cents: float
    tokens_in: int
    tokens_out: int
    call_count: int


class UsageBreakdownResponse(BaseModel):
    breakdown: list[UsageEntry]
