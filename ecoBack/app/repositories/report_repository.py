from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.report import Report, ReportStatus
from app.repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository[Report]):
    def _with_relations(self, stmt):
        return stmt.options(
            selectinload(Report.waste_type),
            selectinload(Report.user),
            selectinload(Report.cleaner),
            selectinload(Report.images),
        )

    async def get_by_user(self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> list[Report]:
        stmt = self._with_relations(
            select(Report)
            .where(Report.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Report.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, db: AsyncSession, status: ReportStatus, skip: int = 0, limit: int = 100) -> list[Report]:
        stmt = self._with_relations(
            select(Report)
            .where(Report.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Report.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_with_images(self, db: AsyncSession, id: UUID) -> Report | None:
        stmt = self._with_relations(select(Report).where(Report.id == id))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_status(self, db: AsyncSession, status: ReportStatus) -> int:
        result = await db.execute(
            select(Report).where(Report.status == status)
        )
        return len(result.scalars().all())

    async def get_filtered(
        self,
        db: AsyncSession,
        status: ReportStatus | None = None,
        waste_type_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Report]:
        stmt = select(Report)

        if status is not None:
            stmt = stmt.where(Report.status == status)
        if waste_type_id is not None:
            stmt = stmt.where(Report.waste_type_id == waste_type_id)
        if date_from is not None:
            stmt = stmt.where(Report.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(Report.created_at <= date_to)

        stmt = self._with_relations(stmt.order_by(Report.created_at.desc()).offset(skip).limit(limit))

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        db: AsyncSession,
        status: ReportStatus | None = None,
        waste_type_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        stmt = select(Report)

        if status is not None:
            stmt = stmt.where(Report.status == status)
        if waste_type_id is not None:
            stmt = stmt.where(Report.waste_type_id == waste_type_id)
        if date_from is not None:
            stmt = stmt.where(Report.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(Report.created_at <= date_to)

        result = await db.execute(stmt)
        return len(result.scalars().all())


    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Report]:
        stmt = self._with_relations(
            select(Report)
            .offset(skip)
            .limit(limit)
            .order_by(Report.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


report_repository = ReportRepository(Report)
