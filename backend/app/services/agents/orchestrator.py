"""Boomerang orchestrator: run 8 specialists in parallel, then Axiom challenge flow."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_settings
from app.core.sse import sse_event
from app.services.agents.axiom import AxiomChallenger
from app.services.agents.base import (
    AGENT_REGISTRY,
    AgentContext,
    BaseAgent,
    record_api_usage,
)
from app.services.agents.prompts import VALID_AGENT_NAMES, build_system_prompt

logger = logging.getLogger(__name__)

SPECIALIST_AGENTS = [name for name in VALID_AGENT_NAMES if name != "axiom"]


class BoomerangOrchestrator:
    """Orchestrates the full boomerang flow: specialists -> Axiom -> resolution."""

    def __init__(self):
        self._challenger = AxiomChallenger()

    async def run(
        self,
        context: AgentContext,
        prompt: str,
        db: AsyncSession,
    ) -> AsyncGenerator[str, None]:
        """Run all 9 agents through the boomerang flow, yielding SSE events."""
        yield sse_event("boomerang_start", {"perspective_id": str(context.perspective_id)})

        # Phase 1: Run 8 specialist agents in parallel
        specialist_outputs: dict[str, str] = {}

        async def run_specialist(agent: BaseAgent) -> tuple[str, str, int, int]:
            system = build_system_prompt(agent.name, context.dimension, context.phase)
            content, in_tok, out_tok = await agent.raw_chat(prompt, system)
            return agent.name, content, in_tok, out_tok

        # Notify start of each agent
        for name in SPECIALIST_AGENTS:
            yield sse_event("agent_start", {"agent": name})

        tasks = [run_specialist(AGENT_REGISTRY[name]) for name in SPECIALIST_AGENTS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error("Specialist agent failed: %s", result)
                continue
            name, content, in_tok, out_tok = result
            specialist_outputs[name] = content

            # Record API usage for this specialist call
            await record_api_usage(
                db, context, name, app_settings.default_agent_model,
                in_tok, out_tok, endpoint=f"boomerang/specialist/{name}",
            )

            yield sse_event("agent_complete", {
                "agent": name,
                "content": content,
            })

        if not specialist_outputs:
            yield sse_event("error", {"error": "All specialist agents failed"})
            return

        # Phase 2: Axiom challenge flow
        yield sse_event("axiom_start", {"agent": "axiom"})

        async for event in self._challenger.stream_challenge(specialist_outputs, context, db):
            yield event

        yield sse_event("boomerang_complete", {
            "perspective_id": str(context.perspective_id),
            "agents_completed": list(specialist_outputs.keys()),
        })
