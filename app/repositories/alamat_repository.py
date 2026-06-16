from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Alamat
from sqlalchemy import select

async def create_alamat(db:AsyncSession,alamat_data:dict):
    new_alamat = Alamat(**alamat_data)
    db.add(new_alamat)
    await db.commit()
    await db.refresh(new_alamat)
    return new_alamat

async def get_alamat_by_id(db:AsyncSession,alamat_id:int):
    result = await db.execute(select(Alamat).where(Alamat.id_alamat == alamat_id))
    return result.scalars().one_or_none()

async def get_alamats_by_user(db:AsyncSession,user_id:int):
    result = await db.execute(select(Alamat).where(Alamat.id_user == user_id))
    return result.scalars().all()

async def update_alamat(db:AsyncSession,alamat_id:int,alamat_data:dict):
    result = await db.execute(select(Alamat).where(Alamat.id_alamat == alamat_id))
    alamat = result.scalars().one_or_none()
    if not alamat:
        return None
    for key, value in alamat_data.items():
        setattr(alamat, key, value)
    await db.commit()
    await db.refresh(alamat)
    return alamat

async def delete_alamat(db:AsyncSession,alamat_id:int):
    result = await db.execute(select(Alamat).where(Alamat.id_alamat == alamat_id))
    alamat = result.scalars().one_or_none()
    if not alamat:
        return None
    await db.delete(alamat)
    await db.commit()
    return alamat