from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import favorit_repository as favorit
from app.schemas.favorit_schema import schema as favorit_schema
from app.exceptions import system_exceptions,user_exceptions

async def toggle_favorit(db: AsyncSession, user_id: int, produk_id: int):
    try:
        existing_favorit = await favorit.check_favorit_exists(db, user_id, produk_id)
        if existing_favorit:
            deleted_favorit = await favorit.delete_favorit(db, existing_favorit.id_favorit, user_id)
            return {"message": "Produk dihapus dari favorit", "favorit": deleted_favorit}
        else:
            new_favorit_data = {
                "id_user": user_id,
                "id_produk": produk_id
            }
            new_favorit = await favorit.create_favorit(db, new_favorit_data)
            return {"message": "Produk ditambahkan ke favorit", "favorit": new_favorit}
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def get_favorit_by_user(db: AsyncSession, user_id: int):
    favorit_list = await favorit.get_all_user_favorits(db, user_id)
    if not favorit_list:
        raise user_exceptions.handle_favorit_not_found(f"Favorit untuk User ID {user_id} tidak ditemukan")
    return favorit_list

