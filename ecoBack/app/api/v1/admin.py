from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.report import ReportResponse
from app.schemas.reward import RewardCreate, RewardResponse
from app.schemas.user import UserResponse
from app.services.report_service import report_service
from app.services.reward_service import reward_service
from app.services.user_service import user_service

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
    return users


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


@router.post("/setup", response_model=MessageResponse)
async def setup_database(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    from app.db.init_db import init_db
    await init_db(db)
    return MessageResponse(message="Database initialized successfully")
