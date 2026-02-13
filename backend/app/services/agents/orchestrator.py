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
    COST_PER_INPUT_TOKEN,
    COST_PER_OUTPUT_TOKEN,
    AgentContext,
    BaseAgent,
    FatalAgentError,
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

        # Phase 1: Run 8 specialist agents in parallel, stream results as they arrive
        yield sse_event("phase", {"phase": "specialists", "message": "Running specialist agents..."})
        specialist_outputs: dict[str, str] = {}

        async def run_specialist(agent: BaseAgent) -> tuple[str, str, int, int]:
            system = build_system_prompt(agent.name, context.dimension, context.phase)
            content, in_tok, out_tok = await agent.raw_chat(prompt, system)
            return agent.name, content, in_tok, out_tok

        # Notify start of each agent
        for name in SPECIALIST_AGENTS:
            yield sse_event("agent_start", {"agent": name})

        # Use as_completed so we yield agent_complete events as each finishes
        # instead of waiting for all 8 to complete before sending any events
        tasks = {
            asyncio.ensure_future(run_specialist(AGENT_REGISTRY[name])): name
            for name in SPECIALIST_AGENTS
        }

        fatal_error: FatalAgentError | None = None

        for coro in asyncio.as_completed(list(tasks.keys())):
            try:
                name, content, in_tok, out_tok = await coro
            except FatalAgentError as exc:
                # Fatal error — cancel all pending tasks and abort immediately
                failed_name = "unknown"
                for task, task_name in tasks.items():
                    if task.done():
                        try:
                            task.exception()
                        except BaseException:
                            if task_name != "unknown":
                                failed_name = task_name
                                break
                logger.error("Fatal API error from %s: %s", failed_name, exc)
                yield sse_event("agent_error", {
                    "agent": failed_name,
                    "error": str(exc),
                    "error_type": exc.error_type,
                })
                fatal_error = exc
                # Cancel all still-pending tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                break
            except Exception as exc:
                # Find which agent failed
                failed_name = "unknown"
                for task, task_name in tasks.items():
                    if task.done() and task.exception() is exc:
                        failed_name = task_name
                        break
                logger.error("Specialist agent %s failed: %s", failed_name, exc)
                yield sse_event("agent_error", {
                    "agent": failed_name,
                    "error": str(exc),
                    "error_type": "unknown",
                })
                continue

            specialist_outputs[name] = content

            # Record API usage for this specialist call
            await record_api_usage(
                db, context, name, app_settings.default_agent_model,
                in_tok, out_tok, endpoint=f"boomerang/specialist/{name}",
            )

            cost_usd = in_tok * COST_PER_INPUT_TOKEN + out_tok * COST_PER_OUTPUT_TOKEN
            yield sse_event("agent_complete", {
                "agent": name,
                "content": content,
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "cost_usd": round(cost_usd, 6),
            })
            yield sse_event("phase", {
                "phase": "specialists",
                "message": f"{len(specialist_outputs)}/{len(SPECIALIST_AGENTS)} specialists complete...",
            })

        # If a fatal error occurred, abort the entire flow
        if fatal_error is not None:
            _error_messages = {
                "credit_balance": "API credit balance exhausted. Add credits at console.anthropic.com to continue.",
                "auth": "Invalid API key. Check your API key in Settings.",
            }
            yield sse_event("boomerang_error", {
                "error": _error_messages.get(fatal_error.error_type, str(fatal_error)),
                "error_type": fatal_error.error_type,
            })
            yield sse_event("boomerang_complete", {
                "perspective_id": str(context.perspective_id),
                "agents_completed": list(specialist_outputs.keys()),
                "aborted": True,
                "error_type": fatal_error.error_type,
            })
            return

        if not specialist_outputs:
            yield sse_event("error", {"error": "All specialist agents failed"})
            return

        # Phase 2: Axiom challenge flow
        logger.info("Specialists complete (%d/%d). Starting Axiom challenge phase.",
                     len(specialist_outputs), len(SPECIALIST_AGENTS))
        yield sse_event("phase", {"phase": "axiom", "message": "Axiom is reviewing specialist outputs..."})
        yield sse_event("axiom_start", {"agent": "axiom"})

        try:
            async for event in self._challenger.stream_challenge(specialist_outputs, context, db):
                yield event
        except FatalAgentError as exc:
            logger.error("Axiom phase hit fatal error: %s", exc)
            yield sse_event("agent_error", {
                "agent": "axiom",
                "error": str(exc),
                "error_type": exc.error_type,
            })
            yield sse_event("boomerang_error", {
                "error": str(exc),
                "error_type": exc.error_type,
            })
        except Exception as exc:
            logger.exception("Axiom challenge phase failed")
            yield sse_event("agent_error", {
                "agent": "axiom",
                "error": f"Axiom challenge phase failed: {exc}",
                "error_type": "unknown",
            })

        logger.info("Axiom phase complete. Emitting boomerang_complete.")
        yield sse_event("boomerang_complete", {
            "perspective_id": str(context.perspective_id),
            "agents_completed": list(specialist_outputs.keys()),
        })
