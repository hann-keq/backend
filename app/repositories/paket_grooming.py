from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import DetailPaketGrooming,PaketGrooming
from sqlalchemy import select

async def create_paket_grooming(db: AsyncSession, paket_data: dict):
    new_paket = PaketGrooming(**paket_data)
    db.add(new_paket)
    await db.commit()
    await db.refresh(new_paket)
    return new_paket

async def get_paket_grooming_by_id(db: AsyncSession, paket_id: int):
    result = await db.execute(select(PaketGrooming).where(PaketGrooming.id_paket_grooming == paket_id))
    return result.scalars().one_or_none()

async def get_all_paket_grooming(db: AsyncSession):
    result = await db.execute(select(PaketGrooming))
    return result.scalars().all()

async def create_detail_paket_grooming(db: AsyncSession, detail_data: dict):
    new_detail = DetailPaketGrooming(**detail_data)
    db.add(new_detail)
    await db.commit()
    await db.refresh(new_detail)
    return new_detail

async def get_detail_paket_grooming_by_partner_id(db: AsyncSession, partner_id: int):
    result = await db.execute(select(DetailPaketGrooming).where(DetailPaketGrooming.id_partner == partner_id))
    return result.scalars().one_or_none()

async def get_all_details_by_paket(db: AsyncSession, paket_id: int):
    result = await db.execute(select(DetailPaketGrooming).where(DetailPaketGrooming.id_paket_grooming == paket_id))
    return result.scalars().all()

async def update_paket_grooming(db: AsyncSession, paket_id: int, paket_data: dict):
    result = await db.execute(select(PaketGrooming).where(PaketGrooming.id_paket_grooming == paket_id))
    paket = result.scalars().one_or_none()
    if not paket:
        return None
    for key, value in paket_data.items():
        setattr(paket, key, value)
    await db.commit()
    await db.refresh(paket)
    return paket

async def delete_paket_grooming(db: AsyncSession, paket_id: int):
    #delete detail abis itu hapus paketnya
    result = await db.execute(select(DetailPaketGrooming).where(DetailPaketGrooming.id_paket_grooming == paket_id))
    detail = result.scalars().all()
    if not detail:
        return None
    for item in detail:
        await db.delete(item)
    result = await db.execute(select(PaketGrooming).where(PaketGrooming.id_paket_grooming == paket_id))
    paket = result.scalars().one_or_none()
    if not paket:
        return None
    await db.delete(paket)
    await db.commit()
    return paket

