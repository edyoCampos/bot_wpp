"""Application settings loaded from environment variables."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application configuration with sane defaults."""
    # Use Postgres via Docker for local/dev. Provide connection via env.
    # Example in .env:
    # DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/robbot
    DATABASE_URL: str = Field(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/robbot",
        env="DATABASE_URL",
    )
    SECRET_KEY: str = Field("change-me", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(
        60 * 24 * 7, env="REFRESH_TOKEN_EXPIRE_MINUTES")
    SMTP_SENDER: str | None = Field(None, env="SMTP_SENDER")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> "Settings":
    """Retorna singleton de configurações, atrasando validação."""
    return Settings()


settings = get_settings()
