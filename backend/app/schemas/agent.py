"""Pydantic schemas for the AI agent system."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=50000)
    context: dict = Field(default_factory=dict)


class AgentTokenEvent(BaseModel):
    agent: str
    content: str


class AgentDoneEvent(BaseModel):
    agent: str
    session_id: uuid.UUID
    input_tokens: int
    output_tokens: int
    cost_cents: float
    duration_ms: int


class BoomerangRequest(BaseModel):
    prompt: str = Field("", max_length=50000)


class AxiomChallengeResponse(BaseModel):
    id: uuid.UUID
    challenge_text: str
    severity: str
    targeted_agents: list[str]
    evidence_needed: str
    resolution: str | None = None
    resolution_text: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentSessionResponse(BaseModel):
    id: uuid.UUID
    agent_name: str
    model_used: str
    input_tokens: int
    output_tokens: int
    cost_cents: float
    duration_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
