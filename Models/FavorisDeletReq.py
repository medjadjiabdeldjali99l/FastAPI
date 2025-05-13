from pydantic import BaseModel

class FavorisDeleteRequest(BaseModel):
    idProduct: int
    idDet: int
