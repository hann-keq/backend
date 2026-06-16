from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import paket_grooming as grooming
from app.schemas.paket_schema.schema import PakeGroomingCreate,PaketGroomingUpdate
from app.exceptions import system_exceptions,user_exceptions

async def create_paket_grooming(db: AsyncSession, paket_data: PakeGroomingCreate):
    try:
        new_paket = await grooming.create_paket_grooming(db, paket_data.dict())
        return new_paket
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def get_paket_grooming_by_id(db: AsyncSession, paket_id: int):
    paket_grooming = await grooming.get_paket_grooming_by_id(db, paket_id)
    if not paket_grooming:
        raise user_exceptions.handle_booking_grooming_not_found(f"Paket Grooming dengan ID {paket_id} tidak ditemukan")
    return paket_grooming

async def get_all_paket_grooming(db: AsyncSession):
    paket_grooming_list = await grooming.get_all_paket_grooming(db)
    if not paket_grooming_list:
        raise user_exceptions.handle_booking_grooming_not_found("Tidak ada Paket Grooming yang ditemukan")
    return paket_grooming_list

async def update_paket_grooming(db: AsyncSession, paket_id: int, paket_data: PaketGroomingUpdate):
    try:
        updated_paket = await grooming.update_paket_grooming(db, paket_id, paket_data.dict(exclude_unset=True))
        if not updated_paket:
            raise user_exceptions.handle_booking_grooming_not_found(f"Paket Grooming dengan ID {paket_id} tidak ditemukan")
        return updated_paket
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))

async def delete_paket_grooming(db: AsyncSession, paket_id: int):
    try:
        deleted_paket = await grooming.delete_paket_grooming(db, paket_id)
        if not deleted_paket:
            raise user_exceptions.handle_booking_grooming_not_found(f"Paket Grooming dengan ID {paket_id} tidak ditemukan")
        return deleted_paket
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
