from pydantic import BaseModel
from typing import List

class DetailOrderCreate(BaseModel):
    id_produk: int
    jumlah: int

class OrderCreate(BaseModel):
    item: List[DetailOrderCreate]

class OrderUpdateStatus(BaseModel):
    status_order:str

class DetailOrderResponse(BaseModel):
    id_detail_order: int
    id_produk: int
    jumlah :int
    subtotal: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id_order_produk: int
    id_user: int
    total_harga: float
    status_order: str

    class Config:
        from_attributes = True