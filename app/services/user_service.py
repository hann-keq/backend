from app.core.security import get_password_hash, verify_password
from app.repositories import user_repository
from app.schemas.schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def create_new_user(db: AsyncSession, user_data: UserCreate):
    #hashing
    hashed_password = get_password_hash(user_data.password)

    user_dict = user_data.model_dump()
    user_dict.pop("password")
    user_dict.pop("verify_password")
    user_dict['password'] = hashed_password

    return await user_repository.create_user(db, user_dict)




