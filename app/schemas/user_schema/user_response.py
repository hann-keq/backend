from pydantic import BaseModel

from app.schemas.user_schema.user_base import UserBase


class UserResponse(BaseModel):
    id_user: int
    nama: str
    email: str

    class Config:
        from_attributes = True

class UserResponseOnlyId(BaseModel):
    id_user: int
    nama:str
    email:str
    no_telepon:str
    foto:str | None

    class Config:
        from_attributes = True