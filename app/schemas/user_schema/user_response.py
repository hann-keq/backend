from app.schemas.user_schema.user_base import UserBase


class UserResponse(UserBase):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True