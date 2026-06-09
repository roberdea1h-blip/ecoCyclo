from abc import ABC, abstractmethod

from fastapi import UploadFile


class ImageStorage(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, subfolder: str = "") -> str:
        ...

    @abstractmethod
    async def delete(self, url: str) -> None:
        ...

    @abstractmethod
    def get_relative_path(self, url: str) -> str:
        ...
