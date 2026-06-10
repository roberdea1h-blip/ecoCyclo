from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.notification import NotificationResponse
from app.services.notification_service import notification_service

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "notifications"}


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notifications = await notification_service.get_user_notifications(
        db, current_user.id, skip=skip, limit=limit
    )
    return notifications


@router.get("/unread", response_model=list[NotificationResponse])
async def get_unread(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notifications = await notification_service.get_unread(db, current_user.id)
    return notifications


@router.patch("/{notification_id}/read", response_model=MessageResponse)
async def mark_as_read(
    notification_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await notification_service.mark_as_read(db, notification_id, user_id=current_user.id)
    return MessageResponse(message="Notification marked as read")


@router.patch("/read-all", response_model=MessageResponse)
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await notification_service.mark_all_as_read(db, current_user.id)
    return MessageResponse(message="All notifications marked as read")


@router.get("/unread/count")
async def count_unread(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await notification_service.count_unread(db, current_user.id)
    return {"count": count}
