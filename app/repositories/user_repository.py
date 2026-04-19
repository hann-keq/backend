from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Pet, User

async def create_user(db: AsyncSession, user_data: dict) :
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().one_or_none()

async def create_pet(db: AsyncSession, pet_data: dict):
    new_pet = Pet(**pet_data)
    db.add(new_pet)
    await db.commit()
    await db.refresh(new_pet)
    return new_pet