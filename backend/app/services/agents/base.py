"""Base agent class with Claude API streaming and session tracking."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.sse import sse_event
from app.models.agent_session import AgentSession
from app.services.agents.prompts import AGENT_DEFINITIONS, build_system_prompt

logger = logging.getLogger(__name__)

# Haiku pricing: input $0.25/MTok, output $1.25/MTok (in dollars)
COST_PER_INPUT_TOKEN = 0.25 / 1_000_000   # dollars per token
COST_PER_OUTPUT_TOKEN = 1.25 / 1_000_000   # dollars per token


@dataclass
class AgentContext:
    """Context passed to an agent for a chat request."""

    perspective_id: uuid.UUID
    dimension: str | None = None
    phase: str | None = None
    goal_statement: str | None = None


class BaseAgent:
    """A single InCube cognitive agent backed by the Claude API."""

    def __init__(self, name: str):
        if name not in AGENT_DEFINITIONS:
            raise ValueError(f"Unknown agent: {name}")
        role, color, _persona = AGENT_DEFINITIONS[name]
        self.name = name
        self.role = role
        self.color = color
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def chat(
        self,
        message: str,
        context: AgentContext,
        db: AsyncSession,
    ) -> AsyncGenerator[str, None]:
        """Stream a response from the Claude API, yielding SSE-formatted events."""
        system_prompt = build_system_prompt(self.name, context.dimension, context.phase)
        model = settings.default_agent_model

        start = time.monotonic()
        full_response = ""
        input_tokens = 0
        output_tokens = 0

        try:
            async with self._client.messages.stream(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": message}],
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    yield sse_event("token", {"agent": self.name, "content": text})

                response = await stream.get_final_message()
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

        except anthropic.APIError as exc:
            logger.error("Anthropic API error for agent %s: %s", self.name, exc)
            yield sse_event("error", {"agent": self.name, "error": str(exc)})
            return

        duration_ms = int((time.monotonic() - start) * 1000)
        cost_cents = (
            input_tokens * COST_PER_INPUT_TOKEN + output_tokens * COST_PER_OUTPUT_TOKEN
        ) * 100  # convert dollars to cents

        session = AgentSession(
            perspective_id=context.perspective_id,
            agent_name=self.name,
            model_used=model,
            system_prompt_version="v1",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_cents=round(cost_cents, 4),
            request_payload={"message": message, "system": system_prompt},
            response_payload={"content": full_response},
            duration_ms=duration_ms,
        )
        db.add(session)
        await db.flush()

        yield sse_event("done", {
            "agent": self.name,
            "session_id": str(session.id),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_cents": round(cost_cents, 4),
            "duration_ms": duration_ms,
        })

    async def raw_chat(self, message: str, system_prompt: str) -> tuple[str, int, int]:
        """Non-streaming chat that returns (content, input_tokens, output_tokens).

        Used internally by the orchestrator and Axiom for structured responses.
        """
        response = await self._client.messages.create(
            model=settings.default_agent_model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": message}],
        )
        content = response.content[0].text
        return content, response.usage.input_tokens, response.usage.output_tokens


# Registry of all 9 agents
AGENT_REGISTRY: dict[str, BaseAgent] = {name: BaseAgent(name) for name in AGENT_DEFINITIONS}
