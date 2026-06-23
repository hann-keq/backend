from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_ROOT_PASSWORD: str
    PMA_HOST : str
    # DB_HOST_DEV : str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE: int
    ALGORITHM: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY_GOOGLE: str
    MERCHANT_ID: str
    MIDTRANS_CLIENT_KEY: str
    MIDTRANS_SERVER_KEY: str
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Absolute path to app/static/uploads — works regardless of cwd
# (local dev vs Docker WORKDIR)
_STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
UPLOAD_ROOT = os.path.join(_STATIC_DIR, "uploads")