from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WasteTypeCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = Field(None, max_length=500)
    icon: str | None = Field(None, max_length=50)
    points_per_report: int = 10


class WasteTypeUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    icon: str | None = None
    points_per_report: int | None = None


class WasteTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    icon: str | None
    points_per_report: int
    created_at: datetime
    updated_at: datetime
