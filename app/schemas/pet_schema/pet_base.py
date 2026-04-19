from enum import Enum

from pydantic import BaseModel
from typing import Optional

class PetType(str,Enum):
    dog = 'dog'
    cat = 'cat'





class PetBase(BaseModel):
    name: str
    type: PetType
    breed: str
    age: int
    weight: int

