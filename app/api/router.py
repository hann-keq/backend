from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.models.models import User, Task
from app.schemas.schemas import UserCreate, UserResponse, TaskCreate, TaskResponse, TaskWithUserResponse
from sqlalchemy import select
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.models import Task
from sqlalchemy.orm import selectinload

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_user = User(name=user.name, email=user.email)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

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

@router.post("/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_task = Task(**task.dict())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskWithUserResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
             select(Task)
             .options(selectinload(Task.user))
            .where(Task.id == task_id)
        )

        task = result.scalars().first()
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))