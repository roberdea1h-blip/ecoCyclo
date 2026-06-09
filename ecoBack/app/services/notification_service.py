import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.notification_repository import notification_repository
from app.schemas.notification import NotificationCreate


class NotificationService:
    async def create_notification(
        self, db: AsyncSession, user_id: UUID, data: NotificationCreate
    ) -> Notification:
        notification = await notification_repository.create(
            db,
            id=uuid.uuid4(),
            user_id=user_id,
            title=data.title,
            message=data.message,
            type=data.type,
        )
        return notification

    async def get_user_notifications(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Notification]:
        return await notification_repository.get_by_user(db, user_id, skip=skip, limit=limit)

    async def get_unread(self, db: AsyncSession, user_id: UUID) -> list[Notification]:
        return await notification_repository.get_unread_by_user(db, user_id)

    async def mark_as_read(self, db: AsyncSession, notification_id: UUID) -> None:
        await notification_repository.mark_as_read(db, notification_id)

    async def mark_all_as_read(self, db: AsyncSession, user_id: UUID) -> None:
        await notification_repository.mark_all_as_read(db, user_id)

    async def count_unread(self, db: AsyncSession, user_id: UUID) -> int:
        return await notification_repository.count_unread(db, user_id)


notification_service = NotificationService()
