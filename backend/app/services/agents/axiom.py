"""Axiom adversarial review and bounded debate logic."""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.sse import sse_event
from app.models.agent_session import AgentSession
from app.models.axiom_challenge import AxiomChallenge
from app.services.agents.base import (
    COST_PER_INPUT_TOKEN,
    COST_PER_OUTPUT_TOKEN,
    AgentContext,
    BaseAgent,
    record_api_usage,
)
from app.services.agents.prompts import (
    build_axiom_challenge_prompt,
    build_axiom_verdict_prompt,
    build_system_prompt,
)

logger = logging.getLogger(__name__)


@dataclass
class Challenge:
    challenge_text: str
    severity: str
    targeted_agents: list[str]
    evidence_needed: str


@dataclass
class Verdict:
    resolution: str
    resolution_text: str


class AxiomChallenger:
    """Manages the Axiom bounded debate flow: challenge -> response -> verdict."""

    def __init__(self):
        self._axiom = BaseAgent("axiom")

    async def challenge(
        self,
        specialist_outputs: dict[str, str],
        context: AgentContext,
        db: AsyncSession,
    ) -> tuple[list[Challenge], str]:
        """Axiom reviews all specialist outputs and produces challenges.

        Returns (challenges, raw_response) tuple.
        """
        prompt = build_axiom_challenge_prompt(specialist_outputs)
        system = build_system_prompt("axiom", context.dimension, context.phase)

        start = time.monotonic()
        content, input_tokens, output_tokens = await self._axiom.raw_chat(prompt, system)
        duration_ms = int((time.monotonic() - start) * 1000)

        cost_cents = (
            input_tokens * COST_PER_INPUT_TOKEN + output_tokens * COST_PER_OUTPUT_TOKEN
        ) * 100

        # Save Axiom session
        session = AgentSession(
            perspective_id=context.perspective_id,
            agent_name="axiom",
            model_used=settings.default_agent_model,
            system_prompt_version="v1",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_cents=round(cost_cents, 4),
            request_payload={"type": "challenge", "prompt": prompt},
            response_payload={"content": content},
            duration_ms=duration_ms,
        )
        db.add(session)
        await db.flush()

        # Record API usage
        await record_api_usage(
            db, context, "axiom", settings.default_agent_model,
            input_tokens, output_tokens, endpoint="boomerang/axiom/challenge",
        )

        # Parse challenges from JSON response
        challenges = _parse_challenges(content)

        # Persist challenges in DB
        for ch in challenges:
            record = AxiomChallenge(
                perspective_id=context.perspective_id,
                challenge_text=ch.challenge_text,
                severity=ch.severity,
                targeted_agents=ch.targeted_agents,
                evidence_needed=ch.evidence_needed,
                agent_session_id=session.id,
            )
            db.add(record)
        await db.flush()

        return challenges, content

    async def get_agent_response(
        self,
        agent: BaseAgent,
        challenge_text: str,
        context: AgentContext,
        db: AsyncSession,
    ) -> tuple[str, uuid.UUID]:
        """Have a specialist agent respond to a challenge. Returns (response_text, session_id)."""
        system = build_system_prompt(agent.name, context.dimension, context.phase)
        prompt = (
            f"You have been challenged by Axiom, the adversarial reviewer.\n\n"
            f"## Challenge\n{challenge_text}\n\n"
            f"Respond with specific evidence, reasoning, and any corrections to your original analysis."
        )

        start = time.monotonic()
        content, input_tokens, output_tokens = await agent.raw_chat(prompt, system)
        duration_ms = int((time.monotonic() - start) * 1000)

        cost_cents = (
            input_tokens * COST_PER_INPUT_TOKEN + output_tokens * COST_PER_OUTPUT_TOKEN
        ) * 100

        session = AgentSession(
            perspective_id=context.perspective_id,
            agent_name=agent.name,
            model_used=settings.default_agent_model,
            system_prompt_version="v1",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_cents=round(cost_cents, 4),
            request_payload={"type": "challenge_response", "challenge": challenge_text},
            response_payload={"content": content},
            duration_ms=duration_ms,
        )
        db.add(session)
        await db.flush()

        # Record API usage
        await record_api_usage(
            db, context, agent.name, settings.default_agent_model,
            input_tokens, output_tokens, endpoint=f"boomerang/challenge_response/{agent.name}",
        )

        return content, session.id

    async def evaluate(
        self,
        challenge: Challenge,
        responses: dict[str, str],
        context: AgentContext,
        db: AsyncSession,
    ) -> Verdict:
        """Axiom evaluates agent responses to a challenge and returns a verdict."""
        prompt = build_axiom_verdict_prompt(challenge.challenge_text, responses)
        system = build_system_prompt("axiom", context.dimension, context.phase)

        start = time.monotonic()
        content, input_tokens, output_tokens = await self._axiom.raw_chat(prompt, system)
        duration_ms = int((time.monotonic() - start) * 1000)

        cost_cents = (
            input_tokens * COST_PER_INPUT_TOKEN + output_tokens * COST_PER_OUTPUT_TOKEN
        ) * 100

        session = AgentSession(
            perspective_id=context.perspective_id,
            agent_name="axiom",
            model_used=settings.default_agent_model,
            system_prompt_version="v1",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_cents=round(cost_cents, 4),
            request_payload={"type": "verdict", "challenge": challenge.challenge_text},
            response_payload={"content": content},
            duration_ms=duration_ms,
        )
        db.add(session)
        await db.flush()

        # Record API usage
        await record_api_usage(
            db, context, "axiom", settings.default_agent_model,
            input_tokens, output_tokens, endpoint="boomerang/axiom/verdict",
        )

        return _parse_verdict(content)

    async def stream_challenge(
        self,
        specialist_outputs: dict[str, str],
        context: AgentContext,
        db: AsyncSession,
    ):
        """Stream the full Axiom challenge flow as SSE events.

        Yields SSE events for challenge, responses, and verdicts.
        """
        # Step 1: Axiom produces challenges
        challenges, _raw = await self.challenge(specialist_outputs, context, db)

        for ch in challenges:
            yield sse_event("axiom_challenge", {
                "challenge_text": ch.challenge_text,
                "severity": ch.severity,
                "targeted_agents": ch.targeted_agents,
                "evidence_needed": ch.evidence_needed,
            })

            # Step 2: Targeted agents respond (max 3 LLM calls total per challenge)
            responses: dict[str, str] = {}
            from app.services.agents.base import AGENT_REGISTRY

            for agent_name in ch.targeted_agents:
                if agent_name in AGENT_REGISTRY and agent_name != "axiom":
                    agent = AGENT_REGISTRY[agent_name]
                    response_text, _session_id = await self.get_agent_response(
                        agent, ch.challenge_text, context, db,
                    )
                    responses[agent_name] = response_text
                    yield sse_event("challenge_response", {
                        "agent": agent_name,
                        "challenge_text": ch.challenge_text,
                        "response": response_text,
                    })

            # Step 3: Axiom evaluates
            verdict = await self.evaluate(ch, responses, context, db)
            yield sse_event("axiom_verdict", {
                "challenge_text": ch.challenge_text,
                "resolution": verdict.resolution,
                "resolution_text": verdict.resolution_text,
            })


def _parse_challenges(content: str) -> list[Challenge]:
    """Parse Axiom's JSON challenge output."""
    try:
        # Try to extract JSON from the response (it may be wrapped in markdown code blocks)
        text = content.strip()
        if text.startswith("```"):
            # Strip markdown code block
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        data = json.loads(text)
        if not isinstance(data, list):
            data = [data]

        challenges = []
        for item in data:
            challenges.append(Challenge(
                challenge_text=item.get("challenge_text", ""),
                severity=item.get("severity", "medium"),
                targeted_agents=item.get("targeted_agents", []),
                evidence_needed=item.get("evidence_needed", ""),
            ))
        return challenges
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Failed to parse Axiom challenges: %s", exc)
        return [
            Challenge(
                challenge_text=content,
                severity="medium",
                targeted_agents=[],
                evidence_needed="Unable to parse structured challenges",
            )
        ]


def _parse_verdict(content: str) -> Verdict:
    """Parse Axiom's JSON verdict output."""
    try:
        text = content.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        data = json.loads(text)
        return Verdict(
            resolution=data.get("resolution", "action_required"),
            resolution_text=data.get("resolution_text", ""),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Failed to parse Axiom verdict: %s", exc)
        return Verdict(resolution="action_required", resolution_text=content)
