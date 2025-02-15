from pydantic import BaseModel

class UserInDB(User):
    hashed_password: str