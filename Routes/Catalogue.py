from fastapi import APIRouter, Request ,Query ,Depends
from Controllers.CatalogueController import CatalogueController
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/all_categories")
async def my_category(request : Request ,token:Annotated[str, Depends(oauth2_scheme)]):
    return CatalogueController.get_all_category(request=request, token=token)

@router.get("/all_type_surface")
async def surface(request : Request ,token:Annotated[str, Depends(oauth2_scheme)]):
    return CatalogueController.get_all_surfaces(request=request, token=token)

@router.get("/all_type_peinture")
async def surface(request : Request ,token:Annotated[str, Depends(oauth2_scheme)]):
    return CatalogueController.get_all_peinture(request=request, token=token)
