from sqlalchemy.ext.asyncio import async_session
from app.repositories import produk_repository
from app.schemas.product_schema import schema

async def add_product(db: async_session, product_data: schema.ProductCreate):
    product_dict = product_data.model_dump()
    return await produk_repository.create_product(db,product_dict)