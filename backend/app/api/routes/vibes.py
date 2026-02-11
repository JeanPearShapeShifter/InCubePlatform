"""API routes for the vibe (voice recording) system."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.errors import NotFoundError, ValidationError
from app.models.perspective import Perspective
from app.models.user import User
from app.models.vibe_analysis import VibeAnalysis
from app.models.vibe_session import VibeSession
from app.schemas.common import ResponseEnvelope
from app.schemas.vibe import (
    VibeAnalysisItem,
    VibeDetailResponse,
    VibeListResponse,
    VibeSessionResponse,
    VibeUploadResponse,
)
from app.services.vibe import (
    create_vibe_session,
    get_vibe_session_detail,
    list_vibe_sessions,
    run_post_vibe_analysis,
    transcribe_vibe,
)

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"audio/webm", "audio/wav", "audio/mpeg", "audio/mp3", "audio/ogg", "audio/x-wav"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


async def _get_perspective(perspective_id: uuid.UUID, db: AsyncSession) -> Perspective:
    """Fetch a perspective or raise 404."""
    result = await db.execute(select(Perspective).where(Perspective.id == perspective_id))
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise NotFoundError(f"Perspective {perspective_id} not found")
    return perspective


@router.post(
    "/perspectives/{perspective_id}/vibes",
    response_model=ResponseEnvelope[VibeUploadResponse],
    status_code=201,
)
async def upload_vibe(
    perspective_id: uuid.UUID,
    audio: UploadFile,
    duration_seconds: int = Form(..., gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a voice recording for a perspective.

    Accepts webm/wav/mp3 audio up to 100 MB. Runs transcription synchronously
    and then triggers post-vibe analysis on the transcript.
    """
    await _get_perspective(perspective_id, db)

    # Validate content type
    if audio.content_type and audio.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(f"Unsupported audio format: {audio.content_type}. Accepted: webm, wav, mp3, ogg")

    # Read file data
    audio_data = await audio.read()
    if len(audio_data) > MAX_FILE_SIZE:
        raise ValidationError(f"File too large: {len(audio_data)} bytes. Maximum: {MAX_FILE_SIZE} bytes (100 MB)")
    if len(audio_data) == 0:
        raise ValidationError("Empty audio file")

    # Create vibe session (uploads to MinIO)
    vibe = await create_vibe_session(db, perspective_id, current_user.id, audio_data, duration_seconds)

    # Run transcription synchronously — will be moved to background jobs later
    try:
        await transcribe_vibe(db, vibe.id)
    except Exception:
        logger.exception("Transcription failed for vibe session %s", vibe.id)
        vibe.status = "failed"
        await db.flush()

    return ResponseEnvelope(data=VibeUploadResponse.model_validate(vibe))


@router.get(
    "/perspectives/{perspective_id}/vibes",
    response_model=ResponseEnvelope[VibeListResponse],
)
async def list_vibes(
    perspective_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List vibe sessions for a perspective."""
    await _get_perspective(perspective_id, db)

    sessions = await list_vibe_sessions(db, perspective_id)

    # Build response with analysis counts
    items = []
    for s in sessions:
        count_result = await db.execute(
            select(func.count()).select_from(VibeAnalysis).where(VibeAnalysis.vibe_session_id == s.id)
        )
        count = count_result.scalar() or 0
        items.append(
            VibeSessionResponse(
                id=s.id,
                duration_seconds=s.duration_seconds,
                status=s.status,
                has_transcript=s.transcript_text is not None,
                analyses_count=count,
                created_at=s.created_at,
            )
        )

    return ResponseEnvelope(data=VibeListResponse(vibe_sessions=items))


@router.get(
    "/vibes/{vibe_id}",
    response_model=ResponseEnvelope[VibeDetailResponse],
)
async def get_vibe_detail(
    vibe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a vibe session with all agent analyses."""
    detail = await get_vibe_session_detail(db, vibe_id)
    vibe = detail["vibe_session"]
    analyses = detail["analyses"]

    return ResponseEnvelope(
        data=VibeDetailResponse(
            id=vibe.id,
            duration_seconds=vibe.duration_seconds,
            transcript_text=vibe.transcript_text,
            status=vibe.status,
            analyses=[VibeAnalysisItem.model_validate(a) for a in analyses],
            created_at=vibe.created_at,
        )
    )


@router.post(
    "/vibes/{vibe_id}/analyze",
    response_model=ResponseEnvelope[VibeUploadResponse],
)
async def re_analyze_vibe(
    vibe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Re-trigger post-vibe analysis on an existing vibe session."""
    result = await db.execute(select(VibeSession).where(VibeSession.id == vibe_id))
    vibe = result.scalar_one_or_none()
    if not vibe:
        raise NotFoundError(f"Vibe session {vibe_id} not found")

    if not vibe.transcript_text:
        raise ValidationError("Cannot analyze — vibe session has no transcript")

    vibe.status = "analyzing"
    await db.flush()

    try:
        await run_post_vibe_analysis(db, vibe.id)
    except Exception:
        logger.exception("Re-analysis failed for vibe session %s", vibe.id)
        vibe.status = "failed"
        await db.flush()

    return ResponseEnvelope(data=VibeUploadResponse.model_validate(vibe))
