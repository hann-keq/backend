from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Produk

async def create_product(db: AsyncSession, product_data: dict):
    new_product = Produk(**product_data)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    return result.scalars().one_or_none()

async def get_all_products(db: AsyncSession):
    result = await db.execute(select(Produk))
    return result.scalars().all()

async def update_product_by_id_product(db: AsyncSession, product_id: int, product_data: dict):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    product = result.scalars().one_or_none()
    if not product:
        return None
    for key, value in product_data.items():
        setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    return product

async def delete_product_by_id_product(db: AsyncSession, product_id: int):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    product = result.scalars().one_or_none()
    if not product:
        return None
    await db.delete(product)
    await db.commit()
    return product

async def reduce_stock_product_by_id_product(db: AsyncSession, product_id: int, quantity: int):
    result = await db.execute(select(Produk).where(Produk.id_produk == product_id))
    product = result.scalars().one_or_none()
    if not product:
        return None
    if product.stok < quantity:
        return None
    product.stok -= quantity
    await db.commit()
    await db.refresh(product)
    return product
