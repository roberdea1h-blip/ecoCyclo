from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reward import Reward
from app.repositories.base_repository import BaseRepository


class RewardRepository(BaseRepository[Reward]):
    async def get_active(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Reward]:
        result = await db.execute(
            select(Reward)
            .where(Reward.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .order_by(Reward.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_redemptions(self, db: AsyncSession, id: int) -> Reward | None:
        result = await db.execute(
            select(Reward)
            .where(Reward.id == id)
            .options(selectinload(Reward.redemptions))
        )
        return result.scalar_one_or_none()


reward_repository = RewardRepository(Reward)
