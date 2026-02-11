import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import EmailTemplate


class SendEmailRequest(BaseModel):
    recipient_email: EmailStr
    template_type: EmailTemplate
    custom_message: str = Field(default="", max_length=2000)


class EmailLogResponse(BaseModel):
    id: uuid.UUID
    perspective_id: uuid.UUID
    recipient_email: str
    template_type: str
    subject: str
    delivery_status: str
    sent_at: datetime

    model_config = {"from_attributes": True}


class EmailListResponse(BaseModel):
    emails: list[EmailLogResponse]
