from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.point_transaction import PointTransaction
from app.repositories.base_repository import BaseRepository


class PointTransactionRepository(BaseRepository[PointTransaction]):
    async def get_by_user(
        self, db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[PointTransaction]:
        result = await db.execute(
            select(PointTransaction)
            .where(PointTransaction.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(PointTransaction.created_at.desc())
        )
        return list(result.scalars().all())


point_transaction_repository = PointTransactionRepository(PointTransaction)
