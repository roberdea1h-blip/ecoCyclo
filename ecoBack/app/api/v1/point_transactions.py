from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.point_transaction_repository import point_transaction_repository
from app.schemas.point_transaction import PointTransactionResponse

router = APIRouter()


@router.get("/me", response_model=list[PointTransactionResponse])
async def my_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = await point_transaction_repository.get_by_user(
        db, current_user.id, skip=skip, limit=limit,
    )
    return transactions
