from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import dokter_repository as dokter
from app.schemas.dockter_schema.schema import DokterCreate, DokterUpdate
from app.exceptions import system_exceptions,user_exceptions

async def create_dokter(db: AsyncSession, dokter_data: DokterCreate):
    try:
        new_dokter = await dokter.create_dokter(db, dokter_data.model_dump())
        return new_dokter
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def get_dokter_by_id(db: AsyncSession, dokter_id: int):
    dokter_data = await dokter.get_dokter_by_id(db, dokter_id)
    if not dokter_data:
        raise user_exceptions.handle_dokter_not_found(f"Dokter dengan ID {dokter_id} tidak ditemukan")
    return dokter_data

async def get_all_dokter_by_partner_id(db: AsyncSession, partner_id: int):
    dokter_list = await dokter.get_all_dokters_by_partner_id(db, partner_id)
    if not dokter_list:
        raise user_exceptions.handle_dokter_not_found("Tidak ada Dokter yang ditemukan")
    return dokter_list

async def update_dokter(db: AsyncSession, dokter_id: int, dokter_data: DokterUpdate):
    try:
        updated_dokter = await dokter.update_dokter(db, dokter_id, dokter_data.model_dump(exclude_unset=True))
        if not updated_dokter:
            raise user_exceptions.handle_dokter_not_found(f"Dokter dengan ID {dokter_id} tidak ditemukan")
        return updated_dokter
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def delete_dokter(db: AsyncSession, dokter_id: int):
    try:
        deleted_dokter = await dokter.delete_dokter(db, dokter_id)
        if not deleted_dokter:
            raise user_exceptions.handle_dokter_not_found(f"Dokter dengan ID {dokter_id} tidak ditemukan")
        return deleted_dokter
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))