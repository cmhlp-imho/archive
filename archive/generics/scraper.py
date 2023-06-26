from __future__ import annotations

from abc import abstractmethod
from logging import getLogger
from typing import Any, AsyncGenerator, Generic, TypeVar

from httpx import AsyncClient

from archive.generics.models import QuestionModel

__all__ = ("BaseScraper",)


logger = getLogger("archive")

T = TypeVar("T", bound=QuestionModel, covariant=True)


class BaseScraper(Generic[T]):
    """Base scraper class. This should be subclassed and site-specific implementations should be written."""

    BASE_URL: str

    def __init__(self, client: AsyncClient):
        self.client = client

    async def get(self, url: str, *args: Any, **kwargs: Any):
        """An alias for `httpx.AsyncClient.get`."""
        logger.debug(f"GET {url}")
        return await self.client.get(url, *args, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.client.aclose()

    async def close(self):
        await self.client.aclose()

    @classmethod
    async def new(cls):
        """Returns a new Scraper instance.
        This is the preferred way of creating new Scrapers.
        """
        client = AsyncClient()
        return cls(client)

    @abstractmethod
    def scrape(
        self, *args: Any, terms: list[str], **kwargs: Any
    ) -> AsyncGenerator[T, None]:
        """An async generator that yields QuestionModels.
        Subclasses should implement this.
        """
        raise NotImplementedError

    @classmethod
    async def collect(cls, *args: Any, terms: list[str], **kwargs: Any):
        """Calls `scrape` and collects the questions into a list."""
        items: list[T] = []
        async with await cls.new() as s:
            async for item in s.scrape(*args, terms=terms, **kwargs):
                items.append(item)
        return items
