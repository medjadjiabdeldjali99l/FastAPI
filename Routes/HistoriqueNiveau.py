from Controllers.HistoriqueNiveauController import HistoriqueNiveauController
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/my_niveau")
async def my_niveau(request : Request,token:Annotated[str, Depends(oauth2_scheme)],id_det: int = Query(description="L'id doit être un entier") ,niveauDet: int = Query(description="L'id doit être un entier")):
    return HistoriqueNiveauController.get_all_niveaux(request=request, token=token,id_det=id_det , niveauDet=niveauDet)