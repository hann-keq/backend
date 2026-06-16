from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import OrderProduk,DetailOrder
from sqlalchemy import select

async def create_order_produk(db: AsyncSession, order_data: dict):
    new_order = OrderProduk(**order_data)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    return new_order

async def get_ordered_produk_by_id(db: AsyncSession, order_id: int):
    result = await db.execute(select(OrderProduk).where(OrderProduk.id_order == order_id))
    return result.scalars().one_or_none()

async def get_all_ordered_produk_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(OrderProduk).where(OrderProduk.id_user == user_id))
    return result.scalars().all()

async def create_detail_order(db: AsyncSession, detail_order_data: dict):
    new_detail_order = DetailOrder(**detail_order_data)
    db.add(new_detail_order)
    await db.commit()
    await db.refresh(new_detail_order)
    return new_detail_order

async def get_detail_order_by_id(db: AsyncSession, detail_order_id: int):
    result = await db.execute(select(DetailOrder).where(DetailOrder.id_detail_order == detail_order_id))
    return result.scalars().one_or_none()

async def get_detail_orders_by_order(db: AsyncSession, order_id: int):
    result = await db.execute(select(DetailOrder).where(DetailOrder.id_order == order_id))
    return result.scalars().all()

async def get_detail_user_order(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(DetailOrder).join(OrderProduk).where(OrderProduk.id_user == user_id)
    )
    return result.scalars().all()

async def update_status_order(db: AsyncSession, order_id: int, status: str):
    result = await db.execute(select(OrderProduk).where(OrderProduk.id_order == order_id))
    order = result.scalars().one_or_none()
    if not order:
        return None
    order.status_order = status
    await db.commit()
    await db.refresh(order)
    return order

async def delete_detail_and_order(db: AsyncSession, id_order: int):
    # hapus detail abis itu hapus ordernya
    result = await db.execute(
        select(DetailOrder).where(DetailOrder.id_order_produk == id_order)
        )
    for item in result.scalars().all():
        await db.delete(item)
    
    result = await db.execute(select(OrderProduk).where(OrderProduk.id_order == id_order))
    order = result.scalars().one_or_none()
    if order:
        await db.delete(order)
    await db.commit()
    return order

async def kurangi_stok_produk(db: AsyncSession, id_produk: int, jumlah: int):
    result = await db.execute(select(DetailOrder).where(DetailOrder.id_produk == id_produk))
    detail_orders = result.scalars().all()
    for detail in detail_orders:
        if detail.jumlah >= jumlah:
            detail.jumlah -= jumlah
            await db.commit()
            await db.refresh(detail)
            return detail
    return None



