from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_ROOT_PASSWORD: str
    PMA_HOST : str
    DB_HOST_DEV : str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()