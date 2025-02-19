from pydantic import BaseModel

class TokenData(BaseModel):
    id : int | None = None
    telephone : str | None = None
    codeDetaillant: str | None = None


