"""
Dependency injection container for FastAPI application.

Centralized dependency management initialized at startup.
No more singletons scattered across modules.

Resolves Issue #1: Rampant Singleton Anti-Pattern
"""

import redis

from robbot.infra.integrations.vector_store.chroma_vector_store import ChromaVectorStore
from robbot.infra.integrations.llm.llm_client import get_llm_client
from robbot.infra.integrations.waha.waha_integration import WAHAIntegration
from robbot.config.prompt_loader import PromptLoader
from robbot.config.settings import Settings
from robbot.core.interfaces import LLMProvider, VectorStore, WAHAClientInterface
from robbot.infra.db.base import SessionLocal
from robbot.infra.redis.client import get_redis_client


class DIContainer:
    """
    Dependency Injection Container.

    Manages lifecycle of application dependencies.
    Initialized once at startup, shared across all requests.

    Replaces all singleton patterns with explicit dependency injection.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

        # Infrastructure dependencies
        self._redis: redis.Redis | None = None

        # Service interfaces (abstractions)
        self._llm: LLMProvider | None = None
        self._vector_store: VectorStore | None = None
        self._waha: WAHAClientInterface | None = None

        # Configuration loaders
        self._prompt_loader: PromptLoader | None = None

        # Session factory
        self._session_factory = SessionLocal

    async def initialize(self) -> None:
        """
        Initialize all container dependencies.
        Called during app startup (lifespan context).
        """
        # Initialize infrastructure
        self._redis = get_redis_client()

        # Initialize service implementations (via interfaces)
        # In dev/test we may skip LLM if API key is unavailable
        if (not self.settings.GOOGLE_API_KEY or self.settings.GOOGLE_API_KEY.lower() == "skip") and \
           (not self.settings.GROQ_API_KEY or self.settings.GROQ_API_KEY.lower() == "skip"):
            self._llm = None
        else:
            # LLMClient handles internal provider registration and fallback
            self._llm = get_llm_client()

        self._vector_store = ChromaVectorStore(
            collection_name=self.settings.CHROMA_COLLECTION_NAME,
        )

        self._waha = WAHAIntegration(
            base_url=self.settings.WAHA_URL,
            api_token=self.settings.WAHA_API_KEY,
        )

        # Initialize configuration loaders
        self._prompt_loader = PromptLoader(prompts_path=self.settings.PROMPTS_PATH)

    async def shutdown(self) -> None:
        """
        Clean up dependencies on application shutdown.
        Called during app shutdown (lifespan context).
        """
        if self._redis:
            self._redis.close()

        if self._llm:
            await self._llm.close()

        if self._vector_store:
            await self._vector_store.close()

        if self._waha:
            await self._waha.close()

    # ===== Getter methods for dependency injection =====

    def get_redis(self) -> redis.Redis:
        """Get Redis client instance."""
        if self._redis is None:
            raise RuntimeError("Redis not initialized")
        return self._redis

    # Backward-compatible alias for tests
    def get_redis_client(self) -> redis.Redis:
        return self.get_redis()

    def get_llm(self) -> LLMProvider:
        """Get LLM provider instance (interface)."""
        if self._llm is None:
            raise RuntimeError("LLM provider not initialized")
        return self._llm

    # Backward-compatible alias for tests
    def get_llm_provider(self) -> LLMProvider:
        return self.get_llm()

    def get_vector_store(self) -> VectorStore:
        """Get vector store instance (interface)."""
        if self._vector_store is None:
            raise RuntimeError("Vector store not initialized")
        return self._vector_store

    # Backward-compatible alias for tests
    def get_vectorstore(self) -> VectorStore:
        return self.get_vector_store()

    def get_waha(self) -> WAHAClientInterface:
        """Get WAHA WhatsApp client instance (interface)."""
        if self._waha is None:
            raise RuntimeError("WAHA client not initialized")
        return self._waha

    # Backward-compatible alias for tests
    def get_waha_client(self) -> WAHAClientInterface:
        return self.get_waha()

    def get_prompt_loader(self) -> PromptLoader:
        """Get prompt loader instance."""
        if self._prompt_loader is None:
            raise RuntimeError("Prompt loader not initialized")
        return self._prompt_loader

    def get_session_factory(self):
        """Get SQLAlchemy session factory."""
        return self._session_factory


# Global container instance (initialized once per app)
_container: DIContainer | None = None


def get_container() -> DIContainer:
    """Get global DI container instance."""
    if _container is None:
        raise RuntimeError("DI Container not initialized. Call initialize_container() first.")
    return _container


async def initialize_container(settings: Settings) -> DIContainer:
    """
    Initialize global DI container.

    Should be called in app startup (lifespan context).

    Args:
        settings: Application settings from config

    Returns:
        Initialized DIContainer instance
    """
    global _container
    _container = DIContainer(settings)
    await _container.initialize()
    return _container


async def shutdown_container() -> None:
    """
    Shutdown global DI container.

    Should be called in app shutdown (lifespan context).
    """
    global _container
    if _container:
        await _container.shutdown()
        _container = None

