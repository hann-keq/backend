from pydantic import BaseModel
from fastapi import Form

class DokterCreate(BaseModel):
    id_partner: int
    nama_dokter: str
    spesialis: str
    foto : str | None

    @classmethod
    def as_form(
        cls,
        id_partner: int = Form(...),
        nama_dokter: str = Form(...),
        spesialis: str = Form(...),
        foto: str | None = Form(None)
    ):
        return cls(
            id_partner=id_partner,
            nama_dokter=nama_dokter,
            spesialis=spesialis,
            foto=foto
        )
class DokterUpdate(BaseModel):
    nama_dokter: str | None
    spesialis: str | None
    foto : str | None
class DokterResponse(BaseModel):
    id_dokter:int
    
    class Config:
        from_attributes = True