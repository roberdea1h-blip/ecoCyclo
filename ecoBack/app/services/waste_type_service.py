from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.waste_type import WasteType
from app.repositories.waste_type_repository import waste_type_repository
from app.waste_type.exceptions import WasteTypeNotFoundException


class WasteTypeService:
    async def get_all(self, db: AsyncSession) -> list[WasteType]:
        return await waste_type_repository.get_multi(db, skip=0, limit=100)

    async def get_by_id(self, db: AsyncSession, waste_type_id) -> WasteType:
        waste_type = await waste_type_repository.get(db, waste_type_id)
        if waste_type is None:
            raise WasteTypeNotFoundException()
        return waste_type

    async def create(self, db: AsyncSession, data) -> WasteType:
        return await waste_type_repository.create(
            db,
            name=data.name,
            description=data.description,
            icon=data.icon,
            points_per_report=data.points_per_report,
        )

    async def update(self, db: AsyncSession, waste_type_id: UUID, data) -> WasteType:
        waste_type = await waste_type_repository.get(db, waste_type_id)
        if waste_type is None:
            raise WasteTypeNotFoundException()
        update_kwargs = data.model_dump(exclude_unset=True)
        if update_kwargs:
            waste_type = await waste_type_repository.update(db, waste_type, **update_kwargs)
        return waste_type

    async def delete(self, db: AsyncSession, waste_type_id: UUID) -> None:
        deleted = await waste_type_repository.delete(db, waste_type_id)
        if not deleted:
            raise WasteTypeNotFoundException()


waste_type_service = WasteTypeService()
