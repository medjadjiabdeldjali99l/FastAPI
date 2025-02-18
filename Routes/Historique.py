from Controllers.HistoriqueController import HistoriqueController
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/my_points")
async def my_points(request : Request,token:Annotated[str, Depends(oauth2_scheme)],id_det: int = Query(None, description="L'id doit être un entier")):
    return HistoriqueController.get_all_points(request=request, token=token,id_det=id_det)