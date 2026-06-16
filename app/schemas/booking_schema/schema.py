from pydantic import BaseModel
from datetime import date,time
from fastapi import Form

class BookingCreate(BaseModel):
    id_pet: int
    id_paket_grooming : int
    tanggal_booking:date
    jam_booking:time

    @classmethod
    def as_form(
        cls,
        id_pet: int = Form(...),
        id_paket_grooming : int = Form(...),
        tanggal_booking:date = Form(...),
        jam_booking:time = Form(...)
    ):
        return cls(
            id_pet=id_pet,
            id_paket_grooming=id_paket_grooming,
            tanggal_booking=tanggal_booking,
            jam_booking=jam_booking
        )
class BookingUpdateStatus(BaseModel):
    status_booking: str

class BookingResponse(BookingCreate):
    id_booking_grooming: int
    id_user: int
    status_booking: str

    class Config:
        from_attributes = True
