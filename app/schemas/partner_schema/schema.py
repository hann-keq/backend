from pydantic import BaseModel

class PartnerBase(BaseModel):
    id_partner: int
    nama_partner: str
    jenis_partner: str
    alamat: str
    no_telepon : str
    foto: str | None
    email : str | None

class PartnerCreate(PartnerBase):
    pass

class PartnerResponse(PartnerBase):
    nama_partner: str
    jenis_partner: str
    alamat: str
    no_telepon : str
    foto: str | None
    email : str | None
    class Config:
        from_attributes = True