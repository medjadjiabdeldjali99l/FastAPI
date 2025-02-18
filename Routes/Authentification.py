from controllers.AuthentificationController import AuthentificationController

from validators.Authentification import *
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")






@router.get("/me")
async def me(request : Request, token:Annotated[str, Depends(oauth2_scheme)]):
    return AuthentificationController.me(request=request, token=token)

@router.post("/login")
async def login(user: UserLogin, request : Request):
    return AuthentificationController.login(request=request, phone=user.phone, password=user.password)

@router.post("/inscription")
async def inscription(user:RegisterUser,request: Request ):
    return AuthentificationController.inscription(request=request,data=user)

@router.post("/adhesion")
async def adhesion(request: Request, user : AdhererUser):
    return AuthentificationController.adhesion(request=request, data=user)

@router.post("/mot-de-passe-oublie")
async def motDePasseOublie (request: Request, data : ForgotPwd):
    return AuthentificationController.motDePasseOublie(request=request,data=data)