from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.mappers.user_mapper import to_user_response
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.report import ReportResponse
from app.schemas.reward import RedemptionResponse, RewardCreate, RewardResponse, RewardUpdate, UpdateRedemptionStatusRequest
from app.schemas.user import UserResponse
from app.schemas.waste_type import WasteTypeCreate, WasteTypeResponse, WasteTypeUpdate
from app.services.report_service import report_service
from app.services.reward_service import reward_service
from app.services.user_service import user_service
from app.services.waste_type_service import waste_type_service
from app.storage import get_image_storage, ImageStorage

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "admin"}


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    from app.repositories.user_repository import user_repository
    users = await user_repository.get_multi(db, skip=skip, limit=limit)
    return [to_user_response(u) for u in users]


@router.get("/reports", response_model=list[ReportResponse])
async def list_all_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    reports = await report_service.get_all_reports(db, skip=skip, limit=limit)
    return reports


@router.post("/rewards", response_model=RewardResponse, status_code=status.HTTP_201_CREATED)
async def create_reward(
    data: RewardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    reward = await reward_service.create_reward(db, data)
    return reward


@router.patch("/rewards/{reward_id}", response_model=RewardResponse)
async def update_reward(
    reward_id: UUID,
    data: RewardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return await reward_service.update_reward(db, reward_id, data)


@router.delete("/rewards/{reward_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reward(
    reward_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    await reward_service.delete_reward(db, reward_id)


@router.post("/rewards/{reward_id}/image", response_model=RewardResponse)
async def upload_reward_image(
    reward_id: UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    storage: ImageStorage = Depends(get_image_storage),
):
    image_url = await storage.save(file, subfolder="rewards")
    reward = await reward_service.update_image(db, reward_id, image_url)
    return reward


@router.post("/setup", response_model=MessageResponse)
async def setup_database(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    from app.db.init_db import init_db
    await init_db(db)
    return MessageResponse(message="Database initialized successfully")


@router.get("/waste-types", response_model=list[WasteTypeResponse])
async def list_waste_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return await waste_type_service.get_all(db)


@router.post("/waste-types", response_model=WasteTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_waste_type(
    data: WasteTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return await waste_type_service.create(db, data)


@router.patch("/waste-types/{waste_type_id}", response_model=WasteTypeResponse)
async def update_waste_type(
    waste_type_id: UUID,
    data: WasteTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return await waste_type_service.update(db, waste_type_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    await user_service.delete_user(db, user_id, current_user.id)


@router.delete("/waste-types/{waste_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_waste_type(
    waste_type_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    await waste_type_service.delete(db, waste_type_id)


@router.get("/redemptions", response_model=list[RedemptionResponse])
async def list_redemptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return await reward_service.get_redemptions(db, skip=skip, limit=limit)


@router.patch("/redemptions/{redemption_id}/status", response_model=RedemptionResponse)
async def update_redemption_status(
    redemption_id: UUID,
    body: UpdateRedemptionStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return await reward_service.update_redemption_status(
        db, redemption_id, body.status, delivery_info=body.delivery_info,
    )
