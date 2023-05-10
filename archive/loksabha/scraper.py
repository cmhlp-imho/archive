import asyncio
from yarl import URL

from archive.generics.scraper import BaseScraper
from archive.loksabha.models import LSQuestion, Page


class LSScraper(BaseScraper[LSQuestion]):

    BASE_URL = "https://eparlib.nic.in/restv3/fetch/all?collectionId=3"
    PAGE_SIZE = 100

    def get_url(self, *, loksabha_no: int, search_string: str, page_no: int = 0) -> URL:
        """Returns the query URL with the given parameters.

        Parameters
        ----------
        loksabha_no: :class:`int`
            The Lok Sabha number.

        search_string: :class:`str`
            The keyword(s) to search for.

        page_no: :class:`int` = 0
            The page number to retrieve. Defaults to zero.
            Page size can be configured via the PAGE_SIZE attribute.

        Returns
        -------
        :class:`yarl.URL`
            The URL object.
        """
        lok_no = f"{loksabha_no:02}"
        params = {
            "loksabhaNo": lok_no,
            "anyWhere": search_string,
            "start": page_no * self.PAGE_SIZE,
            "rows": self.PAGE_SIZE,
        }
        url = URL(self.BASE_URL) % params
        return url

    async def get_page(
        self,
        *,
        loksabha_no: int,
        search_string: str,
        page_no: int,
    ):
        url = self.get_url(
            loksabha_no=loksabha_no, search_string=search_string, page_no=page_no
        )
        resp = await self.get(str(url))
        data = resp.json()
        return Page(**data)

    async def _get_all_pages(self, *, loksabha_no: int, search_string: str):
        initial_task = asyncio.create_task(
            self.get_page(
                loksabha_no=loksabha_no, page_no=0, search_string=search_string
            )
        )
        initial = await initial_task
        total = initial.rowsCount // self.PAGE_SIZE
        tasks: list[asyncio.Task[Page]] = [initial_task]

        for i in range(1, total):
            coro = self.get_page(
                loksabha_no=loksabha_no, search_string=search_string, page_no=i
            )
            task = asyncio.create_task(coro)
            tasks.append(task)

        return tasks

    async def scrape(self, *, terms: list[str]):
        t_type = list[asyncio.Task[Page]]
        tasks: list[asyncio.Task[t_type]] = []
        for term in terms:
            for lok_no in range(1, 18):
                coro = self._get_all_pages(loksabha_no=lok_no, search_string=term)
                task = asyncio.create_task(coro)
                tasks.append(task)

        for task in asyncio.as_completed(tasks):
            for subtask in asyncio.as_completed(await task):
                page = await subtask
                for ques in page.records:
                    yield ques
