from pydantic import BaseModel
from datetime import date

class MembershipCreate(BaseModel):
   tipe_membership: str
   tanggal_berlaku: date
   tanggal_kadaluarsa: date

class MembershipUpdate(MembershipCreate):
    pass

class MembershipResponse(MembershipCreate):
    id_membership: int
    id_user: int

    class Config:
        from_attributes = True