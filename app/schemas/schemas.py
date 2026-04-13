from pydantic import BaseModel, model_validator
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    verify_password: str

    @model_validator(mode= 'after')
    def validate_passwords(self):
        password = self.password
        validating_password = self.verify_password
        if password != validating_password:
            raise ValueError("Passwords do not match")
        return self

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: str
    user_id: int

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

class TaskWithUserResponse(TaskResponse):
    user: UserResponse