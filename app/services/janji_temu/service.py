from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import janji_temu_repository as janji
from app.schemas.janji_schema.schema import JanjiTemuCreate, JanjiTemuUpdateStatus
from app.exceptions import system_exceptions,user_exceptions

async def create_janji_temu(db: AsyncSession, janji_temu_data: JanjiTemuCreate):
    try:
        new_janji_temu = await janji.create_janji_temu(db, janji_temu_data.dict())
        return new_janji_temu
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def get_janji_temu_by_id(db: AsyncSession, janji_temu_id: int):
    janji_temu = await janji.get_janji_temu_by_id(db, janji_temu_id)
    if not janji_temu:
        raise user_exceptions.handle_janji_temu_not_found(f"Janji Temu dengan ID {janji_temu_id} tidak ditemukan")
    return janji_temu

async def get_all_janji_temu_by_user(db: AsyncSession, user_id: int):
    janji_temus = await janji.get_all_janji_temu_by_user(db, user_id)
    if not janji_temus:
        janji_temus = []  # Return an empty list instead of raising an exception
    return janji_temus

async def update_status_janji_temu(db: AsyncSession, janji_temu_id: int, status: str):
    try:
        updated_janji_temu = await janji.update_status_janji_temu(db, janji_temu_id, status)
        if not updated_janji_temu:
            raise user_exceptions.handle_janji_temu_not_found(f"Janji Temu dengan ID {janji_temu_id} tidak ditemukan")
        return updated_janji_temu
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def delete_janji_temu(db: AsyncSession, janji_temu_id: int):
    try:
        deleted_janji_temu = await janji.delete_janji_temu(db, janji_temu_id)
        if not deleted_janji_temu:
            raise user_exceptions.handle_janji_temu_not_found(f"Janji Temu dengan ID {janji_temu_id} tidak ditemukan")
        return deleted_janji_temu
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))