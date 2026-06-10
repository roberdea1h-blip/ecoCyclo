from app.models.redemption import Redemption
from app.repositories.base_repository import BaseRepository


class RedemptionRepository(BaseRepository[Redemption]):
    pass


redemption_repository = RedemptionRepository(Redemption)
