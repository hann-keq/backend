from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.auth import get_current_user
from app.models.models import User
from app.schemas.pet_schema.pet_create import PetCreate, UserCreate, UserLogin, UserResponse
from sqlalchemy import select


from app.services.user.user_service import add_pet, create_new_user, login_user

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
        data={"sub": str(user.id)
              })
    print(access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
    )
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post('/add_pet', response_model=UserResponse)
async def add_user_pet(new_pet: PetCreate, db: AsyncSession = Depends(get_db), current_user:User =Depends(get_current_user)):
    return await add_pet(db,current_user.id,new_pet)