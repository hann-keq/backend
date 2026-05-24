from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from starlette import status
from starlette.exceptions import HTTPException
from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import get_user_by_id
o_auth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(db: AsyncSession = Depends(get_db),token: str = Depends(o_auth2_scheme)):
    payload = decode_access_token(token)
    print(token)
    print("Decoded token payload:", payload)  # Debugging statement
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user
