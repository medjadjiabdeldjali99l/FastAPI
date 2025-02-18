from Controllers.MainController import MainController
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/actualite_evenements")
async def me(request : Request,token:Annotated[str, Depends(oauth2_scheme)]):
    return MainController.get_actualite_events(request=request, token=token)