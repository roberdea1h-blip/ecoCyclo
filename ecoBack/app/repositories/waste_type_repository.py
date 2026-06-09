from app.models.waste_type import WasteType
from app.repositories.base_repository import BaseRepository


class WasteTypeRepository(BaseRepository[WasteType]):
    pass


waste_type_repository = WasteTypeRepository(WasteType)
