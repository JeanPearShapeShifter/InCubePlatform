"""Pydantic schemas for the vibe system."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class VibeUploadResponse(BaseModel):
    id: uuid.UUID
    duration_seconds: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VibeSessionResponse(BaseModel):
    id: uuid.UUID
    duration_seconds: int
    status: str
    has_transcript: bool
    analyses_count: int
    created_at: datetime


class VibeAnalysisItem(BaseModel):
    agent_name: str
    content: dict

    model_config = {"from_attributes": True}


class VibeDetailResponse(BaseModel):
    id: uuid.UUID
    duration_seconds: int
    transcript_text: str | None
    status: str
    analyses: list[VibeAnalysisItem]
    created_at: datetime


class VibeListResponse(BaseModel):
    vibe_sessions: list[VibeSessionResponse]
