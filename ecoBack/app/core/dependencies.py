from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import user_repository

settings = get_settings()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth[7:]

    if not token:
        raise UnauthorizedException(message="Could not validate credentials")

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException(message="Could not validate credentials")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(message="Could not validate credentials")

    user = await user_repository.get_with_role(db, UUID(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedException(message="Could not validate credentials")

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role.name != "admin":
        raise ForbiddenException(message="Not enough permissions")
    return current_user
