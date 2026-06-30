from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class MessageResponse(BaseModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str
    is_active: bool
    role_id: UUID
    points: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str
    is_active: bool
    is_verified: bool
    role_id: UUID
    avatar_url: str | None = None
    points: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WasteTypeResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    icon: str | None = None
    points_per_report: int
    points_per_kilo: int

    model_config = {"from_attributes": True}


class ReportCreate(BaseModel):
    waste_type_id: UUID
    title: str
    description: str | None = None
    latitude: float
    longitude: float
    address: str | None = None
    estimated_quantity: float | None = None


class ReportResponse(BaseModel):
    id: UUID
    user_id: UUID
    waste_type_id: UUID
    title: str
    description: str | None = None
    latitude: float
    longitude: float
    address: str | None = None
    status: str
    cleaner_id: UUID | None = None
    cleaned_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RewardResponse(BaseModel):
    id: UUID
    name: str
    description: str
    points_cost: int
    stock: int | None = None
    image_url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class RedeemRequest(BaseModel):
    reward_id: UUID


class RedeemResponse(BaseModel):
    message: str
    points_spent: int
    remaining_points: int


class NotificationResponse(BaseModel):
    id: UUID
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RedemptionResponse(BaseModel):
    id: UUID
    reward_id: UUID
    reward_name: str
    points_spent: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
