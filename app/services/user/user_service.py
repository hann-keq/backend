from app.core.security import get_password_hash, verify_password
from app.repositories import user_repository
from app.schemas.pet_schema.pet_create import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def create_new_user(db: AsyncSession, user_data: UserCreate):
    #hashing
    hashed_password = get_password_hash(user_data.password)

    user_dict = user_data.model_dump()
    user_dict.pop("password")
    user_dict.pop("confirm_password")
    user_dict['password'] = hashed_password
    user = await user_repository.get_user_by_email(db, user_dict['email'])
    if user:
        raise ValueError("Email already registered")
    return await user_repository.create_user(db, user_dict)

async def login_user(db: AsyncSession, user_login_data: dict):
    user = await user_repository.get_user_by_email(db, user_login_data['email'])

    if not user:
        return None

    if not verify_password(user_login_data['password'], user.password):
        return None

    return user

async def add_pet(db: AsyncSession, user_id: int, pet_data: dict):
    pet_dict = pet_data.model_dump()
    pet_dict['user_id'] = user_id
    return await user_repository.create_pet(db, pet_dict)