from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import BookingGrooming

async def create_booking_grooming(db: AsyncSession, booking_data: dict):
    new_booking = BookingGrooming(**booking_data)
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking

async def get_booking_grooming_by_id(db: AsyncSession, booking_id: int):
    result = await db.execute(select(BookingGrooming).where(BookingGrooming.id == booking_id))
    return result.scalars().one_or_none()

async def get_booking_groomings_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(BookingGrooming).where(BookingGrooming.id_user == user_id))
    return result.scalars().all()


async def update_booking_grooming(db: AsyncSession, booking_id: int, status: str):
    result = await db.execute(select(BookingGrooming).where(BookingGrooming.id == booking_id))
    booking = result.scalars().one_or_none()
    if not booking:
        return None
    booking.status_booking = status
    await db.commit()
    await db.refresh(booking)
    return booking

async def delete_booking_grooming(db: AsyncSession, booking_id: int):
    result = await db.execute(select(BookingGrooming).where(BookingGrooming.id == booking_id))
    booking = result.scalars().one_or_none()
    if not booking:
        return None
    await db.delete(booking)
    await db.commit()
    return booking