from pydantic import BaseModel
from datetime import date


class FavoritCreate(BaseModel):
    id_produk : int

class FavoritResponse(FavoritCreate):
    id_favorit : int
    id_user : int

    class Config:
        from_attributes = True
