from sqlalchemy.ext.asyncio import AsyncSession

from app.models.waste_type import WasteType
from app.repositories.waste_type_repository import waste_type_repository


class WasteTypeService:
    async def get_all(self, db: AsyncSession) -> list[WasteType]:
        return await waste_type_repository.get_multi(db, skip=0, limit=100)

    async def get_by_id(self, db: AsyncSession, waste_type_id) -> WasteType | None:
        return await waste_type_repository.get(db, waste_type_id)


waste_type_service = WasteTypeService()
