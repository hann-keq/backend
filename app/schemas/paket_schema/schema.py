from pydantic import BaseModel
from typing import List
from fastapi import Form

class DetailPaketCreate(BaseModel):
    fitur : str

class PakeGroomingCreate(BaseModel):
    id_partner: int
    nama_paket_grooming: str
    harga:float
    fitur : List[str] = [] # list fitur untuk detail paket grooming

    @classmethod
    def as_form(
        cls,
        id_partner: int = Form(...),
        nama_paket_grooming: str = Form(...),
        harga: float = Form(...),
        
    ):
        return cls(
            id_partner=id_partner,
            nama_paket_grooming=nama_paket_grooming,
            harga=harga,
            
        
    )

class PaketGroomingUpdate(BaseModel):
    nama_paket_grooming: str
    harga:float

class PaketGroomingResponse(BaseModel):
    id_paket_grooming: int
    id_partner: int
    nama_paket_grooming: str
    harga: float
    

    class Config:
        from_attributes = True