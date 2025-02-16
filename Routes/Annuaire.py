from typing import Annotated
from fastapi import APIRouter, Request ,Query ,Depends
from Controllers.AnnuaireController import AnnuaireController
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()
#la table annuiare elle est vide 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@router.get("/contacts")
async def getContacts(tokenUrl: str = Depends(oauth2_scheme),idWilaya: int = Query(None, description="L'id de la wilaya doit être un entier"),search: str = Query(None, description="La recherche doit etre un string")):
    return AnnuaireController.get_contacts(tokenUrl=tokenUrl,idWilaya=idWilaya,search=search)



