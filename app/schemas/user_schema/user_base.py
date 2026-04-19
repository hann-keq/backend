from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str
    phone_number: Optional[str] = None