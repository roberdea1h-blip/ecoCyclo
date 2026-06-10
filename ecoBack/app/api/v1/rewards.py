from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import IdResponse
from app.schemas.reward import RedeemRequest, RedemptionResponse, RewardResponse
from app.services.reward_service import reward_service

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "rewards"}


@router.get("/", response_model=list[RewardResponse])
async def list_rewards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    rewards = await reward_service.get_active_rewards(db, skip=skip, limit=limit)
    return rewards


@router.get("/{reward_id}", response_model=RewardResponse)
async def get_reward(
    reward_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    reward = await reward_service.get_reward(db, reward_id)
    return reward


@router.post("/{reward_id}/redeem", response_model=RedemptionResponse, status_code=status.HTTP_201_CREATED)
async def redeem_reward(
    reward_id: UUID,
    body: RedeemRequest | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    redemption = await reward_service.redeem_reward(
        db, current_user.id, reward_id,
        delivery_type=body.delivery_type if body else None,
        delivery_info=body.delivery_info if body else None,
    )
    return redemption
