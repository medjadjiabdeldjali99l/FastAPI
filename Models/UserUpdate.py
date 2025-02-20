from Models.SocialMedia import SocialMediaType
from Models.Image import Image
from pydantic import BaseModel
from typing import Optional

class SocialMediaAdd(BaseModel):
    type : SocialMediaType
    url : str
    
class SocialMediaDelete(BaseModel):
    id : int

class UserDataVal(BaseModel):
    nom : str = None
    raisonSociale : str = None
    adresse : str = None
    localisation : str = None
    email : str = None
    otherTel : str = None

class AddImage(BaseModel):
    image : str

class ImageDelete(BaseModel):
    id : int