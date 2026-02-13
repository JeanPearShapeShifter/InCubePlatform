import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentAssessment(BaseModel):
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    key_findings: list[str] = Field(default_factory=list)


class DecisionAuditEntry(BaseModel):
    challenge: str
    resolution: str
    evidence: str = ""
    agents: list[str] = Field(default_factory=list)
    timestamp: str = ""


class BankCreate(BaseModel):
    synopsis: str = Field(min_length=1, max_length=5000)
    agent_assessments: dict[str, AgentAssessment] | None = None
    decision_audit: list[DecisionAuditEntry] | None = None


class BankInstanceResponse(BaseModel):
    id: uuid.UUID
    perspective_id: uuid.UUID
    type: str
    synopsis: str
    decision_audit: list[Any]
    agent_assessments: dict[str, Any]
    documents_count: int
    vibes_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BankInstanceDetail(BaseModel):
    """Detailed bank instance with typed agent_assessments and decision_audit."""

    id: uuid.UUID
    perspective_id: uuid.UUID
    type: str
    synopsis: str
    decision_audit: list[DecisionAuditEntry]
    agent_assessments: dict[str, AgentAssessment]
    documents_count: int
    vibes_count: int
    emails_sent: int
    feedback_received: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BankTimelineResponse(BaseModel):
    bank_instances: list[BankInstanceResponse]


class SynopsisResponse(BaseModel):
    synopsis: str
    input_tokens: int
    output_tokens: int
