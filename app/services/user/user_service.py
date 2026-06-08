from app.core.security import hash_password, verify_password
from app.repositories import user_repository
from app.schemas.user_schema.user_create import UserCreate,AdminCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import user_exceptions, system_exceptions
from fastapi import Depends
from app.core.auth import verify_token
from app.core.database import get_db


async def create_new_user(db: AsyncSession, user_data: UserCreate):
    #hashing
    hashed_password = hash_password(user_data.password)

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

async def create_new_admin(db:AsyncSession, admin_data: AdminCreate):
    hashed_password = hash_password(admin_data.password)

    admin_dict = admin_data.model_dump()
    admin_dict.pop("password")
    admin_dict.pop("confirm_password")
    admin_dict['password'] = hashed_password
    admin = await user_repository.get_admin_by_email_and_role(db,admin_dict['email'],admin_dict['role'])
    if admin:
        raise user_exceptions.handle_user_already_exists()
    return await user_repository.create_user(db, admin_dict)

async def login_admin(db:AsyncSession,admin_login_data:dict):
    admin_dump = admin_login_data.model_dump()
    admin = await user_repository.get_admin_by_email_and_role(db,admin_dump['email'],admin_dump['role'])
    if not admin:
        return user_exceptions.handle_user_not_found(detail_message='Admin not found')
    if not verify_password(admin_dump['password'], admin.password):
        return user_exceptions.handle_invalid_email_or_password()
    return admin

async def get_user_by_id(db: AsyncSession, user_id: int):
    user = await user_repository.get_user_by_id(db, user_id)
    if not user:
        raise user_exceptions.handle_user_not_found(detail_message=f'User with ID {user_id} not found')
    return user

async def get_current_admin_by_id(admin_id: int, db: AsyncSession = Depends(get_db)):
    try:
        admin = await user_repository.get_admin_by_id(db, admin_id)
        if not admin:
            system_exceptions.handle_non_authorized_token(Exception('Admin not found'))
        return admin
    except Exception as e:
        system_exceptions.handle_system_error(e)