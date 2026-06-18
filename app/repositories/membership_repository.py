from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Membership
from sqlalchemy import select

async def create_membership(db: AsyncSession, membership_data: dict):
    new_membership = Membership(**membership_data)
    db.add(new_membership)
    await db.commit()
    await db.refresh(new_membership)
    return new_membership

async def get_membership_by_id(db: AsyncSession, membership_id: int):
    result = await db.execute(select(Membership).where(Membership.id_membership == membership_id))
    return result.scalars().one_or_none()

async def get_membership_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Membership).where(Membership.id_user == user_id))
    return result.scalars().one_or_none()

async def update_membership_dates(db: AsyncSession, membership_id: int, data: dict):
    """Update membership fields — used by both select and cancel routes."""
    result = await db.execute(select(Membership).where(Membership.id_membership == membership_id))
    membership = result.scalars().one_or_none()
    if not membership:
        return None
    for key, value in data.items():
        setattr(membership, key, value)
    await db.commit()
    await db.refresh(membership)
    return membership

async def delete_membership(db: AsyncSession, membership_id: int):
    result = await db.execute(select(Membership).where(Membership.id_membership == membership_id))
    membership = result.scalars().one_or_none()
    if not membership:
        return None
    await db.delete(membership)
    await db.commit()
    return membership

async def transfer_membership(db: AsyncSession, membership_id: int, new_user_id: int):
    result = await db.execute(select(Membership).where(Membership.id_membership == membership_id))
    membership = result.scalars().one_or_none()
    if not membership:
        return None
    membership.id_user = new_user_id
    await db.commit()
    await db.refresh(membership)
    return membership
