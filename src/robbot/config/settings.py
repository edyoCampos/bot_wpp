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
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/robbot",
    )
    SECRET_KEY: str = Field(default="change-me")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)

    # SMTP / Email
    SMTP_HOST: str | None = Field(default=None)
    SMTP_PORT: int | None = Field(default=None)
    SMTP_USERNAME: str | None = Field(default=None)
    SMTP_PASSWORD: str | None = Field(default=None)
    SMTP_TLS: bool = Field(default=False)
    SMTP_SENDER: str | None = Field(default=None)

    # CORS configuration
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])
    CORS_CREDENTIALS: bool = Field(default=True)
    COOKIE_HTTPONLY: bool = Field(default=True)
    COOKIE_SECURE: bool = Field(default=False)
    COOKIE_SAMESITE: str = Field(default="lax")
    COOKIE_DOMAIN: str | None = Field(default=None)

    # Email verification
    EMAIL_VERIFICATION_TOKEN_EXPIRATION_HOURS: int = Field(default=24)
    EMAIL_VERIFICATION_RESEND_MIN_INTERVAL_MINUTES: int = Field(default=5)

    # Redis / cache / fila
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    REDIS_CACHE_TTL: int = Field(default=3600)
    REDIS_MAX_CONNECTIONS: int = Field(default=10)

    # Gemini AI
    GOOGLE_API_KEY: str  # required field
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")
    GEMINI_MAX_TOKENS: int = Field(default=2048)
    GEMINI_TEMPERATURE: float = Field(default=0.7)
    
    # OpenAI (Whisper for transcription)
    OPENAI_API_KEY: str | None = Field(default=None)
    WHISPER_MODEL: str = Field(default="whisper-1")

    # WAHA (WhatsApp HTTP API)
    WAHA_URL: str = Field(default="http://waha:3000")
    WAHA_API_KEY: str | None = Field(default=None)
    WAHA_SESSION_NAME: str = Field(default="default")
    WAHA_WEBHOOK_URL: str = Field(
        default="http://api:3333/api/v1/webhooks/waha"
    )

    # Anti-ban settings (WhatsApp best practices)
    WAHA_ANTI_BAN_ENABLED: bool = Field(
        default=True, description="Enable anti-ban delays"
    )
    WAHA_MIN_DELAY_SECONDS: int = Field(
        default=30, description="Min delay before sending (30-60s recommended)"
    )
    WAHA_MAX_DELAY_SECONDS: int = Field(
        default=60, description="Max delay before sending"
    )
    WAHA_MESSAGES_PER_HOUR: int = Field(
        default=20, description="Max messages per hour (conservative limit)"
    )

    # ChromaDB (persistência vetorial)
    CHROMA_PERSIST_DIR: str = Field(default="./data/chroma")
    CHROMA_COLLECTION_NAME: str = Field(default="conversations")
    
    # Clínica GO - Localização Fixa
    CLINIC_NAME: str = Field(default="Clínica GO")
    CLINIC_ADDRESS: str = Field(
        default="Av. São Miguel, 1000 - sala 102 - Centro, Dois Irmãos - RS, 93950-000"
    )
    CLINIC_LATITUDE: float = Field(default=-29.5838212)
    CLINIC_LONGITUDE: float = Field(default=-51.0869905)
    CLINIC_MAPS_URL: str = Field(
        default="https://www.google.com/maps/place/Av.+S%C3%A3o+Miguel,+1000+-+sala+102"
    )

    # Redis Queue (RQ) - Processamento assíncrono
    RQ_DEFAULT_RESULT_TTL: int = Field(
        default=500, description="TTL padrão para resultados de jobs (segundos)"
    )
    RQ_DEFAULT_FAILURE_TTL: int = Field(
        default=86400, description="TTL para jobs falhados (86400 = 24h)"
    )
    RQ_JOB_TIMEOUT_MESSAGE: int = Field(
        default=10, description="Timeout para jobs de mensagens (segundos)"
    )
    RQ_JOB_TIMEOUT_AI: int = Field(
        default=60, description="Timeout para jobs de IA (segundos)"
    )
    RQ_JOB_TIMEOUT_ESCALATION: int = Field(
        default=30, description="Timeout para jobs de escalação (segundos)"
    )
    RQ_MAX_RETRIES: int = Field(
        default=3, description="Número máximo de tentativas por job"
    )
    RQ_FAILED_QUEUE_NAME: str = Field(
        default="failed", description="Nome da fila de jobs falhados (DLQ)"
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
