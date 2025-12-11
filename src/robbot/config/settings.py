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

    # Redis / cache / fila
    REDIS_URL: str = Field("redis://redis:6379/0", env="REDIS_URL")
    REDIS_CACHE_TTL: int = Field(3600, env="REDIS_CACHE_TTL")
    REDIS_MAX_CONNECTIONS: int = Field(10, env="REDIS_MAX_CONNECTIONS")

    # Gemini AI
    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")
    GEMINI_MODEL: str = Field("gemini-1.5-flash", env="GEMINI_MODEL")
    GEMINI_MAX_TOKENS: int = Field(2048, env="GEMINI_MAX_TOKENS")
    GEMINI_TEMPERATURE: float = Field(0.7, env="GEMINI_TEMPERATURE")

    # WAHA (WhatsApp HTTP API)
    WAHA_URL: str = Field("http://waha:3000", env="WAHA_URL")
    WAHA_API_KEY: str | None = Field(None, env="WAHA_API_KEY")
    WAHA_SESSION_NAME: str = Field("default", env="WAHA_SESSION_NAME")
    WAHA_WEBHOOK_URL: str = Field(
        "http://api:3333/api/v1/webhooks/waha", env="WAHA_WEBHOOK_URL"
    )

    # ChromaDB (persistência vetorial)
    CHROMA_PERSIST_DIR: str = Field("./data/chroma", env="CHROMA_PERSIST_DIR")
    CHROMA_COLLECTION_NAME: str = Field(
        "conversations", env="CHROMA_COLLECTION_NAME"
    )

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
