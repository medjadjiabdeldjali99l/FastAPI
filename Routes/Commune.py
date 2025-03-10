from Controllers.CommuneController import CommuneController
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.get("/allCommune")
async def commune(request : Request,codeWilayaOdoo: str = Query(description="L'id doit être un entier")):
    return CommuneController.get_all_commune(request=request, codeWilayaOdoo=codeWilayaOdoo)
