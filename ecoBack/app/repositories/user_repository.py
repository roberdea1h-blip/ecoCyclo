from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role import Role
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_with_role(self, db: AsyncSession, id: UUID) -> User | None:
        result = await db.execute(
            select(User)
            .where(User.id == id)
            .options(selectinload(User.role))
        )
        return result.scalar_one_or_none()

    async def get_admin_role(self, db: AsyncSession) -> Role | None:
        result = await db.execute(select(Role).where(Role.name == "admin"))
        return result.scalar_one_or_none()

    async def get_user_role(self, db: AsyncSession) -> Role | None:
        result = await db.execute(select(Role).where(Role.name == "user"))
        return result.scalar_one_or_none()


user_repository = UserRepository(User)
