from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import TypeVar

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from httpx import AsyncClient

from archive import BaseScraper, LSScraper, QuestionModel, RSScraper
from archive.generics.cloud import Cloud, File

logger = logging.getLogger("archive")
handler = logging.FileHandler("archive.log", mode="w")
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

T = TypeVar("T", bound=QuestionModel)


class Drive:
    def __init__(self, creds: dict[str, str]):
        self.creds = Credentials.from_service_account_info(creds)
        self.service = build("drive", "v3", credentials=self.creds)

    def _create_folder(self, folder: str, parent: str):
        body = {
            "name": folder,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent],
        }
        return self.service.files().create(body=body, fields="id").execute()

    def _upload_file(self, file: File, folder: str):
        body = {"name": file.name, "parents": [folder]}
        media = MediaIoBaseUpload(file.buffer(), mimetype=file.mimetype)
        return (
            self.service.files()
            .create(body=body, media_body=media, fields="id")
            .execute()
        )

    async def create_folder(self, folder: str, parent: str):
        return self._create_folder(folder, parent)

    async def upload_file(self, file: File, folder: str):
        return self._upload_file(file, folder)


class Runner:
    def __init__(
        self,
        *,
        terms: list[str],
        scrapers: list[type[BaseScraper]],
        cloud: Cloud,
        threshold: timedelta,
        parent_folder_id: str,
    ):
        self.terms = terms
        self.scrapers = scrapers
        self.cloud = cloud
        self.threshold = threshold
        self.folder_id: str | None = None
        self.parent_folder_id: str = parent_folder_id

    async def get_folder(self) -> str:
        if f := self.folder_id:
            return f
        now = datetime.now().strftime("%d-%m-%Y")
        meta = await self.cloud.create_folder(now, self.parent_folder_id)
        self.folder_id = meta["id"]
        return self.folder_id

    async def run_scraper(self, scraper_type: type[BaseScraper[T]]) -> list[T]:
        scraper = await scraper_type.new()
        folder = await self.get_folder()
        client = AsyncClient(timeout=None)
        data: list[T] = []
        async with asyncio.TaskGroup() as tg:
            async for question in scraper.scrape(terms=self.terms):
                if datetime.today() - question.get_date() <= self.threshold:
                    data.append(question)
                    file = await File.from_url(
                        question.url(),
                        filename=f"{question.__name__}-{question.number}.{question.filetype()}",
                        client=client,
                    )
                    tg.create_task(self.cloud.upload_file(file, folder))
        await client.aclose()
        return data

    async def __call__(self):
        coros = [self.run_scraper(t) for t in self.scrapers]
        res = await asyncio.gather(*coros)
        print(len([q for p in res for q in p]))


async def main():
    terms = ["suicide", "mental health", "kill self"]
    scrapers = [LSScraper, RSScraper]
    threshold = timedelta(weeks=1)

    creds = os.getenv("ARCHIVE_SERVICE_ACCOUNT_CREDENTIALS")
    if not creds:
        with open("service_account.json") as f:
            creds = f.read()

    creds = json.loads(creds)
    cloud = Drive(creds)

    runner = Runner(
        scrapers=scrapers,
        terms=terms,
        cloud=cloud,
        threshold=threshold,
        parent_folder_id="1H8afWmK6af6vUAcaxNQpJK20Wx3AQ_Nq",
    )

    start = time.perf_counter()
    await runner()
    end = time.perf_counter()

    print(f"Finished in {end - start}s.")


asyncio.run(main())
