from pydantic import BaseModel
from typing import Optional

class Userlogin(BaseModel):
    phone: str
    password: str

class RegisterUser(BaseModel):
    phone : str
    codeDet : str

class AdhererUser(BaseModel):  
    name: str
    name_magasin: str = None    # Raison sociale
    categorie_id : int  # Mapping ids hardcoded in front par ex  categorie_id=1 -> quicallerie gen...
    state_id: int
    commune_id: int
    phone_compte: str
    country_id: Optional[int] = 62 # Liste countries avec ids (  id Algerie = 62)
    
class ForgotPwd(BaseModel):
    phone : str