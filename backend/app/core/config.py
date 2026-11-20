from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = False

    DATABASE_HOST: str
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    CORS_ORIGINS: list[str] = []

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()