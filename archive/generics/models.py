from __future__ import annotations
from pathlib import Path
from typing import Any, Protocol, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from httpx import AsyncClient


class Writeable(Protocol):
    def write(self, data: bytes) -> Any:
        ...


class QuestionModel(BaseModel):
    """Represents a Question from either house of the Parliament."""

    number: str | float | int
    subject: str

    def url(self) -> str:
        raise NotImplementedError

    async def save_pdf(self, path: Path, client: AsyncClient):
        resp = await client.get(self.url())
        with path.open("wb") as f:
            f.write(resp.content)
