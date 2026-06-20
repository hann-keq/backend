from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.security import HTTPBearer
from authlib.integrations.starlette_client import OAuth
import bcrypt
from app.core.config import settings

# ---------------------------------------------------------------------------
# OpenAPI Security Scheme — registers the 🔒 lock icon on protected routes
# ---------------------------------------------------------------------------
bearer_scheme = HTTPBearer(
    auto_error=False,  # we handle 401 ourselves in auth.py
)

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    password_byte = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_byte, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_byte = plain_password.encode("utf-8")
    hashed_password_byte = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_password_byte, hashed_password_byte)


# ---------------------------------------------------------------------------
# JWT token creation / decoding
# ---------------------------------------------------------------------------
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires})
    if "user_id" in to_encode:
        to_encode["sub"] = str(to_encode["user_id"])
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE
    )
    to_encode.update({"exp": expires})
    if "user_id" in to_encode:
        to_encode["sub"] = str(to_encode["user_id"])
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
