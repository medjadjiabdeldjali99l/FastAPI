from Controllers.WilayaController import WilayaController
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.get("/allwilaya")
async def wilaya(request : Request,codeCountryOdoo: str = Query('DZ', description="L'id doit être un entier")):
    return WilayaController.get_all_wilaya(request=request,codeCountryOdoo=codeCountryOdoo)
