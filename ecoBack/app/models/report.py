import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReportStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    cleaned = "cleaned"


class Report(Base):
    __tablename__ = "reports"

    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="ck_report_latitude_range"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="ck_report_longitude_range"),
        Index("ix_report_lat_lng", "latitude", "longitude"),
        Index("ix_report_status", "status"),
        Index("ix_report_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    waste_type_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("waste_types.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(SAEnum(ReportStatus), default=ReportStatus.pending)
    cleaned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="reports")  # noqa: F821
    waste_type: Mapped["WasteType"] = relationship("WasteType", back_populates="reports")  # noqa: F821
    images: Mapped[list["ReportImage"]] = relationship("ReportImage", back_populates="report", cascade="all, delete-orphan")  # noqa: F821
    cleanup_records: Mapped[list["CleanupRecord"]] = relationship("CleanupRecord", back_populates="report", cascade="all, delete-orphan")  # noqa: F821
