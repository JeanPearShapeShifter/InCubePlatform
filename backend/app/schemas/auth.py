import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    organization_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    avatar_url: str | None
    organization_id: uuid.UUID

    model_config = {"from_attributes": True}


class OrganizationNested(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    logo_url: str | None
    monthly_budget_cents: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    avatar_url: str | None
    organization_id: uuid.UUID
    organization: OrganizationNested

    model_config = {"from_attributes": True}


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class VerifyEmailRequest(BaseModel):
    token: str
