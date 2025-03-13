from Controllers.MarkingController import MarkingController
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



# @router.get("/my_marking")
# async def my_marking(request : Request,token:Annotated[str, Depends(oauth2_scheme)],id_det: int = Query(None, description="L'id doit être un entier")):
#     return MarkingController.get_all_marking(request=request, token=token,id_det=id_det)


@router.get("/all_marking")
async def all_markings(request : Request,token:Annotated[str, Depends(oauth2_scheme)]):
    return MarkingController.get_all_markings(request=request, token=token)

# @router.post("/marking_order")
# async def marking_order(request : Request,id_det: int = Query(None, description="L'id doit être un entier"),idStand: int = Query(None, description="L'id doit être un entier")):
#     return MarkingController.get_marking_order(request=request, id_det=id_det,idStand=idStand)



# @router.get("/description_stand")
# async def desc_stand(request : Request,token:Annotated[str, Depends(oauth2_scheme)],idStand: int = Query(None, description="L'id doit être un entier")):
#     return MarkingController.get_desc_stand(request=request, token=token,idStand=idStand)

