from fastapi import Form
from pydantic import BaseModel

class ProductBase(BaseModel):
    id_produk: int
    nama_produk : str
    harga: int
    stok : int
    # deskripsi: str
    gambar : str | None

class ProductCreate(BaseModel):
    nama_produk : str
    harga: int
    stok : int
    # deskripsi: str
    gambar : str | None

    @classmethod
    def as_form(cls,nama_produk: str = Form(...), harga: int = Form(...), stok: int = Form(...), gambar: str = Form(None)):
        return cls(nama_produk=nama_produk, harga=harga, stok=stok, gambar=gambar)

class ProductResponse(ProductBase):
    pass
    class Config:
        from_attributes = True