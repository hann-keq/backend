from select import select

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Pet

async def create_pet(db: AsyncSession, pet_data: dict):
    new_pet = Pet(**pet_data)
    db.add(new_pet)
    await db.commit()
    await db.refresh(new_pet)
    return new_pet

async def get_pet_by_id(db: AsyncSession, pet_id: int):
    result = await db.execute(select(Pet).where(Pet.id_pet == pet_id))
    return result.scalars().one_or_none()

async def get_pets_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Pet).where(Pet.user_id == user_id))
    return result.scalars().all()

async def update_pet(db: AsyncSession, pet_id: int, pet_data: dict):
    result = await db.execute(select(Pet).where(Pet.id_pet == pet_id))
    pet = result.scalars().one_or_none()
    if not pet:
        return None
    for key, value in pet_data.items():
        setattr(pet, key, value)
    await db.commit()
    await db.refresh(pet)
    return pet

async def get_all_user_pets(db: AsyncSession, user_id: int):
    result = await db.execute(select(Pet).where(Pet.user_id == user_id))
    return result.scalars().all()

async def delete_pet(db: AsyncSession, pet_id: int):
    result = await db.execute(select(Pet).where(Pet.id_pet == pet_id))
    pet = result.scalars().one_or_none()
    if not pet:
        return None
    await db.delete(pet)
    await db.commit()
    return pet
