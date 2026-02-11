from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.email import (
    build_budget_alert_email,
    build_journey_complete_email,
    build_stakeholder_invite_email,
    build_vdba_published_email,
    build_vibe_summary_email,
    send_email,
)


class TestSendEmail:
    @pytest.mark.asyncio
    async def test_send_email_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "msg_123"}

        with patch("app.services.email.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with patch("app.services.email.settings") as mock_settings:
                mock_settings.resend_api_key = "test-key"
                mock_settings.resend_from_email = "test@incube.ai"

                result = await send_email("user@example.com", "Test", "<p>Hello</p>")
                assert result == "msg_123"
                mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure_returns_none(self):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}

        with patch("app.services.email.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with patch("app.services.email.settings") as mock_settings:
                mock_settings.resend_api_key = "test-key"
                mock_settings.resend_from_email = "test@incube.ai"

                result = await send_email("user@example.com", "Test", "<p>Hello</p>")
                assert result is None

    @pytest.mark.asyncio
    async def test_send_email_no_api_key_returns_none(self):
        with patch("app.services.email.settings") as mock_settings:
            mock_settings.resend_api_key = ""

            result = await send_email("user@example.com", "Test", "<p>Hello</p>")
            assert result is None


class TestEmailTemplates:
    def test_stakeholder_invite_email(self):
        context = {"dimension": "Architecture", "phase": "Generate", "journey_name": "Test Journey"}
        subject, body = build_stakeholder_invite_email(context, "Please review this")
        assert "Test Journey" in subject
        assert "Architecture" in body
        assert "Generate" in body
        assert "Please review this" in body

    def test_stakeholder_invite_without_custom_message(self):
        context = {"dimension": "Design", "phase": "Review", "journey_name": "My Journey"}
        subject, body = build_stakeholder_invite_email(context, "")
        assert "My Journey" in subject
        assert "Design" in body

    def test_vibe_summary_email(self):
        data = {"journey_name": "Test Journey", "duration_minutes": 30, "agent_count": 5}
        subject, body = build_vibe_summary_email(data)
        assert "Test Journey" in subject
        assert "30" in body
        assert "5" in body

    def test_journey_complete_email(self):
        data = {"journey_name": "Completed Journey"}
        subject, body = build_journey_complete_email(data)
        assert "Completed Journey" in subject
        assert "completed" in body.lower()

    def test_vdba_published_email(self):
        data = {"journey_name": "Published Journey"}
        subject, body = build_vdba_published_email(data)
        assert "Published Journey" in subject
        assert "published" in body.lower()

    def test_budget_alert_email(self):
        data = {"current_spend": 95.50, "threshold": 100.00, "org_name": "Test Org"}
        subject, body = build_budget_alert_email(data)
        assert "Test Org" in subject
        assert "$95.50" in body
        assert "$100.00" in body
