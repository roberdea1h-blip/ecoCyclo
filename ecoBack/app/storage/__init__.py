from fastapi import Depends

from app.core.config import get_settings, Settings
from app.storage.base import ImageStorage
from app.storage.local import LocalImageStorage


def get_image_storage(settings: Settings = Depends(get_settings)) -> ImageStorage:
    return LocalImageStorage(settings.UPLOAD_DIR)


__all__ = ["ImageStorage", "get_image_storage"]
