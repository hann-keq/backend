from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Partner

async def add_partner(db:AsyncSession,partner_data:dict):
    new_partner = Partner(**partner_data)
    db.add(new_partner)
    await db.commit()
    await db.refresh(new_partner)
    return new_partner