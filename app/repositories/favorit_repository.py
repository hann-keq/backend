from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Favorit
from sqlalchemy import select

async def create_favorit(db: AsyncSession, favorit_data: dict):
    new_favorit = Favorit(**favorit_data)
    db.add(new_favorit)
    await db.commit()
    await db.refresh(new_favorit)
    return new_favorit

async def get_favorit_by_id(db: AsyncSession, favorit_id: int):
    result = await db.execute(select(Favorit).where(Favorit.id_favorit == favorit_id))
    return result.scalars().one_or_none()

async def get_all_user_favorits(db: AsyncSession, user_id: int):
    result = await db.execute(select(Favorit).where(Favorit.id_user == user_id))
    return result.scalars().all()

async def check_favorit_exists(db: AsyncSession, user_id: int, id_produk: int):
    result = await db.execute(
        select(Favorit).where(Favorit.id_user == user_id, Favorit.id_produk == id_produk)
    )
    return result.scalars().one_or_none()

async def delete_favorit(db: AsyncSession, favorit_id: int,user_id: int):
    result = await db.execute(select(Favorit).where(Favorit.id_favorit == favorit_id, Favorit.id_user == user_id))
    favorit = result.scalars().one_or_none()
    if not favorit:
        return None
    await db.delete(favorit)
    await db.commit()
    return favorit

