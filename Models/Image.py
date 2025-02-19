from pydantic import BaseModel

class Image(BaseModel):
    id: int
    image: str
