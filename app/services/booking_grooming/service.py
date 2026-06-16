from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import booking_repository as booking
from app.schemas.booking_schema.schema import BookingCreate,BookingUpdateStatus
from app.exceptions import system_exceptions,user_exceptions

async def create_booking_grooming(db: AsyncSession, booking_data: BookingCreate):
    try:
        new_booking = await booking.create_booking_grooming(db, booking_data.dict())
        return new_booking
    except Exception as e:
        raise system_exceptions.handle_system_error(str(e))
    
async def get_booking_grooming_by_id(db: AsyncSession, booking_id: int):
    booking_grooming = await booking.get_booking_grooming_by_id(db, booking_id)
    if not booking_grooming:
        raise user_exceptions.handle_booking_grooming_not_found(f"Booking Grooming dengan ID {booking_id} tidak ditemukan")
    return booking_grooming

async def get_bookings_grooming_by_user(db: AsyncSession, user_id: int):
    bookings_grooming = await booking.get_bookings_grooming_by_user(db, user_id)
    if not bookings_grooming:
        raise user_exceptions.handle_booking_grooming_not_found(f"Booking Grooming untuk User ID {user_id} tidak ditemukan")
    return bookings_grooming

async def update_status_booking_grooming(db: AsyncSession, booking_id: int, status: str):
    try:
        updated_booking = await booking.update_booking_grooming(db, booking_id, status)
        if not updated_booking:
            raise user_exceptions.handle_booking_grooming_not_found(f"Booking Grooming dengan ID {booking_id} tidak ditemukan")
        return updated_booking
    except Exception as e:
        raise system_exceptions.handle_system_error(str(e))
    
async def delete_booking_grooming(db: AsyncSession, booking_id: int):
    try:
        deleted_booking = await booking.delete_booking_grooming(db, booking_id)
        if not deleted_booking:
            raise user_exceptions.handle_booking_grooming_not_found(f"Booking Grooming dengan ID {booking_id} tidak ditemukan")
        return deleted_booking
    except Exception as e:
        raise system_exceptions.handle_system_error(str(e))
