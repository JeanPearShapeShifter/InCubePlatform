"""Enhanced boomerang service: collects agent outputs + Axiom results into structured audit trails."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_session import AgentSession
from app.models.axiom_challenge import AxiomChallenge
from app.services.agents.prompts import VALID_AGENT_NAMES

logger = logging.getLogger(__name__)

SPECIALIST_NAMES = [n for n in VALID_AGENT_NAMES if n != "axiom"]


@dataclass
class AgentAssessment:
    """Structured assessment from a single agent."""

    summary: str
    confidence: float
    key_findings: list[str] = field(default_factory=list)


@dataclass
class DecisionAuditEntry:
    """Single decision audit entry from the Axiom challenge flow."""

    challenge: str
    resolution: str
    evidence: str
    agents: list[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class BoomerangResult:
    """Full result of an enhanced boomerang run."""

    agent_assessments: dict[str, dict]
    decision_audit: list[dict]
    agents_completed: list[str]


async def run_boomerang_with_audit(
    db: AsyncSession,
    perspective_id: uuid.UUID,
) -> BoomerangResult:
    """Collect the latest agent outputs and Axiom challenges into structured audit data.

    This reads from persisted agent sessions and axiom challenges to build
    agent_assessments and decision_audit suitable for banking.
    """
    agent_assessments: dict[str, dict] = {}
    agents_completed: list[str] = []

    # Collect latest specialist outputs from agent_sessions
    for name in SPECIALIST_NAMES:
        result = await db.execute(
            select(AgentSession)
            .where(AgentSession.perspective_id == perspective_id, AgentSession.agent_name == name)
            .order_by(AgentSession.created_at.desc())
            .limit(1)
        )
        session = result.scalar_one_or_none()
        if session and session.response_payload:
            content = session.response_payload.get("content", "")
            if content:
                agents_completed.append(name)
                assessment = _build_assessment(name, content)
                agent_assessments[name] = {
                    "summary": assessment.summary,
                    "confidence": assessment.confidence,
                    "key_findings": assessment.key_findings,
                }

    # Build decision audit from Axiom challenges
    decision_audit = await _build_decision_audit(db, perspective_id)

    return BoomerangResult(
        agent_assessments=agent_assessments,
        decision_audit=decision_audit,
        agents_completed=agents_completed,
    )


async def get_boomerang_summary(
    db: AsyncSession,
    perspective_id: uuid.UUID,
) -> dict[str, dict]:
    """Get the latest agent assessments for a perspective."""
    result = await run_boomerang_with_audit(db, perspective_id)
    return result.agent_assessments


def _build_assessment(agent_name: str, content: str) -> AgentAssessment:
    """Build a structured assessment from raw agent output.

    Extracts a summary (first 300 chars), derives confidence from content length,
    and pulls key findings from the content.
    """
    # Summary: first meaningful paragraph, truncated
    lines = [line.strip() for line in content.strip().split("\n") if line.strip()]
    summary = lines[0][:300] if lines else "No output"

    # Confidence heuristic: longer, more structured responses indicate higher confidence
    confidence = min(1.0, max(0.3, len(content) / 2000))

    # Key findings: extract lines that start with bullet points or numbered items
    key_findings: list[str] = []
    for line in lines:
        cleaned = line.lstrip("- *0123456789.)")
        if cleaned and line != cleaned and len(cleaned) > 10:
            key_findings.append(cleaned.strip()[:200])
        if len(key_findings) >= 5:
            break

    # If no bullet points found, use first few sentences as findings
    if not key_findings and len(lines) > 1:
        for line in lines[1:4]:
            if len(line) > 10:
                key_findings.append(line[:200])

    return AgentAssessment(
        summary=summary,
        confidence=round(confidence, 2),
        key_findings=key_findings,
    )


async def _build_decision_audit(
    db: AsyncSession,
    perspective_id: uuid.UUID,
) -> list[dict]:
    """Build decision audit entries from persisted Axiom challenges."""
    result = await db.execute(
        select(AxiomChallenge)
        .where(AxiomChallenge.perspective_id == perspective_id)
        .order_by(AxiomChallenge.created_at.asc())
    )
    challenges = result.scalars().all()

    audit_entries: list[dict] = []
    for ch in challenges:
        entry = DecisionAuditEntry(
            challenge=ch.challenge_text,
            resolution=ch.resolution or "action_required",
            evidence=ch.resolution_text or ch.evidence_needed or "",
            agents=list(ch.targeted_agents) if ch.targeted_agents else [],
            timestamp=ch.resolved_at.isoformat() if ch.resolved_at else ch.created_at.isoformat(),
        )
        audit_entries.append({
            "challenge": entry.challenge,
            "resolution": entry.resolution,
            "evidence": entry.evidence,
            "agents": entry.agents,
            "timestamp": entry.timestamp,
        })

    return audit_entries
