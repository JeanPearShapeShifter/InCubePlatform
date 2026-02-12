import hashlib
import re
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.errors import UnauthorizedError, ValidationError

ALGORITHM = "HS256"


def create_access_token(user_id: str, org_id: str, role: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "org": str(org_id),
        "role": role,
        "exp": now + timedelta(minutes=settings.jwt_access_minutes),
        "refresh_exp": int((now + timedelta(days=settings.jwt_refresh_days)).timestamp()),
        "iat": now,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise UnauthorizedError("Invalid or expired token") from e


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number")


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
