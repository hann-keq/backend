from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.partner_schema.schema import PartnerCreate
from app.repositories import partner_repository

async def add_partner(db: AsyncSession,partner_data: PartnerCreate):
    partner_dict = partner_data.model_dump()
    return await partner_repository.add_partner(db,partner_dict)