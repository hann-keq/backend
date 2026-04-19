from pydantic import BaseModel, model_validator

from app.schemas.user_schema.user_base import UserBase


class UserCreate(UserBase):
    @model_validator(mode= 'after')
    def validate_passwords(self):
        password = self.password
        if password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class UserLogin(BaseModel):
    email: str
    password: str