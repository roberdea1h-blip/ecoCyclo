from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reward import Reward
from app.repositories.base_repository import BaseRepository


class RewardRepository(BaseRepository[Reward]):
    async def get_active(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Reward]:
        stmt = (
            select(Reward)
            .where(Reward.is_active.is_(True))
            .order_by(Reward.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_with_redemptions(self, db: AsyncSession, reward_id: int) -> Reward | None:
        stmt = (
            select(Reward)
            .where(Reward.id == reward_id)
            .options(selectinload(Reward.redemptions))
        )
        result = await db.execute(stmt)
        return result.scalars().first()


reward_repository = RewardRepository(Reward)
