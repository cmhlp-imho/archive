from pydantic import Field, validator
from datetime import datetime
from archive.generics.models import QuestionModel


class RSQuestion(QuestionModel):
    mp_code: int | None
    qslno: int
    qtitle: str
    qtype: str
    ans_date: datetime
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

    number: float = Field(alias="qno")
    subject: str = Field(alias="qtitle")
    # date: datetime = Field(alias="ans_date")

    def url(self):
        return self.files

    @validator("ans_date", pre=True)
    def convert_ans_date(cls, raw: str):
        return datetime.strptime(raw, "%d.%m.%Y")

    @validator("adate", pre=True)
    def convert_adate(cls, raw: str):
        return datetime.fromisoformat(raw)
