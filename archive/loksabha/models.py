from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, validator

from archive.generics.models import QuestionModel


class LSQuestion(QuestionModel):
    title: str
    type: str
    sessionNo: str
    language: str
    questionType: str
    source: str
    committeeName: str
    debate: str
    handle: str
    keywordsCount: str
    phraseCount: str
    reportNo: str
    members: list[str]
    files: list[str]
    ministry: list[str]
    ministerName: list[str]
    councilOfStateNo: str
    resourceId: str
    assemblyNo: int | str
    date: datetime
    loksabhaNo: int
    questionNo: str  # This is a string because some question numbers contain letters or asterisks in them.
    year: int

    number: str = Field(alias="questionNo")
    subject: str = Field(alias="title")

    @validator("date", pre=True)
    def convert_date(cls, raw: str):
        return datetime.strptime(raw, "%Y-%m-%d")

    def url(self):
        return self.files[0]


class Page(BaseModel):
    records: list[LSQuestion]
    rowsCount: int
    message: str
    statusCode: int
    start: int
    rows: int
    self: str
    timeTaken: str
    bucketFields: list[Any]
    bucketRanges: dict[str, Any]

    rows_count: int = Field(alias="rowsCount")
