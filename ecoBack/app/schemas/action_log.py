from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    action: str
    entity_type: str | None
    entity_id: str | None
    description: str | None
    extra_data: dict | None
    ip_address: str | None
    created_at: datetime
