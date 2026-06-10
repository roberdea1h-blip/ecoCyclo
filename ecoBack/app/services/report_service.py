import math
from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report, ReportStatus
from app.models.report_image import ReportImage
from app.report.exceptions import (
    CannotClaimOwnReportException,
    NotAssignedCleanerException,
    NotOriginalReporterException,
    ReportNotFoundException,
    ReportNotInProgressException,
    ReportNotPendingException,
    ReportNotPendingReviewException,
)
from app.repositories.point_transaction_repository import point_transaction_repository
from app.repositories.report_image_repository import report_image_repository
from app.repositories.report_repository import report_repository
from app.repositories.user_repository import user_repository
from app.repositories.waste_type_repository import waste_type_repository
from app.schemas.notification import NotificationCreate
from app.schemas.report import ReportCreate, ReportUpdate
from app.services.action_log_service import action_log_service
from app.services.notification_service import notification_service
from app.models.user import User


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
            estimated_quantity=data.estimated_quantity,
        )
        report = await self._load_relations(db, report)

        waste_type = await waste_type_repository.get(db, data.waste_type_id)

        admin_role = await user_repository.get_admin_role(db)
        if admin_role:
            admins = await user_repository.get_by_role(db, admin_role.id)
            for admin in admins:
                await notification_service.create_notification(
                    db, admin.id,
                    NotificationCreate(
                        title="Nuevo reporte creado",
                        message=f"Se ha creado un nuevo reporte: {data.title}",
                        type="report_created",
                    ),
                )

        await action_log_service.log(
            db, user_id=user_id, action="report.create",
            entity_type="report", entity_id=str(report.id),
            description=f"Reporte creado: {data.title}",
        )
        return report

    async def get_report(self, db: AsyncSession, report_id: UUID) -> Report:
        report = await report_repository.get_with_images(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        return report

    async def get_user_reports(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Report]:
        return await report_repository.get_by_user(db, user_id, skip=skip, limit=limit)

    async def get_claimed_reports(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Report]:
        return await report_repository.get_by_cleaner(db, user_id, skip=skip, limit=limit)

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
        self, db: AsyncSession, report_id: UUID, current_user: User, data: ReportUpdate
    ) -> Report:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        if report.user_id != current_user.id and current_user.role_name != "admin":
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(message="Not enough permissions")

        update_kwargs = data.model_dump(exclude_unset=True)
        if update_kwargs:
            report = await report_repository.update(db, report, **update_kwargs)
            await action_log_service.log(
                db, user_id=current_user.id, action="report.update",
                entity_type="report", entity_id=str(report_id),
                description=f"Reporte actualizado",
            )

        report = await self._load_relations(db, report)
        return report

    async def delete_report(self, db: AsyncSession, report_id: UUID, current_user: User) -> None:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        if report.user_id != current_user.id and current_user.role_name != "admin":
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(message="Not enough permissions")
        await report_repository.delete(db, report_id)

    async def claim_report(self, db: AsyncSession, report_id: UUID, user_id: UUID) -> Report:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        if report.status != ReportStatus.pending:
            raise ReportNotPendingException()
        if report.user_id == user_id:
            raise CannotClaimOwnReportException()

        report = await report_repository.update(
            db, report, cleaner_id=user_id, status=ReportStatus.in_progress,
        )
        report = await self._load_relations(db, report)

        owner = await user_repository.get(db, report.user_id)
        cleaner = await user_repository.get(db, user_id)
        cleaner_name = cleaner.full_name if cleaner else "Un usuario"

        await notification_service.create_notification(
            db, report.user_id,
            NotificationCreate(
                title="Reporte aceptado",
                message=f"{cleaner_name} ha aceptado tu reporte: {report.title}",
                type="task_claimed",
            ),
        )
        await action_log_service.log(
            db, user_id=user_id, action="report.claim",
            entity_type="report", entity_id=str(report_id),
            description=f"Reporte reclamado: {report.title}",
        )
        return report

    async def unclaim_report(self, db: AsyncSession, report_id: UUID, user_id: UUID) -> Report:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        if report.cleaner_id != user_id and report.user_id != user_id:
            raise NotAssignedCleanerException()
        if report.status != ReportStatus.in_progress:
            raise ReportNotInProgressException()

        report = await report_repository.update(
            db, report, cleaner_id=None, status=ReportStatus.pending,
        )
        report = await self._load_relations(db, report)

        cleaner = await user_repository.get(db, user_id)

        await notification_service.create_notification(
            db, report.user_id,
            NotificationCreate(
                title="Tarea liberada",
                message=f"{cleaner.full_name if cleaner else 'Un voluntario'} ha liberado la tarea: {report.title}. Está disponible para otros voluntarios.",
                type="task_unclaimed",
            ),
        )
        await action_log_service.log(
            db, user_id=user_id, action="report.unclaim",
            entity_type="report", entity_id=str(report_id),
            description=f"Reporte liberado: {report.title}",
        )
        return report

    async def complete_report(
        self, db: AsyncSession, report_id: UUID, user_id: UUID,
        collected_weight: float | None = None, notes: str | None = None,
    ) -> Report:
        report = await report_repository.get_with_images(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        if report.cleaner_id != user_id:
            raise NotAssignedCleanerException()
        if report.status != ReportStatus.in_progress:
            raise ReportNotInProgressException()

        now = datetime.now(timezone.utc)
        report = await report_repository.update(
            db, report, status=ReportStatus.pending_review, cleaned_at=now,
        )

        from app.models.cleanup_record import CleanupRecord
        cleanup = CleanupRecord(
            report_id=report_id, user_id=user_id,
            cleaned_at=now, collected_weight=collected_weight, notes=notes,
        )
        db.add(cleanup)
        await db.flush()

        await notification_service.create_notification(
            db, report.user_id,
            NotificationCreate(
                title="Limpieza pendiente de revisión",
                message=f"El reporte \"{report.title}\" ha sido marcado como limpio. Revisa y confirma la limpieza para liberar los puntos.",
                type="pending_review",
            ),
        )
        if report.cleaner_id:
            await notification_service.create_notification(
                db, report.cleaner_id,
                NotificationCreate(
                    title="Limpieza completada",
                    message=f"Has completado la limpieza de: {report.title}. Esperando confirmación del creador.",
                    type="cleanup_completed",
                ),
            )

        await action_log_service.log(
            db, user_id=user_id, action="report.complete",
            entity_type="report", entity_id=str(report_id),
            description=f"Reporte marcado como limpio (pendiente revisión): {report.title}, peso: {collected_weight}",
        )

        report = await self._load_relations(db, report)
        return report

    async def verify_report(
        self, db: AsyncSession, report_id: UUID, current_user: User,
    ) -> Report:
        report = await report_repository.get_with_images(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        if report.user_id != current_user.id and current_user.role_name != "admin":
            raise NotOriginalReporterException()
        if report.status != ReportStatus.pending_review:
            raise ReportNotPendingReviewException()

        now = datetime.now(timezone.utc)
        report = await report_repository.update(
            db, report, status=ReportStatus.verified,
            validated_at=now, validator_id=current_user.id,
        )

        points = 0
        if report.waste_type and report.waste_type.points_per_report:
            points = report.waste_type.points_per_report

        if points > 0 and report.cleaner_id:
            cleaner = await user_repository.get(db, report.cleaner_id)
            if cleaner:
                cleaner.points += points
                from app.models.point_transaction import PointTransaction, PointTransactionType
                pt = PointTransaction(
                    user_id=report.cleaner_id, points=points, type=PointTransactionType.earned,
                    description=f"Puntos por limpiar reporte: {report.title}",
                    reference_id=str(report_id),
                )
                db.add(pt)
                await db.flush()

        await notification_service.create_notification(
            db, report.user_id,
            NotificationCreate(
                title="Limpieza confirmada",
                message=f"Has confirmado la limpieza de: {report.title}.",
                type="cleanup_verified",
            ),
        )
        if report.cleaner_id:
            await notification_service.create_notification(
                db, report.cleaner_id,
                NotificationCreate(
                    title="Limpieza confirmada",
                    message=f"Tu limpieza de \"{report.title}\" ha sido confirmada. Ganaste {points} puntos.",
                    type="cleanup_verified",
                ),
            )

        await action_log_service.log(
            db, user_id=current_user.id, action="report.verify",
            entity_type="report", entity_id=str(report_id),
            description=f"Reporte verificado: {report.title}, puntos: {points}",
        )

        report = await self._load_relations(db, report)
        return report

    async def reject_report(
        self, db: AsyncSession, report_id: UUID, current_user: User,
        reason: str | None = None,
    ) -> Report:
        report = await report_repository.get_with_images(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        if report.user_id != current_user.id and current_user.role_name != "admin":
            raise NotOriginalReporterException()
        if report.status != ReportStatus.pending_review:
            raise ReportNotPendingReviewException()

        report = await report_repository.update(
            db, report, status=ReportStatus.rejected,
            validated_at=datetime.now(timezone.utc), validator_id=current_user.id,
        )

        await notification_service.create_notification(
            db, report.cleaner_id,
            NotificationCreate(
                title="Limpieza rechazada",
                message=f"La limpieza de \"{report.title}\" ha sido rechazada.{' Motivo: ' + reason if reason else ''}",
                type="cleanup_rejected",
            ),
        )

        await action_log_service.log(
            db, user_id=current_user.id, action="report.reject",
            entity_type="report", entity_id=str(report_id),
            description=f"Reporte rechazado: {report.title}, motivo: {reason}",
        )

        report = await self._load_relations(db, report)
        return report

    async def count_by_status(self, db: AsyncSession, status: ReportStatus) -> int:
        return await report_repository.count_by_status(db, status)

    async def add_image(
        self, db: AsyncSession, report_id: UUID, image_url: str, is_before: bool = True
    ) -> ReportImage:
        report = await report_repository.get(db, report_id)
        if report is None:
            raise ReportNotFoundException(report_id)
        image = await report_image_repository.create(
            db, report_id=report_id, image_url=image_url, is_before=is_before,
        )
        return image

    async def _load_relations(self, db: AsyncSession, report: Report) -> Report:
        loaded = await report_repository.get_with_images(db, report.id)
        return loaded or report


report_service = ReportService()
