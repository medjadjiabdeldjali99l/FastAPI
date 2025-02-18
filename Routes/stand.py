from Controllers.StandController import StandController
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.get("/my_stand")
async def my_stand(request : Request,token:Annotated[str, Depends(oauth2_scheme)],id_det: int = Query(None, description="L'id doit être un entier")):
    return StandController.get_all_stand(request=request, token=token,id_det=id_det)


@router.get("/all_stand")
async def all_stand(request : Request,token:Annotated[str, Depends(oauth2_scheme)]):
    return StandController.get_all_stands(request=request, token=token)