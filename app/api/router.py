from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.auth import get_current_user

from app.models.models import User
from app.services.pet.pet_service import add_pet
from app.exceptions import user_exceptions, system_exceptions
from app.schemas.pet_schema.pet_create import PetCreate
from app.schemas.pet_schema.pet_response import PetResponse
from app.schemas.user_schema.user_create import UserCreate, UserLogin,AdminCreate
from app.schemas.user_schema.user_response import UserResponse, UserResponseOnlyId
from sqlalchemy import select


from app.services.user.user_service import create_new_user, login_user, login_admin,create_new_admin,get_user_by_id

router = APIRouter()

@router.post("/register/", response_model=UserResponse)
async def sign_up(new_user : UserCreate, db:AsyncSession = Depends(get_db)):
    return await create_new_user(db, new_user)

@router.post('/login')
async def login(user_login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await login_user(db, user_login_data.model_dump())

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(
        data={"sub": str(user.id_user)
              })
    print(access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        
    }


@router.get("/users/{user_id}", response_model=UserResponseOnlyId)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
    )
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/users/{user_id}/pets/add', response_model=PetResponse)
async def add_user_new_pet(pet_data: PetCreate, db:AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user)):
    try: 
        print(f'User id = {user_id.id_user}')
        pet = await add_pet(db,user_id.id_user,pet_data)
        print(f'Pet added: {pet}')
        return pet
    except Exception as e:
        system_exceptions.handle_system_error(e)

@router.post('/admin/login')
async def admin_login(admin_login_data: AdminCreate,db:AsyncSession = Depends(get_db) ):
    try:
        admin = await login_admin(db,admin_login_data)
        if not admin:
            return user_exceptions.handle_user_not_found(detail_message='Admin not found')
        access_token = create_access_token(data={"sub": str(admin.id_user)})
        return {
            'access_token': access_token,
            'type':'bearer'
        }
    except Exception as e:
        system_exceptions.handle_system_error(e)

@router.post('/admin/register', response_model=UserResponse)
async def register_admin(admin_data: AdminCreate, db:AsyncSession = Depends(get_db)):
    try:
        admin = await create_new_admin(db, admin_data)
        return admin
    except Exception as e:
        system_exceptions.handle_system_error(e)

    