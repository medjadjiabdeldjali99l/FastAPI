from pydantic import BaseModel

class ProductsData(BaseModel):
    id: int | None = None
    name: str | None = None
    default_code: str | None = None
    list_price: float | None = None
    category :str |None = None
    typeSurface : str |None = None
    typePeinture : str |None = None
    etoiles : int | None = None
    image : str | None = None
    img_url : str | None = None
    descMobile : str | None = None 


    class Config:
        from_attributes = True  # Anciennement `orm_mode = True`
