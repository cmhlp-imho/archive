import asyncio

from pydantic import ValidationError
from archive.generics.scraper import BaseScraper
from archive.rajyasabha.models import RSQuestion


class RSScraper(BaseScraper[RSQuestion]):

    BASE_URL = "https://rsdoc.nic.in/Question/Search_Questions"

    def get_url(self, search_string: str, *, fields: list[str] = ["qtitle"]) -> str:
        clauses: list[str] = []
        for field in fields:
            clauses.append(f"{field} LIKE '%{search_string}%'")
        clause = " OR ".join(clauses)
        return f"{self.BASE_URL}?whereclause=({clause})"

    async def get_page(self, search_string: str):
        url = self.get_url(search_string)
        headers = {"Content-Type": "application/json"}
        resp = await self.get(str(url), headers=headers)
        return [RSQuestion(**data) for data in resp.json()]

    async def scrape(self, terms: list[str]):
        tasks: list[asyncio.Task[list[RSQuestion]]] = []
        for term in terms:
            task = asyncio.create_task(self.get_page(term))
            tasks.append(task)
        for page in asyncio.as_completed(tasks):
            for ques in await page:
                yield ques
