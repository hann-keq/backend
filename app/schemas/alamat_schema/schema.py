from pydantic import BaseModel
from fastapi import Form

class AlamatCreate(BaseModel):
    alamat : str
    kota : str
    provinsi : str
    kode_pos : int

    @classmethod
    def as_form(
        cls,
        alamat: str = Form(...),
        kota: str = Form(...),
        provinsi: str = Form(...),
        kode_pos: int = Form(...)
    ):
        return cls(
            alamat=alamat,
            kota=kota,
            provinsi=provinsi,
            kode_pos=kode_pos
        )
class AlamatUpdate(AlamatCreate):
    pass

class AlamatResponse(AlamatCreate):
    id_alamat: int
    id_user: int

    class Config:
        from_attributes = True
