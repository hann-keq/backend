from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import membership_repository as membership
from app.schemas.membership_schema import schema as membership_schema
from app.exceptions import system_exceptions,user_exceptions

async def create_membership(db: AsyncSession, user_id: int, membership_data: membership_schema.MembershipCreate):
    try:
        new_membership = await membership.create_membership(db, membership_data.model_dump())
        new_membership['id_user'] = user_id
        return new_membership
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def edit_membership(db: AsyncSession, user_id: int, membership_data: membership_schema.MembershipUpdate):
    try:
        updated_membership = await membership.update_membership(db, user_id, membership_data.model_dump(exclude_unset=True))
        if not updated_membership:
            raise user_exceptions.handle_membership_not_found(f"Membership untuk User ID {user_id} tidak ditemukan")
        return updated_membership
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))
    
async def delete_membership(db: AsyncSession, user_id: int):
    try:
        deleted_membership = await membership.delete_membership(db, user_id)
        if not deleted_membership:
            raise user_exceptions.handle_membership_not_found(f"Membership untuk User ID {user_id} tidak ditemukan")
        return deleted_membership
    except Exception as e:
        raise system_exceptions.DatabaseError(str(e))