from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Dokter

async def create_dokter(db: AsyncSession, dokter_data: dict):
    new_dokter = Dokter(**dokter_data)
    db.add(new_dokter)
    await db.commit()
    await db.refresh(new_dokter)
    return new_dokter

async def get_dokter_by_id(db: AsyncSession, dokter_id: int):
    result = await db.execute(select(Dokter).where(Dokter.id_dokter == dokter_id))
    return result.scalars().one_or_none()

async def get_all_dokters_by_partner_id(db: AsyncSession, partner_id: int):
    result = await db.execute(select(Dokter).where(Dokter.id_partner == partner_id))
    return result.scalars().all()

async def get_dokter_by_partner_id(db: AsyncSession, partner_id: int):
    result = await db.execute(select(Dokter).where(Dokter.id_partner == partner_id))
    return result.scalars().one_or_none()

async def get_dokter_by_spesialis(db: AsyncSession, spesialis: str):
    result = await db.execute(select(Dokter).where(Dokter.spesialis == spesialis))
    return result.scalars().all()

async def update_dokter(db: AsyncSession, dokter_id: int, dokter_data: dict):
    result = await db.execute(select(Dokter).where(Dokter.id_dokter == dokter_id))
    dokter = result.scalars().one_or_none()
    if not dokter:
        return None
    for key, value in dokter_data.items():
        setattr(dokter, key, value)
    await db.commit()
    await db.refresh(dokter)
    return dokter

async def delete_dokter(db: AsyncSession, dokter_id: int):
    result = await db.execute(select(Dokter).where(Dokter.id_dokter == dokter_id))
    dokter = result.scalars().one_or_none()
    if not dokter:
        return None
    await db.delete(dokter)
    await db.commit()
    return dokter
