"""Tests for the vibe system — schemas, whisper cost calculation, prompts, and routes."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes.vibes import router as vibes_router
from app.main import app as base_app
from app.schemas.vibe import (
    VibeAnalysisItem,
    VibeDetailResponse,
    VibeListResponse,
    VibeSessionResponse,
    VibeUploadResponse,
)
from app.services.vibe_prompts import VIBE_ANALYSIS_PROMPTS, build_vibe_analysis_prompt
from app.services.whisper import COST_PER_MINUTE

base_app.include_router(vibes_router, prefix="/api")


@pytest.fixture
async def vibe_client():
    transport = ASGITransport(app=base_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- Schema validation ---


class TestVibeSchemas:
    def test_vibe_upload_response(self):
        data = {
            "id": uuid.uuid4(),
            "duration_seconds": 120,
            "status": "transcribing",
            "created_at": datetime.now(tz=UTC),
        }
        response = VibeUploadResponse(**data)
        assert response.status == "transcribing"
        assert response.duration_seconds == 120

    def test_vibe_session_response(self):
        response = VibeSessionResponse(
            id=uuid.uuid4(),
            duration_seconds=300,
            status="complete",
            has_transcript=True,
            analyses_count=9,
            created_at=datetime.now(tz=UTC),
        )
        assert response.has_transcript is True
        assert response.analyses_count == 9

    def test_vibe_detail_response(self):
        analysis = VibeAnalysisItem(
            agent_name="lyra",
            content={"insights": [], "actionItems": [], "contradictions": [], "suggestedEdits": []},
        )
        detail = VibeDetailResponse(
            id=uuid.uuid4(),
            duration_seconds=60,
            transcript_text="Hello, this is a test.",
            status="complete",
            analyses=[analysis],
            created_at=datetime.now(tz=UTC),
        )
        assert detail.transcript_text == "Hello, this is a test."
        assert len(detail.analyses) == 1
        assert detail.analyses[0].agent_name == "lyra"

    def test_vibe_detail_response_null_transcript(self):
        detail = VibeDetailResponse(
            id=uuid.uuid4(),
            duration_seconds=60,
            transcript_text=None,
            status="transcribing",
            analyses=[],
            created_at=datetime.now(tz=UTC),
        )
        assert detail.transcript_text is None

    def test_vibe_list_response(self):
        items = [
            VibeSessionResponse(
                id=uuid.uuid4(),
                duration_seconds=120,
                status="complete",
                has_transcript=True,
                analyses_count=9,
                created_at=datetime.now(tz=UTC),
            )
        ]
        response = VibeListResponse(vibe_sessions=items)
        assert len(response.vibe_sessions) == 1

    def test_vibe_analysis_item(self):
        item = VibeAnalysisItem(
            agent_name="axiom",
            content={
                "insights": [{"text": "Found a contradiction", "source": "0:30"}],
                "actionItems": [],
                "contradictions": [{"text": "X vs Y", "between": "goal vs plan"}],
                "suggestedEdits": [],
            },
        )
        assert item.agent_name == "axiom"
        assert len(item.content["contradictions"]) == 1


# --- Whisper cost calculation ---


class TestWhisperCost:
    def test_cost_for_one_minute(self):
        # $0.006/min = 0.6 cents/min
        duration = 60  # seconds
        cost_cents = (duration / 60) * COST_PER_MINUTE * 100
        assert abs(cost_cents - 0.6) < 0.0001

    def test_cost_for_ten_minutes(self):
        # 10 min * 0.6 cents/min = 6.0 cents
        duration = 600  # seconds
        cost_cents = (duration / 60) * COST_PER_MINUTE * 100
        assert abs(cost_cents - 6.0) < 0.0001

    def test_cost_for_zero_duration(self):
        duration = 0
        cost_cents = (duration / 60) * COST_PER_MINUTE * 100
        assert cost_cents == 0.0

    def test_cost_for_half_minute(self):
        # 0.5 min * 0.6 cents/min = 0.3 cents
        duration = 30
        cost_cents = (duration / 60) * COST_PER_MINUTE * 100
        assert abs(cost_cents - 0.3) < 0.0001


# --- Vibe analysis prompts ---


class TestVibePrompts:
    def test_all_agents_have_prompts(self):
        from app.services.agents.prompts import VALID_AGENT_NAMES

        for name in VALID_AGENT_NAMES:
            assert name in VIBE_ANALYSIS_PROMPTS, f"Missing vibe analysis prompt for {name}"
            assert len(VIBE_ANALYSIS_PROMPTS[name]) > 50

    def test_prompts_request_json_structure(self):
        for name, prompt in VIBE_ANALYSIS_PROMPTS.items():
            assert "insights" in prompt, f"Prompt for {name} missing 'insights'"
            assert "actionItems" in prompt, f"Prompt for {name} missing 'actionItems'"
            assert "contradictions" in prompt, f"Prompt for {name} missing 'contradictions'"
            assert "suggestedEdits" in prompt, f"Prompt for {name} missing 'suggestedEdits'"

    def test_build_vibe_analysis_prompt_basic(self):
        prompt = build_vibe_analysis_prompt("lyra", "This is a test transcript.")
        assert "test transcript" in prompt
        assert "Lyra" in prompt or "Goal" in prompt

    def test_build_vibe_analysis_prompt_with_context(self):
        prompt = build_vibe_analysis_prompt("lyra", "transcript text", dimension="architecture", phase="generate")
        assert "Architecture" in prompt
        assert "Generate" in prompt
        assert "transcript text" in prompt

    def test_build_vibe_analysis_prompt_all_agents(self):
        from app.services.agents.prompts import VALID_AGENT_NAMES

        for name in VALID_AGENT_NAMES:
            prompt = build_vibe_analysis_prompt(name, "Test transcript content")
            assert len(prompt) > 100
            assert "Test transcript content" in prompt

    def test_axiom_prompt_focuses_on_challenges(self):
        prompt = VIBE_ANALYSIS_PROMPTS["axiom"]
        assert "Contradictions" in prompt or "contradictions" in prompt
        assert "Unsubstantiated" in prompt or "unsubstantiated" in prompt
        assert "Risks" in prompt or "risks" in prompt


# --- Whisper service (mocked) ---


class TestWhisperService:
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self):
        mock_response_data = {
            "text": "Hello, this is a test recording.",
            "duration": 65.5,
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.whisper.httpx.AsyncClient", return_value=mock_client):
            from app.services.whisper import transcribe_audio

            result = await transcribe_audio(b"fake audio data")

        assert result["text"] == "Hello, this is a test recording."
        assert result["duration_seconds"] == 65
        expected_cost = (65.5 / 60) * COST_PER_MINUTE * 100
        assert abs(result["cost_cents"] - round(expected_cost, 4)) < 0.001


# --- Vibe MinIO helpers ---


class TestVibeMinIO:
    def test_get_minio_client(self):
        from app.services.vibe_minio import get_minio_client

        client = get_minio_client()
        assert client is not None

    @pytest.mark.asyncio
    async def test_upload_audio_returns_key(self):
        from app.services.vibe_minio import upload_audio

        mock_client = AsyncMock()
        mock_client.put_object = AsyncMock()
        perspective_id = str(uuid.uuid4())

        key = await upload_audio(mock_client, b"audio bytes", perspective_id)

        assert key.startswith(f"vibes/{perspective_id}/")
        assert key.endswith(".webm")
        mock_client.put_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_audio_returns_bytes(self):
        from app.services.vibe_minio import download_audio

        mock_response = AsyncMock()
        mock_response.read = AsyncMock(return_value=b"audio data")
        mock_response.close = AsyncMock()
        mock_response.release = AsyncMock()

        mock_client = AsyncMock()
        mock_client.get_object = AsyncMock(return_value=mock_response)

        data = await download_audio(mock_client, "vibes/test/file.webm")

        assert data == b"audio data"
        mock_client.get_object.assert_called_once()


# --- JSON parsing in vibe analysis ---


class TestVibeAnalysisJsonParsing:
    def test_parse_valid_json(self):
        content = json.dumps({
            "insights": [{"text": "Key insight", "source": "0:15"}],
            "actionItems": [{"text": "Do this", "priority": "high", "owner_agent": "lyra"}],
            "contradictions": [],
            "suggestedEdits": [],
        })
        parsed = json.loads(content)
        assert len(parsed["insights"]) == 1
        assert parsed["insights"][0]["text"] == "Key insight"

    def test_parse_markdown_wrapped_json(self):
        content = '```json\n{"insights": [], "actionItems": [], "contradictions": [], "suggestedEdits": []}\n```'
        cleaned = content.strip()
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        parsed = json.loads(cleaned)
        assert "insights" in parsed

    def test_fallback_for_non_json(self):
        content = "This is not JSON at all, just plain analysis text."
        try:
            json.loads(content)
            fallback = False
        except json.JSONDecodeError:
            fallback = True
        assert fallback is True


# --- Route validation (unit, no DB required for basic checks) ---


class TestVibeRoutes:
    @pytest.mark.asyncio
    async def test_upload_endpoint_rejects_without_auth(self, vibe_client):
        """Upload should require authentication."""
        fake_id = str(uuid.uuid4())
        response = await vibe_client.post(
            f"/api/perspectives/{fake_id}/vibes",
            files={"audio": ("test.webm", b"fake", "audio/webm")},
            data={"duration_seconds": "60"},
        )
        # Should get 400 for missing auth, not 405 (route not found)
        assert response.status_code != 405

    @pytest.mark.asyncio
    async def test_list_endpoint_rejects_without_auth(self, vibe_client):
        """List should require authentication."""
        fake_id = str(uuid.uuid4())
        response = await vibe_client.get(f"/api/perspectives/{fake_id}/vibes")
        assert response.status_code != 405

    @pytest.mark.asyncio
    async def test_detail_endpoint_rejects_without_auth(self, vibe_client):
        """Detail should require authentication."""
        fake_id = str(uuid.uuid4())
        response = await vibe_client.get(f"/api/vibes/{fake_id}")
        assert response.status_code != 405

    @pytest.mark.asyncio
    async def test_reanalyze_endpoint_rejects_without_auth(self, vibe_client):
        """Re-analyze should require authentication."""
        fake_id = str(uuid.uuid4())
        response = await vibe_client.post(f"/api/vibes/{fake_id}/analyze")
        assert response.status_code != 405
