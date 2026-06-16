from pydantic import BaseModel
from datetime import date, time
from fastapi import Form


class JanjiTemuCreate(BaseModel):
    id_pet: int
    id_dokter: int
    tanggal_janji: date
    jam_janji: time
    keluhan: str

    @classmethod
    def as_form(
        cls,
        id_pet: int = Form(...),
        id_dokter: int = Form(...),
        tanggal_janji: date = Form(...),
        jam_janji: time = Form(...),
        keluhan: str = Form(...),
    ):
        return cls(
            id_pet=id_pet,
            id_dokter=id_dokter,
            tanggal_janji=tanggal_janji,
            jam_janji=jam_janji,
            keluhan=keluhan,
        )


class JanjiTemuUpdateStatus(BaseModel):
    status_janji: str  # Menunggu | Selesai | Dibatalkan


class JanjiTemuResponse(JanjiTemuCreate):
    id_janji_temu: int
    id_user: int
    status_janji: str

    class Config:
        from_attributes = True
