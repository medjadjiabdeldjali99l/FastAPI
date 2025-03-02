from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class HelpCenter(BaseModel):
    faqQuestion: List[str]
    faqAnswer : List[str]
    objet : List[str] 

class SendEmail(BaseModel):
    message : str