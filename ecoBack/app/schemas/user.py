from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., max_length=255)


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=255)
    avatar_url: str | None = Field(None, max_length=500)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    username: str
    full_name: str
    is_active: bool
    is_verified: bool
    role_id: UUID
    role_name: str | None = None
    avatar_url: str | None
    points: int
    created_at: datetime
    updated_at: datetime
