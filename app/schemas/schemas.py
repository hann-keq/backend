from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: str

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