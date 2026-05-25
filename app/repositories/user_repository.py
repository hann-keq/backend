from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.exceptions import system_exceptions
from app.models.models import  User

from fastapi import Depends
from app.core.database import get_db

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
    result = await db.execute(select(User).where(User.id_user == user_id))
    return result.scalars().one_or_none()

async def get_admin_by_email_and_role(db:AsyncSession,email:str,role:str):
    result = await db.execute(select(User).where(User.email == email,User.role == role))
    return result.scalars().one_or_none()

async def get_admin_by_id(db:AsyncSession,admin_id:int):
    result = await db.execute(select(User).where(User.id_user == admin_id,User.role == 'ADMIN'))
    return result.scalars().one_or_none()
