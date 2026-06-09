from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.waste_type import WasteTypeResponse
from app.services.waste_type_service import waste_type_service

router = APIRouter()


@router.get("/", response_model=list[WasteTypeResponse])
async def list_waste_types(db: AsyncSession = Depends(get_db)):
    return await waste_type_service.get_all(db)
