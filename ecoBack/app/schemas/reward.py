from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.redemption import RedemptionStatus


class RewardCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    points_cost: int = Field(..., gt=0)
    stock: int | None = Field(None, ge=0)
    image_url: str | None = Field(None, max_length=500)


class RewardUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    points_cost: int | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    image_url: str | None = Field(None, max_length=500)


class RewardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    points_cost: int
    stock: int | None
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RedemptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    reward_id: UUID
    points_spent: int
    status: RedemptionStatus
    delivery_type: str | None = None
    delivery_info: str | None = None
    redeemed_at: datetime


class RedeemRequest(BaseModel):
    delivery_type: Literal["digital", "physical"] | None = None
    delivery_info: str | None = None


class UpdateRedemptionStatusRequest(BaseModel):
    status: RedemptionStatus
    delivery_info: str | None = None
