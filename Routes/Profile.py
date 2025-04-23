from Controllers.ProfileController import ProfileController


from fastapi import APIRouter, Request ,Query ,Depends ,UploadFile, File
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from Models.UserUpdate import *




router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.post("/update-profile")
async def updateProfile(request : Request,token:Annotated[str, Depends(oauth2_scheme)], data : UserDataVal):
    # print ( "data f router ",data)
    return  ProfileController.update_profile(request=request, token=token, data=data)


@router.post("/add-social-media")
async def addSocialMedia(request : Request, token:Annotated[str, Depends(oauth2_scheme)], data : SocialMediaAdd):
    return ProfileController.add_social_media(request=request, token=token, social=data)



@router.post("/delete-social-media")
async def deleteSocialMedia(request : Request, token:Annotated[str, Depends(oauth2_scheme)], data : SocialMediaDelete):
    return ProfileController.delete_social_media(request=request, token=token, id=data.id)

@router.post("/add-image")
async def addImageMagasin(request : Request, token:Annotated[str, Depends(oauth2_scheme)], image : UploadFile = File(...)):
    return ProfileController.add_image(request=request, token=token, image_data= image )

@router.post("/delete-image")
async def deleteImageMagasin(request : Request, token:Annotated[str, Depends(oauth2_scheme)], data : ImageDelete):
    return ProfileController.delete_image(request=request, token=token, id = data.id)

# @router.get("/get-info")
# async def infoUsers(request : Request):
#     return ProfileController.info_users(request=request, token=request.headers.get('Authorization'))



