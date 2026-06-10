import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RedemptionStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    activated = "activated"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Redemption(Base):
    __tablename__ = "redemptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reward_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rewards.id"), nullable=False)
    points_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RedemptionStatus] = mapped_column(SAEnum(RedemptionStatus), default=RedemptionStatus.pending)
    delivery_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    delivery_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    redeemed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="redemptions")  # noqa: F821
    reward: Mapped["Reward"] = relationship("Reward", back_populates="redemptions")  # noqa: F821
