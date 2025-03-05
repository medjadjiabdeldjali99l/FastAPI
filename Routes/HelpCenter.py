from fastapi import APIRouter, Request ,Query ,Depends
from Controllers.HelpController import HelpController
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from Models.HelpCenter import SendEmail


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/help_centre")
async def help_centre(request : Request ,token:Annotated[str, Depends(oauth2_scheme)]):
    return HelpController.get_help(request=request, token=token)


@router.post("/send_email")
async def sendEmail(request : Request , content:SendEmail,idDetaillant: int = Query(None, description="L'id de detaillant doit être un entier"),idTopic: int = Query(None, description="L'id de Topic doit être un entier") ):
    return HelpController.SendEmailDetallaint(request=request , message =content ,idDetaillant=idDetaillant ,idTopic=idTopic)


