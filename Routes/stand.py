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

@router.post("/stand_order")
async def stands_order(request : Request,id_det: int = Query(None, description="L'id doit être un entier"),idStand: int = Query(None, description="L'id doit être un entier")):
    return StandController.get_stands_order(request=request, id_det=id_det,idStand=idStand)



@router.get("/description_stand")
async def desc_stand(request : Request,token:Annotated[str, Depends(oauth2_scheme)],idStand: int = Query(None, description="L'id doit être un entier")):
    return StandController.get_desc_stand(request=request, token=token,idStand=idStand)

