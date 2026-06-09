from uuid import UUID

from fastapi import APIRouter, Depends, Path, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import user_service
from app.storage import get_image_storage, ImageStorage

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "users"}


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await user_service.update_profile(
        db,
        current_user.id,
        full_name=data.full_name,
        avatar_url=data.avatar_url,
    )
    return user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: ImageStorage = Depends(get_image_storage),
):
    avatar_url = await storage.save(file, subfolder="avatars")
    user = await user_service.update_profile(
        db, current_user.id, avatar_url=avatar_url,
    )
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await user_service.get_by_id(db, user_id)
    return user
