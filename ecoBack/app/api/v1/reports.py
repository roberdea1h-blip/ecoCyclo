from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.report import ReportStatus
from app.models.user import User
from app.schemas.report import CompleteReportRequest, RejectReportRequest, ReportCreate, ReportImageResponse, ReportResponse, ReportUpdate
from app.services.report_service import report_service
from app.storage import get_image_storage, ImageStorage

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "reports"}


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.create_report(db, current_user.id, data)
    return report


@router.get("/", response_model=list[ReportResponse])
async def list_reports(
    status: ReportStatus | None = Query(None),
    waste_type_id: UUID | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    lat: float | None = Query(None, ge=-90, le=90),
    lng: float | None = Query(None, ge=-180, le=180),
    radius_km: float | None = Query(None, ge=0.1, le=1000),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = await report_service.get_filtered_reports(
        db,
        status=status,
        waste_type_id=waste_type_id,
        date_from=date_from,
        date_to=date_to,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        skip=skip,
        limit=limit,
    )
    return reports


@router.get("/mine", response_model=list[ReportResponse])
async def my_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = await report_service.get_user_reports(db, current_user.id, skip=skip, limit=limit)
    return reports


@router.get("/claimed", response_model=list[ReportResponse])
async def claimed_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = await report_service.get_claimed_reports(db, current_user.id, skip=skip, limit=limit)
    return reports


@router.post("/{report_id}/images", response_model=ReportImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_report_image(
    report_id: UUID,
    file: UploadFile,
    is_before: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: ImageStorage = Depends(get_image_storage),
):
    image_url = await storage.save(file, subfolder="reports")
    image = await report_service.add_image(db, report_id, image_url, is_before=is_before)
    return image


@router.post("/{report_id}/claim", response_model=ReportResponse)
async def claim_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.claim_report(db, report_id, current_user.id)
    return report


@router.post("/{report_id}/unclaim", response_model=ReportResponse)
async def unclaim_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.unclaim_report(db, report_id, current_user.id)
    return report


@router.post("/{report_id}/complete", response_model=ReportResponse)
async def complete_report(
    report_id: UUID,
    body: CompleteReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.complete_report(
        db, report_id, current_user.id,
        collected_weight=body.collected_weight,
        notes=body.notes,
    )
    return report


@router.post("/{report_id}/verify", response_model=ReportResponse)
async def verify_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.verify_report(db, report_id, current_user)
    return report


@router.post("/{report_id}/reject", response_model=ReportResponse)
async def reject_report(
    report_id: UUID,
    body: RejectReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.reject_report(db, report_id, current_user, reason=body.reason)
    return report


@router.get("/pending-review", response_model=list[ReportResponse])
async def pending_review_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = await report_service.get_filtered_reports(
        db, status=ReportStatus.pending_review, skip=skip, limit=limit,
    )
    return [r for r in reports if r.user_id == current_user.id]


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.get_report(db, report_id)
    return report


@router.patch("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    data: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = await report_service.update_report(db, report_id, current_user, data)
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await report_service.delete_report(db, report_id, current_user)
