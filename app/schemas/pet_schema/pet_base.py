from enum import Enum

from pydantic import BaseModel
from typing import Optional

class PetType(str,Enum):
    ANJING = 'Anjing'
    KUCING = 'Kucing'

class GenderHewan(str,Enum):
    JANTAN = 'Jantan'
    BETINA = 'Betina'



class PetBase(BaseModel):
    
    nama_hewan: str
    jenis_hewan: PetType
    gender_hewan: GenderHewan
    umur: int
    berat: int
    foto_hewan: Optional[str] = None

