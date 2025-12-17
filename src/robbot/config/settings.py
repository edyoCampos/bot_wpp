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
    
    # OpenAI (Whisper for transcription)
    OPENAI_API_KEY: str | None = Field(None, env="OPENAI_API_KEY")
    WHISPER_MODEL: str = Field("whisper-1", env="WHISPER_MODEL")

    # WAHA (WhatsApp HTTP API)
    WAHA_URL: str = Field("http://waha:3000", env="WAHA_URL")
    WAHA_API_KEY: str | None = Field(None, env="WAHA_API_KEY")
    WAHA_SESSION_NAME: str = Field("default", env="WAHA_SESSION_NAME")
    WAHA_WEBHOOK_URL: str = Field(
        "http://api:3333/api/v1/webhooks/waha", env="WAHA_WEBHOOK_URL"
    )


    # Anti-ban settings (WhatsApp best practices)
    WAHA_ANTI_BAN_ENABLED: bool = Field(
        True, env="WAHA_ANTI_BAN_ENABLED", description="Enable anti-ban delays"
    )
    WAHA_MIN_DELAY_SECONDS: int = Field(
        30, env="WAHA_MIN_DELAY_SECONDS", description="Min delay before sending (30-60s recommended)"
    )
    WAHA_MAX_DELAY_SECONDS: int = Field(
        60, env="WAHA_MAX_DELAY_SECONDS", description="Max delay before sending"
    )
    WAHA_MESSAGES_PER_HOUR: int = Field(
        20, env="WAHA_MESSAGES_PER_HOUR", description="Max messages per hour (conservative limit)"
    )

    # ChromaDB (persistência vetorial)
    CHROMA_PERSIST_DIR: str = Field("./data/chroma", env="CHROMA_PERSIST_DIR")
    CHROMA_COLLECTION_NAME: str = Field(
        "conversations", env="CHROMA_COLLECTION_NAME"
    )
    
    # Clínica GO - Localização Fixa
    CLINIC_NAME: str = Field("Clínica GO", env="CLINIC_NAME")
    CLINIC_ADDRESS: str = Field(
        "Av. São Miguel, 1000 - sala 102 - Centro, Dois Irmãos - RS, 93950-000",
        env="CLINIC_ADDRESS"
    )
    CLINIC_LATITUDE: float = Field(-29.5838212, env="CLINIC_LATITUDE")
    CLINIC_LONGITUDE: float = Field(-51.0869905, env="CLINIC_LONGITUDE")
    CLINIC_MAPS_URL: str = Field(
        "https://www.google.com/maps/place/Av.+S%C3%A3o+Miguel,+1000+-+sala+102",
        env="CLINIC_MAPS_URL"
    )

    # Redis Queue (RQ) - Processamento assíncrono
    RQ_DEFAULT_RESULT_TTL: int = Field(
        500, env="RQ_DEFAULT_RESULT_TTL", description="TTL padrão para resultados de jobs (segundos)"
    )
    RQ_DEFAULT_FAILURE_TTL: int = Field(
        86400, env="RQ_DEFAULT_FAILURE_TTL", description="TTL para jobs falhados (86400 = 24h)"
    )
    RQ_JOB_TIMEOUT_MESSAGE: int = Field(
        10, env="RQ_JOB_TIMEOUT_MESSAGE", description="Timeout para jobs de mensagens (segundos)"
    )
    RQ_JOB_TIMEOUT_AI: int = Field(
        60, env="RQ_JOB_TIMEOUT_AI", description="Timeout para jobs de IA (segundos)"
    )
    RQ_JOB_TIMEOUT_ESCALATION: int = Field(
        30, env="RQ_JOB_TIMEOUT_ESCALATION", description="Timeout para jobs de escalação (segundos)"
    )
    RQ_MAX_RETRIES: int = Field(
        3, env="RQ_MAX_RETRIES", description="Número máximo de tentativas por job"
    )
    RQ_FAILED_QUEUE_NAME: str = Field(
        "failed", env="RQ_FAILED_QUEUE_NAME", description="Nome da fila de jobs falhados (DLQ)"
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
