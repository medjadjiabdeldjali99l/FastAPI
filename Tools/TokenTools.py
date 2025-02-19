from os import getenv
from dotenv import load_dotenv
from Models.TokenData import TokenData
from typing import Annotated
from fastapi import APIRouter, Request ,Query ,Depends ,HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import InvalidTokenError
from datetime import datetime, timedelta, timezone

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
    def generate_token(data: dict, expires_delta: timedelta | None = None):

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt
        




    @staticmethod
    def check_token(token: Annotated[str, Depends(oauth2_scheme)]):
              
        try:
            # print(" had 2", SECRET_KEY,ALGORITHM)
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # print("=========================================================", payload)
            if payload is None:
                raise False
            token_data = TokenData(**payload)
        except InvalidTokenError:
            raise credentials_exception
        print ("hada typeee ta3 playe load", type(token_data))
        return token_data

