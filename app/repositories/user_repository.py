from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User

async def create_user(db: AsyncSession, user_data: dict) :
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().one_or_none()