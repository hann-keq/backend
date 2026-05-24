from typing import Optional
from enum import Enum
from pydantic import BaseModel,ConfigDict

class AdminRole(str,Enum):
    Admin = 'Admin'

class UserBase(BaseModel):
    nama : str
    email : str
    no_telepon : str
    password : str
    foto : Optional[str] = None
    confirm_password : str

    model_config = ConfigDict(from_attributes=True)

class UserAsAdmin(BaseModel):
    nama : str
    email : str
    no_telepon : str
    password : str
    foto : Optional[str] = None
    confirm_password : str
    role: AdminRole = AdminRole.Admin.value

    model_config = ConfigDict(from_attributes=True)