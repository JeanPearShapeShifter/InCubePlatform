"""Whisper transcription service using OpenAI API."""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
COST_PER_MINUTE = 0.006  # $0.006/minute


async def transcribe_audio(audio_data: bytes, filename: str = "audio.webm", language: str = "en") -> dict:
    """Call OpenAI Whisper API to transcribe audio.

    Returns {"text": "...", "duration_seconds": N, "cost_cents": X.XX}
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            WHISPER_API_URL,
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            files={"file": (filename, audio_data, "audio/webm")},
            data={"model": "whisper-1", "language": language, "response_format": "verbose_json"},
        )
        response.raise_for_status()
        data = response.json()
        duration = data.get("duration", 0)
        cost_cents = (duration / 60) * COST_PER_MINUTE * 100
        return {
            "text": data.get("text", ""),
            "duration_seconds": int(duration),
            "cost_cents": round(cost_cents, 4),
        }
