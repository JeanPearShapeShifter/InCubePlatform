"""Vibe session orchestration — upload, transcription, and post-vibe analysis."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import NotFoundError
from app.models.agent_session import AgentSession
from app.models.perspective import Perspective
from app.models.vibe_analysis import VibeAnalysis
from app.models.vibe_session import VibeSession
from app.services.agents.base import COST_PER_INPUT_TOKEN, COST_PER_OUTPUT_TOKEN
from app.services.agents.prompts import VALID_AGENT_NAMES
from app.services.vibe_minio import download_audio, ensure_bucket, get_minio_client, upload_audio
from app.services.vibe_prompts import VIBE_ANALYSIS_SYSTEM, build_vibe_analysis_prompt
from app.services.whisper import transcribe_audio

logger = logging.getLogger(__name__)


async def create_vibe_session(
    db: AsyncSession,
    perspective_id: uuid.UUID,
    user_id: uuid.UUID,
    audio_data: bytes,
    duration_seconds: int,
) -> VibeSession:
    """Upload audio to MinIO and create a VibeSession record."""
    client = get_minio_client()
    await ensure_bucket(client)
    minio_key = await upload_audio(client, audio_data, str(perspective_id))

    session = VibeSession(
        perspective_id=perspective_id,
        conducted_by=user_id,
        duration_seconds=duration_seconds,
        audio_minio_key=minio_key,
        status="transcribing",
    )
    db.add(session)
    await db.flush()
    return session


async def transcribe_vibe(db: AsyncSession, vibe_session_id: uuid.UUID) -> None:
    """Run Whisper transcription on a vibe session's audio."""
    result = await db.execute(select(VibeSession).where(VibeSession.id == vibe_session_id))
    vibe = result.scalar_one_or_none()
    if not vibe:
        raise NotFoundError(f"Vibe session {vibe_session_id} not found")

    # Download audio from MinIO
    client = get_minio_client()
    audio_data = await download_audio(client, vibe.audio_minio_key)

    # Transcribe
    transcription = await transcribe_audio(audio_data)

    # Update vibe session
    vibe.transcript_text = transcription["text"]
    vibe.transcription_cost_cents = transcription["cost_cents"]
    vibe.status = "analyzing"
    await db.flush()

    # Run post-vibe analysis
    await run_post_vibe_analysis(db, vibe_session_id)


async def _run_single_agent_analysis(
    agent_name: str,
    transcript: str,
    perspective: Perspective,
    vibe_session_id: uuid.UUID,
    db: AsyncSession,
) -> VibeAnalysis | None:
    """Run a single agent's post-vibe analysis and save results."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    model = settings.default_agent_model

    user_prompt = build_vibe_analysis_prompt(
        agent_name, transcript, dimension=perspective.dimension, phase=perspective.phase
    )

    start = time.monotonic()
    try:
        response = await client.messages.create(
            model=model,
            max_tokens=4096,
            system=VIBE_ANALYSIS_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except anthropic.APIError:
        logger.exception("Anthropic API error for vibe analysis agent %s", agent_name)
        return None

    duration_ms = int((time.monotonic() - start) * 1000)
    content_text = response.content[0].text
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost_cents = (input_tokens * COST_PER_INPUT_TOKEN + output_tokens * COST_PER_OUTPUT_TOKEN) * 100

    # Parse JSON content — handle markdown-wrapped JSON
    try:
        cleaned = content_text.strip()
        if cleaned.startswith("```"):
            # Strip markdown code fence
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        content_json = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Agent %s returned non-JSON vibe analysis, wrapping raw text", agent_name)
        content_json = {
            "insights": [{"text": content_text, "source": "raw_response"}],
            "actionItems": [],
            "contradictions": [],
            "suggestedEdits": [],
        }

    # Save agent session for tracking
    agent_session = AgentSession(
        perspective_id=perspective.id,
        agent_name=agent_name,
        model_used=model,
        system_prompt_version="v1",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_cents=round(cost_cents, 4),
        request_payload={"type": "post_vibe", "vibe_session_id": str(vibe_session_id)},
        response_payload={"content": content_text},
        duration_ms=duration_ms,
    )
    db.add(agent_session)
    await db.flush()

    # Save vibe analysis record
    analysis = VibeAnalysis(
        vibe_session_id=vibe_session_id,
        agent_name=agent_name,
        analysis_type="post_vibe",
        content=content_json,
        agent_session_id=agent_session.id,
    )
    db.add(analysis)
    await db.flush()
    return analysis


async def run_post_vibe_analysis(db: AsyncSession, vibe_session_id: uuid.UUID) -> None:
    """Run all 9 agents on the transcript in parallel."""
    result = await db.execute(select(VibeSession).where(VibeSession.id == vibe_session_id))
    vibe = result.scalar_one_or_none()
    if not vibe:
        raise NotFoundError(f"Vibe session {vibe_session_id} not found")

    if not vibe.transcript_text:
        raise ValueError("Vibe session has no transcript — transcribe first")

    # Get perspective for context
    p_result = await db.execute(select(Perspective).where(Perspective.id == vibe.perspective_id))
    perspective = p_result.scalar_one_or_none()
    if not perspective:
        raise NotFoundError(f"Perspective {vibe.perspective_id} not found")

    # Delete existing analyses for this session (in case of re-analysis)
    existing = await db.execute(
        select(VibeAnalysis).where(VibeAnalysis.vibe_session_id == vibe_session_id)
    )
    for old_analysis in existing.scalars().all():
        await db.delete(old_analysis)
    await db.flush()

    # Run all agents in parallel
    # Note: we use asyncio.gather but each coroutine shares the same db session,
    # which is acceptable for SQLAlchemy async sessions with careful flushing.
    tasks = [
        _run_single_agent_analysis(name, vibe.transcript_text, perspective, vibe_session_id, db)
        for name in VALID_AGENT_NAMES
    ]
    await asyncio.gather(*tasks)

    # Mark complete
    vibe.status = "complete"
    await db.flush()


async def list_vibe_sessions(db: AsyncSession, perspective_id: uuid.UUID) -> list[VibeSession]:
    """List vibe sessions for a perspective, newest first."""
    result = await db.execute(
        select(VibeSession)
        .where(VibeSession.perspective_id == perspective_id)
        .order_by(VibeSession.created_at.desc())
    )
    return list(result.scalars().all())


async def get_vibe_session_detail(db: AsyncSession, vibe_id: uuid.UUID) -> dict:
    """Get a vibe session with its analyses."""
    result = await db.execute(select(VibeSession).where(VibeSession.id == vibe_id))
    vibe = result.scalar_one_or_none()
    if not vibe:
        raise NotFoundError(f"Vibe session {vibe_id} not found")

    analyses_result = await db.execute(
        select(VibeAnalysis)
        .where(VibeAnalysis.vibe_session_id == vibe_id)
        .order_by(VibeAnalysis.agent_name)
    )
    analyses = analyses_result.scalars().all()

    return {
        "vibe_session": vibe,
        "analyses": analyses,
    }
