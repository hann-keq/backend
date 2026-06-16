from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import JanjiTemu
from sqlalchemy import select

async def create_janji_temu(db: AsyncSession, janji_temu_data: dict):
    new_janji_temu = JanjiTemu(**janji_temu_data)
    db.add(new_janji_temu)
    await db.commit()
    await db.refresh(new_janji_temu)
    return new_janji_temu

async def get_janji_temu_by_id(db: AsyncSession, janji_temu_id: int):
    result = await db.execute(select(JanjiTemu).where(JanjiTemu.id_janji_temu == janji_temu_id))
    return result.scalars().one_or_none()

async def get_janji_temus_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(JanjiTemu).where(JanjiTemu.id_user == user_id))
    return result.scalars().all()

async def update_status_janji_temu(db: AsyncSession, janji_temu_id: int, status: str):
    result = await db.execute(select(JanjiTemu).where(JanjiTemu.id_janji_temu == janji_temu_id))
    janji_temu = result.scalars().one_or_none()
    if not janji_temu:
        return None
    janji_temu.status_janji_temu = status
    await db.commit()
    await db.refresh(janji_temu)
    return janji_temu

async def delete_janji_temu(db: AsyncSession, janji_temu_id: int):
    result = await db.execute(select(JanjiTemu).where(JanjiTemu.id_janji_temu == janji_temu_id))
    janji_temu = result.scalars().one_or_none()
    if not janji_temu:
        return None
    await db.delete(janji_temu)
    await db.commit()
    return janji_temu
