from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportStatus
from app.repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository[Report]):
    async def get_by_user(self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Report]:
        result = await db.execute(
            select(Report)
            .where(Report.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_status(self, db: AsyncSession, status: ReportStatus, skip: int = 0, limit: int = 100) -> list[Report]:
        result = await db.execute(
            select(Report)
            .where(Report.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_images(self, db: AsyncSession, id: UUID) -> Report | None:
        result = await db.execute(
            select(Report)
            .where(Report.id == id)
            .options(selectinload(Report.images))
        )
        return result.scalar_one_or_none()

    async def count_by_status(self, db: AsyncSession, status: ReportStatus) -> int:
        result = await db.execute(
            select(Report).where(Report.status == status)
        )
        return len(result.scalars().all())


report_repository = ReportRepository(Report)
