import uuid
from pathlib import Path

from fastapi import UploadFile

from app.storage.base import ImageStorage

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


class LocalImageStorage(ImageStorage):
    def __init__(self, upload_dir: str | Path) -> None:
        self._upload_dir = Path(upload_dir)

    async def save(self, file: UploadFile, subfolder: str = "") -> str:
        content = await file.read()
        ext = Path(file.filename or "image.jpg").suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            ext = ".jpg"

        subdir = self._upload_dir / subfolder if subfolder else self._upload_dir
        subdir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = subdir / filename
        filepath.write_bytes(content)

        return f"/uploads/{subfolder}/{filename}" if subfolder else f"/uploads/{filename}"

    async def delete(self, url: str) -> None:
        relative = self.get_relative_path(url)
        filepath = self._upload_dir / relative
        if filepath.exists():
            filepath.unlink()

    def get_relative_path(self, url: str) -> str:
        prefix = "/uploads/"
        if url.startswith(prefix):
            return url[len(prefix):]
        return url.lstrip("/")
