import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, update
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
        if await user_repository.get_by_email(db, request.email):
            raise EmailAlreadyRegistered()

        if await user_repository.get_by_username(db, request.username):
            raise UsernameAlreadyRegistered()

        user_role = await user_repository.get_user_role(db)
        if not user_role:
            raise ValueError("Default user role not found. Run init_db first.")

        return await user_repository.create(
            db,
            id=uuid.uuid4(),
            email=request.email,
            username=request.username,
            hashed_password=hash_password(request.password),
            full_name=request.full_name,
            role_id=user_role.id,
        )

    async def login(self, db: AsyncSession, email: str, password: str) -> tuple[str, str, User]:
        user = await user_repository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise CredentialsException()

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_str = create_refresh_token(data={"sub": str(user.id)})

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self._store_refresh_token(db, user.id, refresh_token_str, expires_at)

        return access_token, refresh_token_str, user

    async def refresh(self, db: AsyncSession, raw_refresh_token: str) -> tuple[str, str]:
        payload = decode_token(raw_refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidToken()

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidToken()

        # Primero revocamos el token viejo de forma eficiente
        token_hash = hash_refresh_token(raw_refresh_token)
        was_revoked = await self._revoke_token_by_hash(db, token_hash)
        if not was_revoked:
            raise InvalidToken()

        new_access = create_access_token(data={"sub": user_id})
        new_refresh = create_refresh_token(data={"sub": user_id})

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self._store_refresh_token(db, uuid.UUID(user_id), new_refresh, expires_at)

        return new_access, new_refresh

    async def logout(self, db: AsyncSession, raw_refresh_token: str | None) -> None:
        if not raw_refresh_token:
            return
        token_hash = hash_refresh_token(raw_refresh_token)
        await self._revoke_token_by_hash(db, token_hash)

    async def _revoke_token_by_hash(self, db: AsyncSession, token_hash: str) -> bool:
        """Revoca un token activo. Retorna True si el token existía y fue modificado."""
        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash, RefreshToken.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        await db.flush()
        return result.rowcount > 0

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
        if not user or not user.is_active:
            raise UserNotFoundException()
        return user


auth_service = AuthService()
