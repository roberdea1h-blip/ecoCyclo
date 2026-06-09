from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WasteTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    icon: str | None
    points_per_report: int
    created_at: datetime
    updated_at: datetime
