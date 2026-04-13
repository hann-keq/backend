from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models.models import User

async def create_user(db: AsyncSession, user_data: dict) :
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user