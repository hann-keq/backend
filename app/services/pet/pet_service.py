from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import pet_repository
from app.schemas.pet_schema.pet_create import PetCreate
# from app.repositories import 
async def add_pet(db: AsyncSession, user_id: int, pet_data: PetCreate):
    pet_dict = pet_data.model_dump()
    pet_dict['id_user'] = user_id
    return await pet_repository.create_pet(db, pet_dict)