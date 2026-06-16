from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import alamat_repository
from app.schemas.alamat_schema.schema import AlamatCreate, AlamatUpdate
from app.exceptions import user_exceptions, system_exceptions

async def create_new_alamat(db: AsyncSession, alamat_data: AlamatCreate, user_id: int):
    alamat_dict = alamat_data.model_dump()
    alamat_dict['id_user'] = user_id
    return await alamat_repository.create_alamat(db, alamat_dict)

async def get_alamat_by_id(db: AsyncSession, alamat_id: int):
    alamat = await alamat_repository.get_alamat_by_id(db, alamat_id)
    if not alamat:
        raise user_exceptions.handle_alamat_not_found(detail_message=f'Alamat pengguna dengan ID {alamat_id} tidak ditemukan')
    return alamat

async def get_alamats_by_user(db: AsyncSession, user_id: int):
    return await alamat_repository.get_alamats_by_user(db, user_id)

async def update_alamat(db: AsyncSession, alamat_id: int, alamat_data: AlamatUpdate):
    updated_alamat = await alamat_repository.update_alamat(db, alamat_id, alamat_data.model_dump(exclude_unset=True))
    if not updated_alamat:
        raise user_exceptions.handle_alamat_not_found(detail_message=f'Alamat pengguna dengan ID {alamat_id} tidak ditemukan')
    return updated_alamat

async def delete_alamat(db: AsyncSession, alamat_id: int):
    deleted_alamat = await alamat_repository.delete_alamat(db, alamat_id)
    if not deleted_alamat:
        raise user_exceptions.handle_alamat_not_found(detail_message=f'Alamat pengguna dengan ID {alamat_id} tidak ditemukan')
    return deleted_alamat