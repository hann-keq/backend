from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import decode_access_token, bearer_scheme,oauth,hash_password,create_access_token
from app.repositories.user_repository import get_user_by_id,get_user_by_email,create_user
from app.core.database import get_db
from app.exceptions import user_exceptions, system_exceptions


async def google_authorize(request: Request,callback_url: str):
    redirect_uri = request.url_for(callback_url)
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def access_token_oauth(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve user information from Google.",
        )
    email = user_info.get("email")

    user = await get_user_by_email(db, email)

    if not user:
        hash_pass = hash_password("google_oauth_user")  # Placeholder password for OAuth users
        user = await create_user(db, {
            "email": email,
            "password": hash_pass,
            "role": "User",
            "nama": user_info.get("name") or "Google User",
            "no_telepon": "0000000000",
            "foto": user_info.get("picture") or "default_picture",
        })

    # "sub" is what get_current_user decodes; user_id gets auto-mapped to "sub"
    jwt_token = create_access_token(data={"sub": str(user.id_user)})
    return jwt_token

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
