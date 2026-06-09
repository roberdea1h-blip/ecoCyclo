from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.report import ReportStatus
from app.models.user import User
from app.schemas.report import ReportCreate, ReportImageResponse, ReportResponse, ReportUpdate
from app.services.report_service import report_service
from app.storage import get_image_storage, ImageStorage

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/health", summary="Verificar salud del servicio")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "reports"}


@router.post(
    "/", 
    response_model=ReportResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo reporte",
    description="Registra un reporte de residuos vinculándolo al usuario autenticado."
)
async def create_report(
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    report = await report_service.create_report(db, current_user.id, data)
    return ReportResponse.model_validate(report)


@router.get(
    "/", 
    response_model=list[ReportResponse],
    summary="Listar reportes filtrados",
    description="Obtiene una lista de reportes permitiendo filtrar por estado, tipo de residuo, rango de fechas y coordenadas geográficas con radio."
)
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
) -> list[ReportResponse]:
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
    return [ReportResponse.model_validate(r) for r in reports]


@router.get(
    "/mine", 
    response_model=list[ReportResponse],
    summary="Listar mis reportes",
    description="Obtiene exclusivamente los reportes creados por el usuario autenticado actualmente."
)
async def my_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ReportResponse]:
    reports = await report_service.get_user_reports(db, current_user.id, skip=skip, limit=limit)
    return [ReportResponse.model_validate(r) for r in reports]


@router.post(
    "/{report_id}/images", 
    response_model=ReportImageResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen para un reporte",
    description="Sube un archivo de imagen al almacenamiento y lo asocia al reporte especificado (puede marcarse como foto de 'antes' o 'después')."
)
async def upload_report_image(
    report_id: UUID,
    file: UploadFile,
    is_before: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: ImageStorage = Depends(get_image_storage),
) -> ReportImageResponse:
    image_url = await storage.save(file, subfolder="reports")
    image = await report_service.add_image(db, report_id, image_url, is_before=is_before)
    return ReportImageResponse.model_validate(image)


@router.get(
    "/{report_id}", 
    response_model=ReportResponse,
    summary="Obtener un reporte por ID",
    description="Recupera toda la información detallada de un único reporte mediante su identificador único."
)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    report = await report_service.get_report(db, report_id)
    return ReportResponse.model_validate(report)


@router.patch(
    "/{report_id}", 
    response_model=ReportResponse,
    summary="Actualizar parcialmente un reporte",
    description="Modifica los campos permitidos de un reporte existente. Requiere validación de autoría en el servicio."
)
async def update_report(
    report_id: UUID,
    data: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    report = await report_service.update_report(db, report_id, current_user.id, data)
    return ReportResponse.model_validate(report)


@router.delete(
    "/{report_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un reporte",
    description="Remueve de forma definitiva un reporte del sistema si el usuario actual tiene los permisos correspondientes."
)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await report_service.delete_report(db, report_id, current_user.id)
