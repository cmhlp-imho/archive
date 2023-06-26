import mimetypes
from io import BytesIO
from pathlib import Path
from typing import Any, Protocol

from httpx import AsyncClient

__all__ = "File", "Cloud"


class File:
    """Represents a file that can be uploaded to a Cloud platform.
    This class normalizes the interface for files and in-memory buffers.
    """

    def __init__(self, data: bytes, name: str):
        self.data = data
        self.name = name
        self.mimetype = mimetypes.guess_type(name)[0] or "application/pdf"

    def buffer(self):
        return BytesIO(self.data)

    @classmethod
    def from_path(cls, path: Path):
        with path.open("wb") as f:
            return File(f.read(), str(path))

    @classmethod
    async def from_url(
        cls,
        url: str,
        *,
        filename: str,
        client: AsyncClient,
        timeout: float | None = None
    ):
        resp = await client.get(url, timeout=timeout)
        file = cls(resp.content, filename)
        file.mimetype = mimetypes.guess_type(url)[0] or "application/pdf"
        return file


class Cloud(Protocol):
    async def upload_file(self, file: File, folder: str) -> Any:
        ...

    async def create_folder(self, folder: str, parent: str) -> Any:
        ...
