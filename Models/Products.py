# from pydantic import BaseModel
# from Models.Conditionnement import Conditionnement
# from typing import Optional, List

# class ProductsData(BaseModel):
#     id: int | None = None
#     name: str | None = None
#     default_code: str | None = None
#     list_price: float | None = None
#     category :str |None = None
#     typeSurface : str |None = None
#     typePeinture : str |None = None
#     etoiles : int | None = None
#     image : str | None = None
#     img_url : str | None = None
#     descMobile : str | None = None 
#     # cond :List[Conditionnement] | None =None
    

#     class Config:
#         from_attributes = True  # Anciennement `orm_mode = True`


from pydantic import BaseModel
from Models.Conditionnement import Conditionnement
from typing import Optional, List

class ProductsData(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    default_code: Optional[str] = None
    list_price: Optional[float] = None
    category: Optional[str] = None
    typeSurface: Optional[str] = None
    typePeinture: Optional[str] = None
    etoiles: Optional[int] = None
    image: Optional[str] = None
    img_url: Optional[str] = None
    descMobile: Optional[str] = None
    cond: Optional[List[Conditionnement]] = None  # Packaging info

    class Config:
        from_attributes = True  # équivalent de orm_mode = True
