from os import getenv
from dotenv import load_dotenv
from Models.TokenData import TokenData
from typing import Annotated
from fastapi import APIRouter, Request ,Query ,Depends ,HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import InvalidTokenError

load_dotenv() 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY=getenv("SECRET_KEY")
ALGORITHM=getenv("ALGORITHM")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

class TokenTools:
    """Classe utilitaire pour la gestion des mots de passe."""

    @staticmethod
    def check_token(token: Annotated[str, Depends(oauth2_scheme)]):
              
        try:
            # print(" had 2", SECRET_KEY,ALGORITHM)
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # print("=========================================================", payload)
            if payload is None:
                raise False
        except InvalidTokenError:
            raise credentials_exception
        return payload

