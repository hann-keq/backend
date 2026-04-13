from sqlalchemy import select
from app.models.models import Task


async def get_tasks_by_user(db,user_id: int):
    result = await db.execute(
        select(Task).where(Task.user_id == user_id)
    )
    return result.scalars().all()

