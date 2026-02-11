from collections.abc import AsyncGenerator, Callable

from fastapi import Cookie, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenError, UnauthorizedError
from app.db.session import async_session_factory
from app.models.enums import UserRole
from app.models.user import User
from app.services import auth as auth_service

ROLE_HIERARCHY = {
    UserRole.ADMIN: 3,
    UserRole.EDITOR: 2,
    UserRole.VIEWER: 1,
}


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    access_token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
) -> User:
    token = None
    if access_token:
        token = access_token
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token:
        raise UnauthorizedError("Not authenticated")

    return await auth_service.get_current_user(db, token)


def require_role(min_role: str) -> Callable:
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        user_level = ROLE_HIERARCHY.get(UserRole(current_user.role), 0)
        required_level = ROLE_HIERARCHY.get(UserRole(min_role), 0)
        if user_level < required_level:
            raise ForbiddenError("Insufficient permissions")
        return current_user

    return _check
