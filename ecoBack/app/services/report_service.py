import math
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportStatus
from app.models.report_image import ReportImage
from app.repositories.report_image_repository import report_image_repository
from app.repositories.report_repository import report_repository
from app.schemas.report import ReportCreate, ReportUpdate
from app.utils.exceptions import ForbiddenException, ReportNotFoundException


def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class ReportService:
     async def create_report(
        self, db: AsyncSession, user_id: UUID, data: ReportCreate
    ) -> Report:
        report_data = data.model_dump()
        report_data["user_id"] = user_id

        
        return await report_repository.create(db, **report_data) # Desempaquetamos el diccionario directamente en el repositorio

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

    async def get_filtered_reports(
        self,
        db: AsyncSession,
        status: ReportStatus | None = None,
        waste_type_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        lat: float | None = None,
        lng: float | None = None,
        radius_km: float | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Report]:
        reports = await report_repository.get_filtered(
            db,
            status=status,
            waste_type_id=waste_type_id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )

        if lat is not None and lng is not None and radius_km is not None:
            reports = [r for r in reports if _haversine_distance(lat, lng, r.latitude, r.longitude) <= radius_km]

        return reports

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

    async def add_image(
        self, db: AsyncSession, report_id: UUID, image_url: str, is_before: bool = True
    ) -> ReportImage:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException()
        image = await report_image_repository.create(
            db, report_id=report_id, image_url=image_url, is_before=is_before,
        )
        return image


report_service = ReportService()
