from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportStatus
from app.repositories.report_repository import report_repository
from app.schemas.report import ReportCreate, ReportUpdate
from app.utils.exceptions import ForbiddenException, ReportNotFoundException


class ReportService:
    async def create_report(self, db: AsyncSession, user_id: UUID, data: ReportCreate) -> Report:
        report = await report_repository.create(
            db,
            user_id=user_id,
            waste_type_id=data.waste_type_id,
            title=data.title,
            description=data.description,
            latitude=data.latitude,
            longitude=data.longitude,
            address=data.address,
        )
        return report

    async def get_report(self, db: AsyncSession, report_id: UUID) -> Report:
        report = await report_repository.get_with_images(db, report_id)
        if report is None:
            raise ReportNotFoundException()
        return report

    async def get_user_reports(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Report]:
        return await report_repository.get_by_user(db, user_id, skip=skip, limit=limit)

    async def get_all_reports(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Report]:
        return await report_repository.get_multi(db, skip=skip, limit=limit)

    async def update_report(
        self, db: AsyncSession, report_id: UUID, user_id: UUID, data: ReportUpdate
    ) -> Report:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException()
        if report.user_id != user_id:
            raise ForbiddenException()

        update_kwargs = data.model_dump(exclude_unset=True)
        if update_kwargs:
            report = await report_repository.update(db, report, **update_kwargs)

        return report

    async def delete_report(self, db: AsyncSession, report_id: UUID, user_id: UUID) -> None:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException()
        if report.user_id != user_id:
            raise ForbiddenException()
        await report_repository.delete(db, report_id)

    async def count_by_status(self, db: AsyncSession, status: ReportStatus) -> int:
        return await report_repository.count_by_status(db, status)


report_service = ReportService()
