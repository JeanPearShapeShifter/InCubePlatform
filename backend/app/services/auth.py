import re
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.security import (
    create_access_token,
    decode_token,
    generate_token,
    hash_password,
    hash_token,
    validate_password,
    verify_password,
)
from app.models.auth_token import AuthToken
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import RegisterRequest


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug)
    return slug or "org"


async def register(db: AsyncSession, data: RegisterRequest) -> tuple[User, Organization]:
    validate_password(data.password)

    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise ConflictError("Email already registered")

    slug = _slugify(data.organization_name)
    existing_org = await db.execute(select(Organization).where(Organization.slug == slug))
    if existing_org.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    org = Organization(name=data.organization_name, slug=slug)
    db.add(org)
    await db.flush()

    user = User(
        organization_id=org.id,
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        role="admin",
    )
    db.add(user)
    await db.flush()

    return user, org


async def login(db: AsyncSession, email: str, password: str) -> tuple[User, str]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise ValidationError("Invalid email or password")

    token = create_access_token(str(user.id), str(user.organization_id), user.role)
    user.last_login_at = datetime.now(UTC)
    await db.flush()

    return user, token


async def get_current_user(db: AsyncSession, token: str) -> User:
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise ValidationError("Invalid token")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")
    return user


async def refresh_token(token: str) -> str:
    payload = decode_token(token)
    refresh_exp = payload.get("refresh_exp")
    if not refresh_exp:
        raise ValidationError("Token is not refreshable")

    now = datetime.now(UTC)
    if now.timestamp() > refresh_exp:
        raise ValidationError("Refresh token has expired")

    return create_access_token(payload["sub"], payload["org"], payload["role"])


async def verify_email(db: AsyncSession, token_str: str) -> User:
    token_hash = hash_token(token_str)
    result = await db.execute(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash,
            AuthToken.token_type == "email_verify",
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > datetime.now(UTC),
        )
    )
    auth_token = result.scalar_one_or_none()
    if not auth_token:
        raise ValidationError("Invalid or expired verification token")

    auth_token.used_at = datetime.now(UTC)

    user_result = await db.execute(select(User).where(User.id == auth_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")

    user.email_verified_at = datetime.now(UTC)
    await db.flush()
    return user


async def forgot_password(db: AsyncSession, email: str) -> str | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None

    raw_token = generate_token()
    auth_token = AuthToken(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        token_type="password_reset",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db.add(auth_token)
    await db.flush()
    return raw_token


async def reset_password(db: AsyncSession, token_str: str, new_password: str) -> User:
    validate_password(new_password)

    token_hash = hash_token(token_str)
    result = await db.execute(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash,
            AuthToken.token_type == "password_reset",
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > datetime.now(UTC),
        )
    )
    auth_token = result.scalar_one_or_none()
    if not auth_token:
        raise ValidationError("Invalid or expired reset token")

    auth_token.used_at = datetime.now(UTC)

    user_result = await db.execute(select(User).where(User.id == auth_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")

    user.password_hash = hash_password(new_password)
    await db.flush()
    return user
