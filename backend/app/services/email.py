import httpx

from app.core.config import settings

RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(to: str, subject: str, html_body: str) -> str | None:
    """Send email via Resend API. Returns message_id or None on failure."""
    if not settings.resend_api_key:
        return None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            RESEND_API_URL,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.resend_from_email,
                "to": [to],
                "subject": subject,
                "html": html_body,
            },
            timeout=10.0,
        )
        if response.status_code == 200:
            return response.json().get("id")
        return None


def build_stakeholder_invite_email(perspective_context: dict, custom_message: str) -> tuple[str, str]:
    """Returns (subject, html_body) for stakeholder invite."""
    dimension = perspective_context.get("dimension", "")
    phase = perspective_context.get("phase", "")
    journey_name = perspective_context.get("journey_name", "InCube Journey")

    subject = f"You're invited to review: {journey_name} - {dimension} {phase}"
    msg_block = ""
    if custom_message:
        msg_block = (
            f'<p style="margin: 16px 0; padding: 12px; background: #f5f5f5;'
            f' border-radius: 4px;">{custom_message}</p>'
        )

    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>InCube Stakeholder Review</h2>
        <p>You've been invited to review the <strong>{dimension} - {phase}</strong> perspective
        for <strong>{journey_name}</strong>.</p>
        {msg_block}
        <p>Please log in to the InCube platform to provide your feedback.</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;" />
        <p style="color: #888; font-size: 12px;">Sent via InCube Platform</p>
    </div>
    """
    return subject, html_body


def build_vibe_summary_email(vibe_data: dict) -> tuple[str, str]:
    """Returns (subject, html_body) for vibe summary."""
    journey_name = vibe_data.get("journey_name", "InCube Journey")
    duration = vibe_data.get("duration_minutes", 0)
    agent_count = vibe_data.get("agent_count", 0)

    subject = f"Vibe Session Summary: {journey_name}"
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Vibe Session Summary</h2>
        <p>A vibe session for <strong>{journey_name}</strong> has been completed.</p>
        <ul>
            <li>Duration: {duration} minutes</li>
            <li>Agents involved: {agent_count}</li>
        </ul>
        <p>Log in to the InCube platform to review the full analysis.</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;" />
        <p style="color: #888; font-size: 12px;">Sent via InCube Platform</p>
    </div>
    """
    return subject, html_body


def build_journey_complete_email(journey_data: dict) -> tuple[str, str]:
    """Returns (subject, html_body) for journey complete."""
    journey_name = journey_data.get("journey_name", "InCube Journey")

    subject = f"Journey Complete: {journey_name}"
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Journey Complete</h2>
        <p>The journey <strong>{journey_name}</strong> has been completed.</p>
        <p>All perspectives have been reviewed and banked. You can now publish the final VDBA.</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;" />
        <p style="color: #888; font-size: 12px;">Sent via InCube Platform</p>
    </div>
    """
    return subject, html_body


def build_vdba_published_email(vdba_data: dict) -> tuple[str, str]:
    """Returns (subject, html_body) for VDBA published."""
    journey_name = vdba_data.get("journey_name", "InCube Journey")

    subject = f"VDBA Published: {journey_name}"
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>VDBA Published</h2>
        <p>The VDBA for <strong>{journey_name}</strong> has been published and is now available.</p>
        <p>Log in to the InCube platform to view the published document.</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;" />
        <p style="color: #888; font-size: 12px;">Sent via InCube Platform</p>
    </div>
    """
    return subject, html_body


def build_budget_alert_email(usage_data: dict) -> tuple[str, str]:
    """Returns (subject, html_body) for budget alert."""
    current_spend = usage_data.get("current_spend", 0)
    threshold = usage_data.get("threshold", 0)
    org_name = usage_data.get("org_name", "your organization")

    subject = f"Budget Alert: {org_name} API usage threshold reached"
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2>Budget Alert</h2>
        <p>API usage for <strong>{org_name}</strong> has reached the configured threshold.</p>
        <ul>
            <li>Current spend: ${current_spend:.2f}</li>
            <li>Threshold: ${threshold:.2f}</li>
        </ul>
        <p>Please review your API usage in the InCube settings.</p>
        <hr style="margin: 24px 0; border: none; border-top: 1px solid #eee;" />
        <p style="color: #888; font-size: 12px;">Sent via InCube Platform</p>
    </div>
    """
    return subject, html_body


TEMPLATE_BUILDERS = {
    "stakeholder_invite": build_stakeholder_invite_email,
    "vibe_summary": build_vibe_summary_email,
    "journey_complete": build_journey_complete_email,
    "vdba_published": build_vdba_published_email,
    "budget_alert": build_budget_alert_email,
}
