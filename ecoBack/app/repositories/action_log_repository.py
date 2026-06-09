from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.action_log import ActionLog
from app.repositories.base_repository import BaseRepository


class ActionLogRepository(BaseRepository[ActionLog]):
    async def get_by_user(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[ActionLog]:
        result = await db.execute(
            select(ActionLog)
            .where(ActionLog.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(ActionLog.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_action(
        self, db: AsyncSession, action: str, skip: int = 0, limit: int = 100
    ) -> list[ActionLog]:
        result = await db.execute(
            select(ActionLog)
            .where(ActionLog.action == action)
            .offset(skip)
            .limit(limit)
            .order_by(ActionLog.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_entity(
        self, db: AsyncSession, entity_type: str, entity_id: str, skip: int = 0, limit: int = 100
    ) -> list[ActionLog]:
        result = await db.execute(
            select(ActionLog)
            .where(ActionLog.entity_type == entity_type, ActionLog.entity_id == entity_id)
            .offset(skip)
            .limit(limit)
            .order_by(ActionLog.created_at.desc())
        )
        return list(result.scalars().all())


action_log_repository = ActionLogRepository(ActionLog)
