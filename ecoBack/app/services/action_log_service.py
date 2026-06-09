import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_log import ActionLog
from app.repositories.action_log_repository import action_log_repository


class ActionLogService:
    async def log(
        self,
        db: AsyncSession,
        user_id: UUID | None,
        action: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        description: str | None = None,
        extra_data: dict | None = None,
        ip_address: str | None = None,
    ) -> ActionLog:
        log_entry = await action_log_repository.create(
            db,
            id=uuid.uuid4(),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            extra_data=extra_data,
            ip_address=ip_address,
        )
        return log_entry

    async def get_by_user(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[ActionLog]:
        return await action_log_repository.get_by_user(db, user_id, skip=skip, limit=limit)

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ActionLog]:
        return await action_log_repository.get_multi(db, skip=skip, limit=limit)


action_log_service = ActionLogService()
