import logging
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.models.agent_session import AgentSession
from app.models.axiom_challenge import AxiomChallenge
from app.models.bank_instance import BankInstance
from app.models.enums import BankType, DimensionType, PerspectiveStatus, PhaseType
from app.models.perspective import Perspective
from app.services.agents.base import BaseAgent

logger = logging.getLogger(__name__)


def _determine_bank_type(dimension: str, phase: str) -> str:
    """Auto-determine bank type from dimension and phase."""
    if phase != PhaseType.SUMMARIZE.value:
        return BankType.BANKABLE.value
    if dimension in (DimensionType.ARCHITECTURE.value, DimensionType.DESIGN.value):
        return BankType.FILM.value
    # Engineering Summarize
    return BankType.FILM_REEL.value


async def create_bank_instance(
    db: AsyncSession,
    perspective_id: uuid.UUID,
    synopsis: str,
    agent_assessments: dict[str, Any] | None = None,
    decision_audit: list[dict] | None = None,
) -> BankInstance:
    """Create a bank instance for a completed perspective.

    Optionally accepts agent_assessments and decision_audit from the boomerang flow.
    """
    # Get perspective and validate it's completed
    result = await db.execute(select(Perspective).where(Perspective.id == perspective_id))
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise NotFoundError("Perspective not found")
    if perspective.status != PerspectiveStatus.COMPLETED.value:
        raise ValidationError("Perspective must be completed before banking")

    bank_type = _determine_bank_type(perspective.dimension, perspective.phase)
    bank = BankInstance(
        perspective_id=perspective_id,
        type=bank_type,
        synopsis=synopsis,
        agent_assessments=agent_assessments or {},
        decision_audit=decision_audit or [],
    )
    db.add(bank)
    await db.flush()
    return bank


async def populate_bank_stats(db: AsyncSession, bank_id: uuid.UUID) -> BankInstance:
    """Populate document/vibe/email counts for a bank instance from its perspective's data."""
    result = await db.execute(select(BankInstance).where(BankInstance.id == bank_id))
    bank = result.scalar_one_or_none()
    if not bank:
        raise NotFoundError("Bank instance not found")

    # Count documents for this perspective
    from app.models.document import Document

    doc_count_result = await db.execute(
        select(func.count()).select_from(Document).where(Document.perspective_id == bank.perspective_id)
    )
    bank.documents_count = doc_count_result.scalar() or 0

    # Count vibes for this perspective
    from app.models.vibe_session import VibeSession

    vibe_count_result = await db.execute(
        select(func.count()).select_from(VibeSession).where(VibeSession.perspective_id == bank.perspective_id)
    )
    bank.vibes_count = vibe_count_result.scalar() or 0

    await db.flush()
    return bank


async def create_published_vdba(
    db: AsyncSession,
    journey_id: uuid.UUID,
    title: str,
    description: str,
) -> BankInstance:
    """Create a published VDBA bank instance for a journey.

    Requires at least one completed perspective in the journey. Uses the first
    completed perspective as the anchor.
    """
    result = await db.execute(
        select(Perspective)
        .where(Perspective.journey_id == journey_id, Perspective.status == PerspectiveStatus.COMPLETED.value)
        .order_by(Perspective.completed_at.desc())
        .limit(1)
    )
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise ValidationError("Journey must have at least one completed perspective to publish a VDBA")

    bank = BankInstance(
        perspective_id=perspective.id,
        type=BankType.PUBLISHED.value,
        synopsis=f"{title}\n\n{description}",
    )
    db.add(bank)
    await db.flush()
    return bank


async def get_bank_timeline(db: AsyncSession, journey_id: uuid.UUID) -> list[BankInstance]:
    result = await db.execute(
        select(BankInstance)
        .join(Perspective, BankInstance.perspective_id == Perspective.id)
        .where(Perspective.journey_id == journey_id)
        .order_by(BankInstance.created_at)
    )
    return list(result.scalars().all())


async def get_bank_instance(db: AsyncSession, bank_id: uuid.UUID) -> BankInstance:
    result = await db.execute(select(BankInstance).where(BankInstance.id == bank_id))
    bank = result.scalar_one_or_none()
    if not bank:
        raise NotFoundError("Bank instance not found")
    return bank


_SYNOPSIS_SYSTEM = (
    "You are a concise business analyst. Given the outputs of specialist AI agents "
    "and any challenges raised by the Axiom reviewer, write a clear, actionable synopsis "
    "of the analysis (3-5 paragraphs). Focus on key findings, risks identified, and "
    "recommended actions. Do NOT use bullet points for the main body — use flowing prose. "
    "Keep it under 800 words."
)


async def generate_synopsis(
    db: AsyncSession,
    perspective_id: uuid.UUID,
) -> tuple[str, int, int]:
    """Generate an AI synopsis from agent outputs and axiom challenges.

    Returns (synopsis_text, input_tokens, output_tokens).
    """
    # Fetch latest agent session per agent
    subq = (
        select(
            AgentSession.agent_name,
            func.max(AgentSession.created_at).label("latest"),
        )
        .where(AgentSession.perspective_id == perspective_id)
        .group_by(AgentSession.agent_name)
        .subquery()
    )
    result = await db.execute(
        select(AgentSession)
        .join(
            subq,
            (AgentSession.agent_name == subq.c.agent_name)
            & (AgentSession.created_at == subq.c.latest),
        )
        .where(AgentSession.perspective_id == perspective_id)
    )
    sessions = list(result.scalars().all())

    if not sessions:
        raise ValidationError("No agent sessions found for this perspective")

    # Build specialist outputs section
    parts: list[str] = []
    for session in sessions:
        content = (session.response_payload or {}).get("content", "")
        if content:
            truncated = content[:1500]
            parts.append(f"### {session.agent_name.capitalize()}\n{truncated}")

    # Fetch axiom challenges
    challenge_result = await db.execute(
        select(AxiomChallenge)
        .where(AxiomChallenge.perspective_id == perspective_id)
        .order_by(AxiomChallenge.created_at)
    )
    challenges = list(challenge_result.scalars().all())

    challenge_parts: list[str] = []
    for ch in challenges:
        entry = f"- **Challenge** ({ch.severity}): {ch.challenge_text}"
        if ch.resolution_text:
            entry += f"\n  **Verdict** ({ch.resolution}): {ch.resolution_text}"
        challenge_parts.append(entry)

    prompt_sections = ["## Specialist Agent Outputs\n"] + parts
    if challenge_parts:
        prompt_sections.append("\n## Axiom Review\n" + "\n".join(challenge_parts))
    prompt_sections.append(
        "\n---\nWrite a synopsis summarizing the above analysis."
    )

    prompt = "\n\n".join(prompt_sections)

    agent = BaseAgent("axiom")
    synopsis, input_tokens, output_tokens = await agent.raw_chat(
        prompt, _SYNOPSIS_SYSTEM, max_tokens=1024,
    )
    logger.info(
        "generate_synopsis perspective=%s tokens_in=%d tokens_out=%d",
        perspective_id, input_tokens, output_tokens,
    )
    return synopsis, input_tokens, output_tokens
