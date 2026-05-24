from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Pet

async def create_pet(db: AsyncSession, pet_data: dict):
    new_pet = Pet(**pet_data)
    db.add(new_pet)
    await db.commit()
    await db.refresh(new_pet)
    return new_pet