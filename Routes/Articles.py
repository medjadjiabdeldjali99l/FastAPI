from fastapi import APIRouter, Request ,Query ,Depends
from Controllers.ArticlesController import ArticlesController
from Models.Products import ProductsData
from fastapi_pagination import Page, paginate ,Params
from Models.Params import CustomParams
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/all_products")
async def my_products(request : Request,token:Annotated[str, Depends(oauth2_scheme)],id_cat: int = Query(None, description="L'id doit être un entier"),search: str = Query(None, description="L'code doit être un string"),id_sur:int= Query(None, description="L'id doit être un entier") ,id_paint:int= Query(None, description="L'id doit être un entier"),etoile:int= Query(None, description="L'id doit être un entier"),new_product:bool= Query(None, description="L'id doit être un boolien"),params: CustomParams = Depends()) -> Page[ProductsData]:
    return ArticlesController.get_all_products(request=request, token=token,id_cat=id_cat,search=search,id_sur=id_sur ,id_paint=id_paint,etoile=etoile,new_product=new_product ,params=params)


@router.get("/packaging")
async def my_conditionement(request : Request ,token:Annotated[str, Depends(oauth2_scheme)],productId: int = Query(description="L'id doit être un entier")):
    return ArticlesController.getConditionement(request=request, token=token ,productId=productId)
