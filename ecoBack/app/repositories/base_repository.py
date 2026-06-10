from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        result = await db.execute(
            select(self.model).offset(skip).limit(limit).order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        try:
            await db.flush()
        except IntegrityError as e:
            raise ConflictException(message=f"Unique constraint violation: {e.orig}") from e
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: ModelType, **kwargs) -> ModelType:
        for field, value in kwargs.items():
            setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        obj = await self.get(db, id)
        if obj is None:
            return False
        await db.delete(obj)
        await db.flush()
        return True

    async def count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar()
