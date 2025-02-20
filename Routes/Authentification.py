from Controllers.AuthentificationController import AuthentificationController
from Models.UserConnexion import *
from fastapi import APIRouter, Request ,Query ,Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm





router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




@router.get("/me")
async def me(request : Request, token:Annotated[str, Depends(oauth2_scheme)]):
    return AuthentificationController.me(request=request, token=token)

@router.post("/login")
async def login(request : Request , UserLogin:Userlogin ):
    return AuthentificationController.login(request=request ,UserLogin=UserLogin)

@router.post("/inscription")
async def inscription(request: Request ,user:RegisterUser ):
    return AuthentificationController.inscription(request=request,data=user)

@router.post("/adhesion")
async def adhesion(request: Request, user : AdhererUser):
    return AuthentificationController.adhesion(request=request, data=user)

# @router.post("/mot-de-passe-oublie")
# async def motDePasseOublie (request: Request, data : ForgotPwd):
#     return AuthentificationController.motDePasseOublie(request=request,data=data)