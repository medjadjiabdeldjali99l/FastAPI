from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from Models.SocialMedia import SocialMedia
from Models.Image import Image

class UserData(BaseModel):
    id: Optional[int] = None
    nom: Optional[str] = None
    tel: Optional[str] = None
    raisonSociale: Optional[str] = None
    natureCommerce: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    wilaya: Optional[str] = None
    localisation: Optional[str] = None
    email: Optional[str] = None
    otherTel: Optional[str] = None
    pourcentageProfil: Optional[int] = None
    idDetaillant: Optional[str] = None
    niveauDetaillant: Optional[int] = None
    pointsDetaillant: Optional[int] = None
    pourcentageNiveau: Optional[int] = None
    delegue: Optional[list] = None
    socialMedia: List[SocialMedia] = []
    images: List[Image] = []

    model_config = ConfigDict(from_attributes=True)


class CondidateData(BaseModel):
    id: Optional[int] = None
    nom: Optional[str] = None
    tel: Optional[str] = None
    natureCommerce: Optional[str] = None
    ville: Optional[str] = None
    wilaya: Optional[str] = None
    raisonSociale: Optional[str] = None
    etatCondidat : Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None

