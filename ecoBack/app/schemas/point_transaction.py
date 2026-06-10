from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.point_transaction import PointTransactionType


class PointTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: PointTransactionType
    points: int
    description: str | None
    reference_id: str | None
    created_at: datetime
