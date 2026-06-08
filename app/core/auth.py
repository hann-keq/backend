from jose import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,HTTPException, Request
from app.core.security import decode_access_token
from app.repositories.user_repository import get_user_by_id,get_admin_by_email_and_role
from app.core.database import get_db
from app.exceptions import user_exceptions,system_exceptions
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials




security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = decode_access_token(credentials.credentials)
        user_id : str = payload.get('sub')
        if not payload or not user_id:
            raise HTTPException(status_code=401,detail='Invalid token')
        return user_id
    except ExpiredSignatureError as e:
        system_exceptions.handle_expire_token(e)
        

async def get_current_user(user_id:str = Depends(verify_token),db:AsyncSession = Depends(get_db)):
    try:
        user = await get_user_by_id(db, int(user_id))    
        return user
    except Exception as e:
        user_exceptions.handle_user_not_found(detail_message='User not found')


async def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

async def get_current_user_from_cookie(token: str = Depends(get_token_from_cookie), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if not payload or not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await get_user_by_id(db, int(user_id))
        return user
    except ExpiredSignatureError as e:
        system_exceptions.handle_expire_token(e)


