import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import ValidationError
from app.models.email_log import EmailLog
from app.schemas.email import EmailListResponse, EmailLogResponse, SendEmailRequest
from app.services.email import TEMPLATE_BUILDERS, send_email

router = APIRouter()


@router.post("/perspectives/{perspective_id}/email", response_model=EmailLogResponse, status_code=201)
async def send_perspective_email(
    perspective_id: uuid.UUID,
    data: SendEmailRequest,
    # TODO: replace with get_current_user dependency
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> EmailLogResponse:
    builder = TEMPLATE_BUILDERS.get(data.template_type.value)
    if not builder:
        raise ValidationError(f"Unknown template type: {data.template_type}")

    # Build email content based on template type
    if data.template_type.value == "stakeholder_invite":
        context = {"perspective_id": str(perspective_id), "custom_message": data.custom_message}
        subject, html_body = builder(context, data.custom_message)
    else:
        context = {"perspective_id": str(perspective_id)}
        subject, html_body = builder(context)

    message_id = await send_email(data.recipient_email, subject, html_body)

    log = EmailLog(
        perspective_id=perspective_id,
        sent_by=user_id,
        recipient_email=data.recipient_email,
        template_type=data.template_type.value,
        subject=subject,
        body_preview=html_body[:500] if html_body else None,
        resend_message_id=message_id,
        delivery_status="sent" if message_id else "failed",
        sent_at=datetime.now(UTC),
    )
    db.add(log)
    await db.flush()

    return EmailLogResponse.model_validate(log)


@router.get("/perspectives/{perspective_id}/emails", response_model=EmailListResponse)
async def list_emails(
    perspective_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> EmailListResponse:
    result = await db.execute(
        select(EmailLog).where(EmailLog.perspective_id == perspective_id).order_by(EmailLog.sent_at.desc())
    )
    logs = list(result.scalars().all())
    return EmailListResponse(emails=[EmailLogResponse.model_validate(log) for log in logs])
