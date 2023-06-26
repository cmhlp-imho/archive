import asyncio

from archive.generics.scraper import BaseScraper
from archive.rajyasabha.models import RSQuestion

__all__ = ("RSScraper",)


class RSScraper(BaseScraper[RSQuestion]):

    BASE_URL = "https://rsdoc.nic.in/Question/Search_Questions"

    def get_url(
        self, search_string: str, *, fields: list[str] = ["qtitle", "qn_text"]
    ) -> str:
        """Creates an SQL Query and returns a URL string.

        Parameters
        ----------
        search_string: :class:`str`
            The string to search for in questions.

        fields: :class:`list[str]`
            A list of field names from `RSQuestion` to search in.
            Defaults to one field, "qtitle".

        Returns
        -------
        :class:`str`
            The URL string.
        """
        clauses: list[str] = []
        for field in fields:
            clauses.append(f"{field} LIKE '%{search_string}%'")
        clause = " OR ".join(clauses)
        return f"{self.BASE_URL}?whereclause=({clause})"

    async def get_page(self, search_string: str):
        """Requests and retrieves the questions from a page.

        Parameters
        ----------
        search_string: :class:`str`
            The string to search for.

        Returns
        -------
        :class:`list[RsQuestion]`
            A list of the parsed `RSQuestion`.
        """
        url = self.get_url(search_string)
        headers = {"Content-Type": "application/json"}
        resp = await self.get(str(url), headers=headers, timeout=None)
        return [RSQuestion(**data) for data in resp.json() if data.get("qn_text")]

    async def scrape(self, terms: list[str]):
        tasks: list[asyncio.Task[list[RSQuestion]]] = []
        for term in terms:
            task = asyncio.create_task(self.get_page(term))
            tasks.append(task)
        for page in asyncio.as_completed(tasks):
            for ques in await page:
                yield ques
