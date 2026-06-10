import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import RegisterRequest
from app.utils.exceptions import (
    CredentialsException,
    EmailAlreadyRegistered,
    InvalidToken,
    UserNotFoundException,
    UsernameAlreadyRegistered,
)

settings = get_settings()


class AuthService:
    async def register(self, db: AsyncSession, request: RegisterRequest) -> User:
        existing_email = await user_repository.get_by_email(db, request.email)
        if existing_email:
            raise EmailAlreadyRegistered()

        existing_username = await user_repository.get_by_username(db, request.username)
        if existing_username:
            raise UsernameAlreadyRegistered()

        user_role = await user_repository.get_user_role(db)
        if user_role is None:
            raise ValueError("Default user role not found. Run init_db first.")

        user = await user_repository.create(
            db,
            id=uuid.uuid4(),
            email=request.email,
            username=request.username,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
            role_id=user_role.id,
        )
        await db.refresh(user, ["role"])
        return user

    async def login(self, db: AsyncSession, email: str, password: str) -> tuple[str, str, User]:
        user = await user_repository.get_by_email(db, email)
        if user is None or not verify_password(password, user.hashed_password):
            raise CredentialsException()

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_str = create_refresh_token(data={"sub": str(user.id)})

        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self._store_refresh_token(db, user.id, refresh_token_str, expires_at)

        return access_token, refresh_token_str, user

    async def refresh(self, db: AsyncSession, raw_refresh_token: str) -> tuple[str, str]:
        token_hash = hash_refresh_token(raw_refresh_token)
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
        )
        stored_token = result.scalar_one_or_none()
        if stored_token is None:
            raise InvalidToken()

        payload = decode_token(raw_refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise InvalidToken()

        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidToken()

        stored_token.is_revoked = True
        await db.flush()

        new_access = create_access_token(data={"sub": user_id})
        new_refresh = create_refresh_token(data={"sub": user_id})

        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self._store_refresh_token(db, uuid.UUID(user_id), new_refresh, expires_at)

        return new_access, new_refresh

    async def logout(self, db: AsyncSession, raw_refresh_token: str | None) -> None:
        if raw_refresh_token is None:
            return
        token_hash = hash_refresh_token(raw_refresh_token)
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()
        if stored_token:
            stored_token.is_revoked = True
            await db.flush()

    async def _store_refresh_token(
        self, db: AsyncSession, user_id: uuid.UUID, token: str, expires_at: datetime
    ) -> None:
        refresh_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_hash=hash_refresh_token(token),
            expires_at=expires_at,
        )
        db.add(refresh_token)
        await db.flush()

    async def get_current_user(self, db: AsyncSession, user_id: uuid.UUID) -> User:
        user = await user_repository.get_with_role(db, user_id)
        if user is None or not user.is_active:
            raise UserNotFoundException()
        return user


auth_service = AuthService()
