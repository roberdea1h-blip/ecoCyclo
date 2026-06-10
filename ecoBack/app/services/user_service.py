from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import user_repository
from app.users.exceptions import CannotDeleteSelfException, UserNotFoundException


class UserService:
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> User:
        user = await user_repository.get_with_role(db, user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return user

    async def get_profile(self, db: AsyncSession, user_id: UUID) -> User:
        return await self.get_by_id(db, user_id)

    async def update_profile(
        self, db: AsyncSession, user_id: UUID, full_name: str | None = None, avatar_url: str | None = None
    ) -> User:
        user = await user_repository.get_with_role(db, user_id)
        if user is None:
            raise UserNotFoundException(user_id)

        update_kwargs = {}
        if full_name is not None:
            update_kwargs["full_name"] = full_name
        if avatar_url is not None:
            update_kwargs["avatar_url"] = avatar_url

        if update_kwargs:
            user = await user_repository.update(db, user, **update_kwargs)

        return user

    async def delete_user(self, db: AsyncSession, user_id: UUID, current_user_id: UUID) -> None:
        if user_id == current_user_id:
            raise CannotDeleteSelfException()

        user = await user_repository.get_with_role(db, user_id)
        if user is None:
            raise UserNotFoundException(user_id)

        await user_repository.delete(db, user_id)
        await db.flush()


user_service = UserService()
