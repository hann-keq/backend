from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.system_exceptions import HTTPException
from app.repositories import pet_repository
from app.schemas.pet_schema.pet_create import PetCreate
# from app.repositories import 
async def add_pet(db: AsyncSession, user_id: int, pet_data: PetCreate):
    pet_dict = pet_data.model_dump()
    pet_dict['id_user'] = user_id
    # Pydantic field is 'foto_hewan', DB column is 'foto'
    if 'foto_hewan' in pet_dict:
        pet_dict['foto'] = pet_dict.pop('foto_hewan')
    return await pet_repository.create_pet(db, pet_dict)

async def update_pet(db: AsyncSession, user_id: int, pet_id: int, pet_data: PetCreate):
    try:
        existing_pet = await pet_repository.get_pet_by_id(db, pet_id)
        if not existing_pet or existing_pet.id_user != user_id:
            raise HTTPException(status_code=404, detail='Pet not found')
        pet_dict = pet_data.model_dump(exclude={'id_user'})
        return await pet_repository.update_pet(db, pet_id, pet_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def delete_pet(db: AsyncSession, user_id: int, pet_id: int):
    try:
        existing_pet = await pet_repository.get_pet_by_id(db, pet_id)
        if not existing_pet or existing_pet.id_user != user_id:
            raise HTTPException(status_code=404, detail='Pet not found')
        return await pet_repository.delete_pet(db, pet_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_all_user_pets(db: AsyncSession, user_id: int):
    pet = await pet_repository.get_all_user_pets(db, user_id)
    if pet is None:
        raise HTTPException(status_code=404, detail='No pets found for this user')
    return pet