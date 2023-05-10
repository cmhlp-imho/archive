from __future__ import annotations
import asyncio
from abc import abstractmethod
from httpx import AsyncClient
from logging import getLogger
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generic, TypeVar
from archive.generics.models import QuestionModel

if TYPE_CHECKING:
    from pathlib import Path

logger = getLogger(__name__)

T = TypeVar("T", bound=QuestionModel)


class BaseScraper(Generic[T]):
    """Base scraper class. This should be subclassed and site-specific implementations should be written."""

    BASE_URL: str

    def __init__(self, client: AsyncClient):
        self.client = client

    async def get(self, url: str, *args: Any, **kwargs: Any):
        """An alias for `httpx.AsyncClient.get`."""
        return await self.client.get(url, *args, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.client.aclose()

    @classmethod
    async def new(cls):
        """Returns a new Scraper instance.
        This is the preferred way of creating new Scrapers.
        """
        client = AsyncClient()
        return cls(client)

    @abstractmethod
    def scrape(self, *args: Any, **kwargs: Any) -> AsyncGenerator[T, None]:
        """An async generator that yields QuestionModels.
        Subclasses should implement this.
        """
        raise NotImplementedError

    @classmethod
    async def collect(cls, *args: Any, **kwargs: Any):
        """Calls `scrape` and collects the questions into a list."""
        items: list[T] = []
        async with await cls.new() as s:
            async for item in s.scrape(*args, **kwargs):
                items.append(item)
        return items

    async def save_pdfs(self, questions: list[T], path: Path):
        """Saves the PDFs of a list of Questions."""
        async with asyncio.TaskGroup() as tg:
            for ques in questions:
                fp = path / f"{type(ques).__qualname__}{ques.number}.pdf"
                coro = ques.save_pdf(fp, self.client)
                tg.create_task(coro)
