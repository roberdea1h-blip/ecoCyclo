from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    async def get_by_user(self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Notification]:
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_unread_by_user(self, db: AsyncSession, user_id: UUID) -> list[Notification]:
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())

    async def mark_as_read(self, db: AsyncSession, notification_id: UUID) -> None:
        await db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(is_read=True)
        )
        await db.flush()

    async def mark_all_as_read(self, db: AsyncSession, user_id: UUID) -> None:
        await db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        await db.flush()

    async def count_unread(self, db: AsyncSession, user_id: UUID) -> int:
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        return len(result.scalars().all())


notification_repository = NotificationRepository(Notification)
