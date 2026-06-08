from pydantic import BaseModel, model_validator
from fastapi import Form
from app.schemas.user_schema.user_base import AdminRole
from app.schemas.user_schema.user_base import UserBase,UserAsAdmin


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

class AdminLogin(BaseModel):
    email: str
    password: str
    role : str = AdminRole.Admin.value

    @classmethod
    def as_form(cls, email: str = Form(...), password: str = Form(...), role: str = Form(AdminRole.Admin.value)):
        return cls(email=email, password=password, role=role)


class AdminCreate(UserAsAdmin):
    pass