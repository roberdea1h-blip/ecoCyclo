import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role: Mapped["Role"] = relationship("Role", back_populates="users")  # noqa: F821

    @property
    def role_name(self) -> str | None:
        return self.role.name if self.role else None
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="user", foreign_keys="Report.user_id")  # noqa: F821
    cleanup_records: Mapped[list["CleanupRecord"]] = relationship("CleanupRecord", back_populates="user")  # noqa: F821
    redemptions: Mapped[list["Redemption"]] = relationship("Redemption", back_populates="user")  # noqa: F821
    point_transactions: Mapped[list["PointTransaction"]] = relationship("PointTransaction", back_populates="user")  # noqa: F821
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")  # noqa: F821
    action_logs: Mapped[list["ActionLog"]] = relationship("ActionLog", back_populates="user")  # noqa: F821
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")  # noqa: F821
