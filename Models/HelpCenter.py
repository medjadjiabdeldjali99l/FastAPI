from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class HelpCenter(BaseModel):
    objetEmail : List
    Faq : List
    urlVid: str

class SendEmail(BaseModel):
    content : str