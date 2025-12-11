# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        env="DATABASE_URL"
    )

    SECRET_KEY: str = Field(
        default="5190431c647cd269d64bd13be15bf26837b633b5192b431c97b2a2b6080aca63",
        env="SECRET_KEY"
    )

    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # NEW → AES 256-bit key (base64 encoded)
    AESGCM_KEY: Optional[str] = Field(
        default=None,
        env="AESGCM_KEY"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# must exist
settings = Settings()
