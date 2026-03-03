"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application configuration with sane defaults."""

    # Development Mode (filter messages by phone number)
    DEV_MODE: bool = Field(default=False, description="Enable dev mode (only respond to DEV_PHONE_NUMBERS)")
    DEV_PHONE_NUMBERS: str | None = Field(
        default=None, description="Phone numbers to respond to in dev mode (e.g., 5511999999999,5511888888888)"
    )

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

    # Prompts configuration
    PROMPTS_PATH: str = Field(default="src/robbot/config/prompts.yaml")

    # Email verification
    EMAIL_VERIFICATION_TOKEN_EXPIRATION_HOURS: int = Field(default=24)
    EMAIL_VERIFICATION_RESEND_MIN_INTERVAL_MINUTES: int = Field(default=5)
    FRONTEND_URL: str = Field(default="http://localhost:3000")  # Frontend URL for email links

    # Redis / cache / fila
    REDIS_URL: str = Field(default="redis://redis:6379/0")
    REDIS_CACHE_TTL: int = Field(default=3600)
    REDIS_MAX_CONNECTIONS: int = Field(default=10)

    # Groq (Primary - generous free tier, fast)
    GROQ_API_KEY: str | None = Field(default=None)
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile")
    GROQ_MAX_TOKENS: int = Field(default=2048)
    GROQ_TEMPERATURE: float = Field(default=0.7)

    # Gemini AI (Fallback - quota limited)
    GOOGLE_API_KEY: str  # required field
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro")
    GEMINI_MAX_TOKENS: int = Field(default=2048)
    GEMINI_TEMPERATURE: float = Field(default=0.7)

    # LLM Provider Selection
    LLM_PRIMARY_PROVIDER: str = Field(default="groq", description="Primary LLM provider (groq or gemini)")
    LLM_ENABLE_FALLBACK: bool = Field(default=True, description="Enable fallback to secondary provider")
    LLM_TIMEOUT: int = Field(default=60, description="LLM request timeout in seconds")

    # WAHA (WhatsApp HTTP API)
    WAHA_URL: str = Field(default="http://waha:3000")
    WAHA_API_KEY: str | None = Field(default=None)
    WAHA_SESSION_NAME: str = Field(default="default")
    WAHA_WEBHOOK_URL: str = Field(default="http://api:3333/api/v1/webhooks/waha")
    WAHA_MOCK_REQUESTS: bool = Field(default=False, description="Use mock WAHA responses in DEV_MODE")

    # Anti-ban settings (WhatsApp best practices)
    # NOTE: Reduced delays for better UX. Monitor for bans and adjust if needed.
    WAHA_ANTI_BAN_ENABLED: bool = Field(default=True, description="Enable anti-ban delays")
    WAHA_MIN_DELAY_SECONDS: int = Field(default=3, description="Min delay before sending (balance UX vs safety)")
    WAHA_MAX_DELAY_SECONDS: int = Field(default=8, description="Max delay before sending")
    WAHA_MESSAGES_PER_HOUR: int = Field(default=30, description="Max messages per hour (increased for faster conversations)")

    # Message debouncing (group rapid messages)
    MESSAGE_DEBOUNCE_SECONDS: int = Field(
        default=10,
        description="Seconds to wait before processing message (groups rapid messages together)"
    )

    # ChromaDB (persistência vetorial)
    CHROMA_PERSIST_DIR: str = Field(default="./data/chroma")
    CHROMA_COLLECTION_NAME: str = Field(default="conversations")

    # Go - Localização Fixa
    CLINIC_NAME: str = Field(default="Clínica Go")
    CLINIC_ADDRESS: str = Field(default="Av. São Miguel, 1000 - sala 102 - Centro, Dois Irmãos - RS, 93950-000")
    CLINIC_LATITUDE: float = Field(default=-29.5838212)
    CLINIC_LONGITUDE: float = Field(default=-51.0869905)
    CLINIC_MAPS_URL: str = Field(default="https://www.google.com/maps/place/Av.+S%C3%A3o+Miguel,+1000+-+sala+102")

    # Redis Queue (RQ) - Processamento assíncrono
    RQ_DEFAULT_RESULT_TTL: int = Field(default=500, description="TTL padrão para resultados de jobs (segundos)")
    RQ_DEFAULT_FAILURE_TTL: int = Field(default=86400, description="TTL para jobs falhados (86400 = 24h)")
    RQ_JOB_TIMEOUT_MESSAGE: int = Field(default=300, description="Timeout para jobs de mensagens (segundos)")
    RQ_JOB_TIMEOUT_AI: int = Field(default=60, description="Timeout para jobs de IA (segundos)")
    RQ_JOB_TIMEOUT_ESCALATION: int = Field(default=30, description="Timeout para jobs de escalação (segundos)")
    RQ_MAX_RETRIES: int = Field(default=3, description="Número máximo de tentativas por job")
    RQ_FAILED_QUEUE_NAME: str = Field(default="failed", description="Nome da fila de jobs falhados (DLQ)")

    # Analytics Performance Thresholds
    ANALYTICS_LATENCY_THRESHOLD_MS: int = Field(default=5000, description="Threshold de latência para alertas (ms)")
    ANALYTICS_ERROR_RATE_THRESHOLD: float = Field(default=5.0, description="Threshold de taxa de erro para alertas (%)")
    ANALYTICS_REALTIME_WINDOW_MINUTES: int = Field(default=5, description="Janela de tempo para métricas real-time")
    ANALYTICS_ACTIVE_CONVERSATIONS_WARNING: int = Field(
        default=50, description="Threshold warning para conversas ativas"
    )
    ANALYTICS_ACTIVE_CONVERSATIONS_CRITICAL: int = Field(
        default=100, description="Threshold crítico para conversas ativas"
    )

    # Analytics Cache TTL
    ANALYTICS_CACHE_TTL_REALTIME: int = Field(default=30, description="TTL cache para dados real-time (segundos)")
    ANALYTICS_CACHE_TTL_METRICS: int = Field(default=900, description="TTL cache para métricas (segundos)")
    ANALYTICS_CACHE_TTL_HISTORICAL: int = Field(default=3600, description="TTL cache para dados históricos (segundos)")
    ANALYTICS_CACHE_TTL_REPORTS: int = Field(default=1800, description="TTL cache para relatórios (segundos)")

    # WebSocket Rate Limiting
    WEBSOCKET_MAX_CONNECTIONS_PER_USER: int = Field(default=3, description="Máximo de conexões WebSocket por usuário")
    WEBSOCKET_MESSAGE_RATE_LIMIT: int = Field(default=10, description="Máximo de mensagens por segundo")
    WEBSOCKET_IDLE_TIMEOUT_MINUTES: int = Field(default=30, description="Timeout para conexões idle (minutos)")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def dev_phone_list(self) -> list[str]:
        """
        Convert DEV_PHONE_NUMBERS to list format for compatibility.
        
        Supports:
        - Single phone: "555198098876" → ["555198098876"]
        - Multiple phones: "555198098876,555191234567" → ["555198098876", "555191234567"]
        - Empty: None or "" → []
        """
        if not self.DEV_PHONE_NUMBERS:
            return []
        
        # Split by comma and strip whitespace
        phones = [p.strip() for p in str(self.DEV_PHONE_NUMBERS).split(",") if p.strip()]
        return phones


@lru_cache
def get_settings() -> "Settings":
    """Retorna singleton de configurações, atrasando validação."""
    return Settings()


settings = get_settings()
