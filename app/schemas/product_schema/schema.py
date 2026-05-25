from pydantic import BaseModel

class ProductBase(BaseModel):
    id_produk: int
    nama_produk : str
    harga: int
    stok : int
    # deskripsi: str
    gambar : str | None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    pass
    class Config:
        from_attributes = True