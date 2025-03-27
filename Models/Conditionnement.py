from pydantic import BaseModel

class Conditionnement(BaseModel):
    id: int
    name: str
    qty:float 
