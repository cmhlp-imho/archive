from __future__ import annotations

import asyncio
import datetime
import logging
from typing import TYPE_CHECKING, Any, Protocol

from pydantic import BaseModel

__all__ = ("QuestionModel",)

logger = logging.getLogger("archive")

if TYPE_CHECKING:
    from httpx import AsyncClient


class Writable(Protocol):
    """A Protocol that accepts any object that implements a `write` method that accepts `bytes`.
    This could be a file object returned by open(), or an in-memory buffer like io.BytesIO.
    """

    def write(self, data: bytes, /) -> Any:
        ...


class EmptyFileException(Exception):
    def __init__(self, question: QuestionModel):
        self.question = question


class QuestionModel(BaseModel):
    """Represents a Question from either house of the Parliament."""

    number: str | float | int
    subject: str
    __name__: str

    def get_date(self) -> datetime.datetime:
        """Returns the Question's date.
        Subclasses should implement this method.
        """
        raise NotImplementedError

    def url(self) -> str:
        """Returns the PDF URL.
        Subclasses should implement this method.
        """
        raise NotImplementedError

    def filetype(self):
        items = self.url().split("/")
        return items[-1].split(".")[-1]

    async def save(self, writable: Writable, client: AsyncClient):
        resp = await client.get(self.url(), timeout=None)
        if data := resp.content:
            await asyncio.to_thread(writable.write, data)
        else:
            raise EmptyFileException(self)

    def __str__(self):
        return f"{self.__name__}{self.number}) {self.subject}: {self.url()}"
