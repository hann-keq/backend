from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import decode_access_token, bearer_scheme
from app.repositories.user_repository import get_user_by_id
from app.core.database import get_db
from app.exceptions import user_exceptions, system_exceptions


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    """
    Dependency that extracts and validates the JWT token.

    Looks in:
      1. Authorization: Bearer <token>  header  (mobile/API clients)
      2. access_token cookie                     (Jinja browser forms)

    FastAPI's OpenAPI schema generation sees `bearer_scheme` in the
    dependency chain → protected routes get the 🔒 lock icon in /docs.
    """
    token = None

    # 1. Authorization header (standard Bearer)
    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        # 2. Cookie (browser / Jinja forms)
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Clean "Bearer " prefix if it leaked into the cookie value
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")

        if not payload or not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await get_user_by_id(db, int(user_id))
        if not user:
            user_exceptions.handle_user_not_found(detail_message="User not found")

        return user

    except ExpiredSignatureError:
        system_exceptions.handle_expire_token(Exception("Token expired"))

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token format is invalid or corrupted. Please login again.",
        )

    except Exception as e:
        system_exceptions.handle_system_error(e)
