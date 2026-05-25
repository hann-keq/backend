from app.models.models import Produk
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def create_product(db:AsyncSession,product_data:dict):
    new_product = Produk(**product_data)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

async def get_product_by_id(db:AsyncSession,product_id:int):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    return result.scalars().one_or_none()

