from datetime import datetime

from pydantic import Field, validator

from archive.generics.models import QuestionModel

__all__ = ("RSQuestion",)


class RSQuestion(QuestionModel):

    __name__ = "RSQ"

    mp_code: int | None
    qslno: int
    qtitle: str
    qtype: str
    ans_date: str
    adate: datetime
    shri: str  # Yes, this is a real key. I promise.
    qno: float
    name: str
    min_name: str
    qn_text: str
    ans_text: str | None
    ses_no: int
    depc: int | None
    status: str
    P_flag: str
    files: str
    hindifiles: str
    eng_file_dsp: str
    hindi_file_dsp: str
    min_code: int
    supp: str | None

    number: int = Field(alias="qno")
    subject: str = Field(alias="qtitle")
    date: datetime = Field(alias="adate")

    def url(self):
        return self.files

    @validator("ans_date", pre=True)
    def convert_ans_date(cls, raw: str):
        return raw
        # return datetime.strptime(raw, "%d.%m.%Y")

    @validator("adate", pre=True)
    def convert_adate(cls, raw: str):
        return datetime.fromisoformat(raw)

    def get_date(self):
        return self.adate
