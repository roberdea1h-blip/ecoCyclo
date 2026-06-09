import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reward import Reward
from app.repositories.reward_repository import reward_repository
from app.schemas.reward import RewardCreate
from app.utils.exceptions import (
    InsufficientPointsException,
    RewardNotFoundException,
    RewardOutOfStockException,
)


class RewardService:
    async def create_reward(self, db: AsyncSession, data: RewardCreate) -> Reward:
        reward = await reward_repository.create(
            db,
            name=data.name,
            description=data.description,
            points_cost=data.points_cost,
            stock=data.stock,
            image_url=data.image_url,
        )
        return reward

    async def get_reward(self, db: AsyncSession, reward_id: UUID) -> Reward:
        reward = await reward_repository.get(db, reward_id)
        if reward is None:
            raise RewardNotFoundException()
        return reward

    async def get_active_rewards(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Reward]:
        return await reward_repository.get_active(db, skip=skip, limit=limit)

    async def update_image(self, db: AsyncSession, reward_id: UUID, image_url: str) -> Reward:
        reward = await reward_repository.get(db, reward_id)
        if reward is None:
            raise RewardNotFoundException()
        reward = await reward_repository.update(db, reward, image_url=image_url)
        return reward

    async def redeem_reward(self, db: AsyncSession, user_id: UUID, reward_id: UUID) -> bool:
        """Placeholder for reward redemption logic."""
        reward = await reward_repository.get(db, reward_id)
        if reward is None:
            raise RewardNotFoundException()

        if reward.stock is not None and reward.stock <= 0:
            raise RewardOutOfStockException()

        from app.repositories.user_repository import user_repository

        user = await user_repository.get(db, user_id)
        if user is None or user.points < reward.points_cost:
            raise InsufficientPointsException()

        return True


reward_service = RewardService()
