"""Server-side cart repository — one cart per user, persisted in DB."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Cart, CartItem


async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
    """Return the user's cart, creating one if it doesn't exist."""
    result = await db.execute(select(Cart).where(Cart.id_user == user_id))
    cart = result.scalars().one_or_none()
    if cart is None:
        cart = Cart(id_user=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart


async def get_cart_items(db: AsyncSession, cart_id: int) -> list[CartItem]:
    result = await db.execute(select(CartItem).where(CartItem.id_cart == cart_id))
    return list(result.scalars().all())


async def add_item(db: AsyncSession, cart_id: int, id_produk: int, jumlah: int = 1):
    """Add a product to cart, or increase quantity if already present."""
    result = await db.execute(
        select(CartItem).where(
            CartItem.id_cart == cart_id,
            CartItem.id_produk == id_produk,
        )
    )
    existing = result.scalars().one_or_none()
    if existing:
        existing.jumlah += jumlah
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        item = CartItem(id_cart=cart_id, id_produk=id_produk, jumlah=jumlah)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item


async def update_item_qty(db: AsyncSession, cart_id: int, id_produk: int, jumlah: int):
    result = await db.execute(
        select(CartItem).where(
            CartItem.id_cart == cart_id,
            CartItem.id_produk == id_produk,
        )
    )
    item = result.scalars().one_or_none()
    if item is None:
        return None
    if jumlah <= 0:
        await db.delete(item)
        await db.commit()
        return None  # removed
    item.jumlah = jumlah
    await db.commit()
    await db.refresh(item)
    return item


async def remove_item(db: AsyncSession, cart_id: int, id_produk: int):
    result = await db.execute(
        select(CartItem).where(
            CartItem.id_cart == cart_id,
            CartItem.id_produk == id_produk,
        )
    )
    item = result.scalars().one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
    return item


async def clear_cart(db: AsyncSession, cart_id: int):
    items = await get_cart_items(db, cart_id)
    for item in items:
        await db.delete(item)
    await db.commit()
