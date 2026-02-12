"""API routes for the AI agent system."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.errors import NotFoundError, ValidationError
from app.core.sse import sse_event, sse_response
from app.models.agent_session import AgentSession
from app.models.axiom_challenge import AxiomChallenge
from app.models.goal import Goal
from app.models.journey import Journey
from app.models.perspective import Perspective
from app.models.user import User
from app.schemas.agent import (
    AgentSessionResponse,
    AxiomChallengeResponse,
    BoomerangRequest,
    ChatRequest,
)
from app.schemas.common import PaginationMeta, ResponseEnvelope
from app.services.agents.base import AGENT_REGISTRY, AgentContext
from app.services.agents.orchestrator import BoomerangOrchestrator
from app.services.agents.prompts import VALID_AGENT_NAMES

router = APIRouter()


async def _get_perspective(perspective_id: uuid.UUID, db: AsyncSession) -> Perspective:
    """Fetch a perspective or raise 404."""
    result = await db.execute(select(Perspective).where(Perspective.id == perspective_id))
    perspective = result.scalar_one_or_none()
    if not perspective:
        raise NotFoundError(f"Perspective {perspective_id} not found")
    return perspective


@router.post("/perspectives/{perspective_id}/agents/{agent_name}/chat")
async def agent_chat(
    perspective_id: uuid.UUID,
    agent_name: str,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stream a chat response from a single agent via SSE."""
    if agent_name not in VALID_AGENT_NAMES:
        raise ValidationError(f"Invalid agent name: {agent_name}. Must be one of: {', '.join(VALID_AGENT_NAMES)}")

    perspective = await _get_perspective(perspective_id, db)
    agent = AGENT_REGISTRY[agent_name]

    context = AgentContext(
        perspective_id=perspective.id,
        dimension=perspective.dimension,
        phase=perspective.phase,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
    )

    async def stream() -> AsyncGenerator[str, None]:
        async for event in agent.chat(body.message, context, db):
            yield event

    return sse_response(stream())


@router.post("/perspectives/{perspective_id}/boomerang")
async def run_boomerang(
    perspective_id: uuid.UUID,
    body: BoomerangRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run the full boomerang flow (8 specialists + Axiom) via SSE."""
    perspective = await _get_perspective(perspective_id, db)

    # Load goal via perspective -> journey -> goal
    journey_result = await db.execute(select(Journey).where(Journey.id == perspective.journey_id))
    journey = journey_result.scalar_one_or_none()
    goal_statement = ""
    if journey:
        goal_result = await db.execute(select(Goal).where(Goal.id == journey.goal_id))
        goal = goal_result.scalar_one_or_none()
        if goal:
            goal_statement = goal.title
            if goal.description:
                goal_statement += f"\n\n{goal.description}"

    context = AgentContext(
        perspective_id=perspective.id,
        dimension=perspective.dimension,
        phase=perspective.phase,
        goal_statement=goal_statement,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
    )

    # Build user message from goal context — never send empty
    user_prompt = body.prompt.strip() if body.prompt else ""
    if user_prompt:
        message = (
            f"## Goal\n{goal_statement}\n\n## Additional Context\n{user_prompt}"
            if goal_statement
            else user_prompt
        )
    elif goal_statement:
        dim, phase = perspective.dimension, perspective.phase
        message = (
            f"## Goal\n{goal_statement}\n\n"
            f"Analyze this goal from your specialist perspective "
            f"within the {dim} / {phase} intersection."
        )
    else:
        dim, phase = perspective.dimension, perspective.phase
        message = (
            f"Analyze the current business transformation context "
            f"from your specialist perspective "
            f"within the {dim} / {phase} intersection."
        )

    orchestrator = BoomerangOrchestrator()

    async def stream() -> AsyncGenerator[str, None]:
        async for event in orchestrator.run(context, message, db):
            yield event

    return sse_response(stream())


@router.get(
    "/perspectives/{perspective_id}/agent-sessions",
    response_model=ResponseEnvelope[list[AgentSessionResponse]],
)
async def list_agent_sessions(
    perspective_id: uuid.UUID,
    agent: str | None = Query(None, description="Filter by agent name"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List agent sessions for a perspective."""
    await _get_perspective(perspective_id, db)

    base_query = select(AgentSession).where(AgentSession.perspective_id == perspective_id)
    count_query = select(func.count()).select_from(AgentSession).where(
        AgentSession.perspective_id == perspective_id,
    )

    if agent:
        if agent not in VALID_AGENT_NAMES:
            raise ValidationError(f"Invalid agent name: {agent}")
        base_query = base_query.where(AgentSession.agent_name == agent)
        count_query = count_query.where(AgentSession.agent_name == agent)

    # Total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginated results
    offset = (page - 1) * per_page
    query = base_query.order_by(AgentSession.created_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    sessions = result.scalars().all()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    return ResponseEnvelope(
        data=[AgentSessionResponse.model_validate(s) for s in sessions],
        meta=PaginationMeta(page=page, per_page=per_page, total=total, total_pages=total_pages).model_dump(),
    )


@router.post("/perspectives/{perspective_id}/axiom/challenge")
async def trigger_axiom_challenge(
    perspective_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger an Axiom challenge against the latest specialist outputs for this perspective.

    Fetches the most recent session output from each specialist agent and feeds them to Axiom.
    """
    perspective = await _get_perspective(perspective_id, db)

    context = AgentContext(
        perspective_id=perspective.id,
        dimension=perspective.dimension,
        phase=perspective.phase,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
    )

    # Gather latest specialist outputs from stored sessions
    specialist_outputs: dict[str, str] = {}
    specialist_names = [n for n in VALID_AGENT_NAMES if n != "axiom"]

    for name in specialist_names:
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
                specialist_outputs[name] = content

    if not specialist_outputs:
        raise ValidationError("No specialist outputs found for this perspective. Run agents first.")

    from app.services.agents.axiom import AxiomChallenger

    challenger = AxiomChallenger()

    async def stream() -> AsyncGenerator[str, None]:
        async for event in challenger.stream_challenge(specialist_outputs, context, db):
            yield event
        yield sse_event("challenge_complete", {"perspective_id": str(perspective_id)})

    return sse_response(stream())


@router.get(
    "/perspectives/{perspective_id}/axiom/challenges",
    response_model=ResponseEnvelope[list[AxiomChallengeResponse]],
)
async def list_axiom_challenges(
    perspective_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List Axiom challenges for a perspective."""
    await _get_perspective(perspective_id, db)

    count_query = select(func.count()).select_from(AxiomChallenge).where(
        AxiomChallenge.perspective_id == perspective_id,
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * per_page
    query = (
        select(AxiomChallenge)
        .where(AxiomChallenge.perspective_id == perspective_id)
        .order_by(AxiomChallenge.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(query)
    challenges = result.scalars().all()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 0

    return ResponseEnvelope(
        data=[AxiomChallengeResponse.model_validate(c) for c in challenges],
        meta=PaginationMeta(page=page, per_page=per_page, total=total, total_pages=total_pages).model_dump(),
    )
