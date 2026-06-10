import uuid
from uuid import UUID

from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.point_transaction import PointTransaction, PointTransactionType
from app.models.redemption import Redemption, RedemptionStatus
from app.models.reward import Reward
from app.repositories.redemption_repository import redemption_repository
from app.repositories.reward_repository import reward_repository
from app.repositories.user_repository import user_repository
from app.schemas.reward import RewardCreate, RewardUpdate
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

    async def update_reward(self, db: AsyncSession, reward_id: UUID, data: RewardUpdate) -> Reward:
        reward = await reward_repository.get(db, reward_id)
        if reward is None:
            raise RewardNotFoundException()
        update_kwargs = data.model_dump(exclude_unset=True)
        if update_kwargs:
            reward = await reward_repository.update(db, reward, **update_kwargs)
        return reward

    async def delete_reward(self, db: AsyncSession, reward_id: UUID) -> None:
        deleted = await reward_repository.delete(db, reward_id)
        if not deleted:
            raise RewardNotFoundException()

    async def update_image(self, db: AsyncSession, reward_id: UUID, image_url: str) -> Reward:
        reward = await reward_repository.get(db, reward_id)
        if reward is None:
            raise RewardNotFoundException()
        reward = await reward_repository.update(db, reward, image_url=image_url)
        return reward

    async def redeem_reward(
        self, db: AsyncSession, user_id: UUID, reward_id: UUID,
        delivery_type: str | None = None, delivery_info: str | None = None,
    ) -> Redemption:
        reward = await reward_repository.get(db, reward_id)
        if reward is None:
            raise RewardNotFoundException()

        if reward.stock is not None and reward.stock <= 0:
            raise RewardOutOfStockException()

        user = await user_repository.get(db, user_id)
        if user is None or user.points < reward.points_cost:
            raise InsufficientPointsException()

        decrement = (
            sql_update(Reward)
            .where(Reward.id == reward_id)
            .where(Reward.stock > 0)
            .values(stock=Reward.stock - 1)
        )
        await db.execute(decrement)

        user.points -= reward.points_cost

        redemption = await redemption_repository.create(
            db,
            user_id=user_id,
            reward_id=reward_id,
            points_spent=reward.points_cost,
            status=RedemptionStatus.pending,
            delivery_type=delivery_type,
            delivery_info=delivery_info,
        )

        pt = PointTransaction(
            user_id=user_id,
            points=-reward.points_cost,
            type=PointTransactionType.redeemed,
            description=f"Canje: {reward.name}",
            reference_id=str(redemption.id),
        )
        db.add(pt)
        await db.flush()

        return redemption

    async def get_redemptions(
        self, db: AsyncSession, skip: int = 0, limit: int = 100,
    ) -> list[Redemption]:
        return await redemption_repository.get_multi(db, skip=skip, limit=limit)

    async def update_redemption_status(
        self, db: AsyncSession, redemption_id: UUID,
        status: RedemptionStatus, delivery_info: str | None = None,
    ) -> Redemption:
        redemption = await redemption_repository.get(db, redemption_id)
        if redemption is None:
            from app.utils.exceptions import RedemptionNotFoundException
            raise RedemptionNotFoundException()

        update_kwargs = {"status": status}
        if delivery_info is not None:
            update_kwargs["delivery_info"] = delivery_info

        return await redemption_repository.update(db, redemption, **update_kwargs)


reward_service = RewardService()
