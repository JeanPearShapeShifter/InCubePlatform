"""Tests for the AI agent system."""

import json

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes.agents import router as agents_router
from app.core.sse import sse_event
from app.main import app as base_app
from app.services.agents.prompts import (
    AGENT_DEFINITIONS,
    INTERSECTION_LABELS,
    VALID_AGENT_NAMES,
    build_axiom_challenge_prompt,
    build_system_prompt,
)

# Mount agent router for route tests

base_app.include_router(agents_router, prefix="/api")


@pytest.fixture
async def agent_client():
    transport = ASGITransport(app=base_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- SSE utilities ---


def test_sse_event_format():
    result = sse_event("token", {"content": "hello"})
    assert result.startswith("event: token\n")
    assert "data: " in result
    assert result.endswith("\n\n")
    data_line = result.split("\n")[1]
    payload = json.loads(data_line.replace("data: ", ""))
    assert payload["content"] == "hello"


def test_sse_event_escapes_json():
    result = sse_event("token", {"content": 'say "hi"'})
    data_line = result.split("\n")[1]
    payload = json.loads(data_line.replace("data: ", ""))
    assert payload["content"] == 'say "hi"'


# --- Agent name validation ---


def test_valid_agent_names():
    expected = {"lyra", "mira", "dex", "rex", "vela", "koda", "halo", "nova", "axiom"}
    assert set(VALID_AGENT_NAMES) == expected


def test_agent_definitions_complete():
    for name in VALID_AGENT_NAMES:
        assert name in AGENT_DEFINITIONS
        role, color, persona = AGENT_DEFINITIONS[name]
        assert role
        assert color
        assert persona


# --- System prompts ---


def test_build_system_prompt_without_context():
    prompt = build_system_prompt("lyra")
    assert "Lyra" in prompt
    assert "Goal" in prompt


def test_build_system_prompt_with_context():
    prompt = build_system_prompt("lyra", dimension="architecture", phase="generate")
    assert "Imagining" in prompt
    assert "Architecture" in prompt
    assert "Generate" in prompt


def test_build_system_prompt_all_agents():
    for name in VALID_AGENT_NAMES:
        prompt = build_system_prompt(name)
        assert len(prompt) > 50


def test_intersection_labels_complete():
    dimensions = ["architecture", "design", "engineering"]
    phases = ["generate", "review", "validate", "summarize"]
    for dim in dimensions:
        for phase in phases:
            assert (dim, phase) in INTERSECTION_LABELS


# --- Axiom prompts ---


def test_build_axiom_challenge_prompt():
    outputs = {"lyra": "Goal analysis here", "dex": "Requirements analysis here"}
    prompt = build_axiom_challenge_prompt(outputs)
    assert "Lyra" in prompt
    assert "Goal analysis here" in prompt
    assert "Dex" in prompt
    assert "JSON array" in prompt


# --- BaseAgent ---


def test_base_agent_creation():
    from app.services.agents.base import BaseAgent

    agent = BaseAgent("lyra")
    assert agent.name == "lyra"
    assert agent.role == "Goal"
    assert agent.color == "purple"


def test_base_agent_invalid_name():
    from app.services.agents.base import BaseAgent

    with pytest.raises(ValueError, match="Unknown agent"):
        BaseAgent("invalid_agent")


# --- Agent registry ---


def test_agent_registry_has_all_agents():
    from app.services.agents.base import AGENT_REGISTRY

    assert set(AGENT_REGISTRY.keys()) == set(VALID_AGENT_NAMES)


# --- Route validation (unit, no DB) ---


@pytest.mark.asyncio
async def test_chat_endpoint_rejects_invalid_agent(agent_client):
    """Test that invalid agent names are rejected."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = await agent_client.post(
        f"/api/perspectives/{fake_id}/agents/invalid_agent/chat",
        json={"message": "test"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "invalid" in data["error"]["message"].lower() or "Invalid" in data["error"]["message"]


@pytest.mark.asyncio
async def test_boomerang_endpoint_exists(agent_client):
    """Test that the boomerang endpoint is registered."""
    import uuid

    fake_id = str(uuid.uuid4())
    response = await agent_client.post(
        f"/api/perspectives/{fake_id}/boomerang",
        json={"prompt": "test"},
    )
    # 404 for missing perspective is fine; 405 would mean route doesn't exist
    assert response.status_code != 405


def test_agent_sessions_endpoint_exists():
    """Test that the agent-sessions route is registered in the app."""
    routes = [r.path for r in base_app.routes if hasattr(r, "path")]
    assert any("agent-sessions" in r for r in routes)


def test_axiom_challenges_endpoint_exists():
    """Test that the axiom challenges route is registered in the app."""
    routes = [r.path for r in base_app.routes if hasattr(r, "path")]
    assert any("axiom/challenges" in r for r in routes)


# --- Cost calculation ---


def test_cost_calculation():
    from app.services.agents.base import COST_PER_INPUT_TOKEN, COST_PER_OUTPUT_TOKEN

    # 1M input tokens should cost $0.25 = 25 cents
    cost_cents = 1_000_000 * COST_PER_INPUT_TOKEN * 100
    assert abs(cost_cents - 25.0) < 0.001

    # 1M output tokens should cost $1.25 = 125 cents
    cost_cents = 1_000_000 * COST_PER_OUTPUT_TOKEN * 100
    assert abs(cost_cents - 125.0) < 0.001


# --- Axiom parsing ---


def test_parse_challenges_valid_json():
    from app.services.agents.axiom import _parse_challenges

    content = json.dumps([
        {
            "challenge_text": "No evidence for ROI claim",
            "severity": "high",
            "targeted_agents": ["vela", "lyra"],
            "evidence_needed": "Quantitative ROI analysis",
        }
    ])
    challenges = _parse_challenges(content)
    assert len(challenges) == 1
    assert challenges[0].challenge_text == "No evidence for ROI claim"
    assert challenges[0].severity == "high"
    assert "vela" in challenges[0].targeted_agents


def test_parse_challenges_markdown_wrapped():
    from app.services.agents.axiom import _parse_challenges

    content = (
        '```json\n[{"challenge_text": "test", "severity": "low",'
        ' "targeted_agents": [], "evidence_needed": ""}]\n```'
    )
    challenges = _parse_challenges(content)
    assert len(challenges) == 1
    assert challenges[0].challenge_text == "test"


def test_parse_challenges_invalid_json_fallback():
    from app.services.agents.axiom import _parse_challenges

    challenges = _parse_challenges("This is not JSON at all")
    assert len(challenges) == 1
    assert challenges[0].severity == "medium"
    assert "This is not JSON at all" in challenges[0].challenge_text


def test_parse_verdict_valid():
    from app.services.agents.axiom import _parse_verdict

    content = json.dumps({"resolution": "resolved", "resolution_text": "All concerns addressed"})
    verdict = _parse_verdict(content)
    assert verdict.resolution == "resolved"
    assert verdict.resolution_text == "All concerns addressed"


def test_parse_verdict_invalid_fallback():
    from app.services.agents.axiom import _parse_verdict

    verdict = _parse_verdict("Not valid JSON")
    assert verdict.resolution == "action_required"
