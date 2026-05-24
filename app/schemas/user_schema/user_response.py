from pydantic import BaseModel

from app.schemas.user_schema.user_base import UserBase


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class UserResponseOnlyId(BaseModel):
    id: int

    class Config:
        from_attributes = True