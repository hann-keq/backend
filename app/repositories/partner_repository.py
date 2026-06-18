from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Partner

async def add_partner(db: AsyncSession, partner_data: dict):
    new_partner = Partner(**partner_data)
    db.add(new_partner)
    await db.commit()
    await db.refresh(new_partner)
    return new_partner

async def get_partner_by_id(db: AsyncSession, partner_id: int):
    result = await db.execute(select(Partner).where(Partner.id_partner == partner_id))
    return result.scalars().one_or_none()

async def get_all_partners(db: AsyncSession):
    result = await db.execute(select(Partner))
    return result.scalars().all()

async def update_partner(db: AsyncSession, partner_id: int, partner_data: dict):
    result = await db.execute(select(Partner).where(Partner.id_partner == partner_id))
    partner = result.scalars().one_or_none()
    if not partner:
        return None
    for key, value in partner_data.items():
        setattr(partner, key, value)
    await db.commit()
    await db.refresh(partner)
    return partner

async def delete_partner(db: AsyncSession, partner_id: int):
    result = await db.execute(select(Partner).where(Partner.id_partner == partner_id))
    partner = result.scalars().one_or_none()
    if not partner:
        return None
    await db.delete(partner)
    await db.commit()
    return partner
