import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CleanupRecord(Base):
    __tablename__ = "cleanup_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cleaned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    collected_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped["Report"] = relationship("Report", back_populates="cleanup_records")  # noqa: F821
    user: Mapped["User"] = relationship("User", back_populates="cleanup_records")  # noqa: F821
