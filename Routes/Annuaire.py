from typing import Annotated
from fastapi import APIRouter, Request ,Query ,Depends
from Controllers.AnnuaireController import AnnuaireController
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()
#la table annuiare elle est vide 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@router.get("/contacts")
async def getContacts(request : Request ,token:Annotated[str, Depends(oauth2_scheme)],fonction:str= Query(None, description="La fonction doit doit être un string soit sup ou delegue"),idWilaya: int = Query(None, description="L'id de la wilaya doit être un entier"),search: str = Query(None, description="La recherche doit etre un string")):
    return AnnuaireController.get_contacts(request=request,token=token,fonction=fonction,idWilaya=idWilaya,search=search)



