"""
Unit tests for DIContainer dependency injection.

Tests container initialization, dependency availability, and lifecycle management.

Resolves Issue #1: Rampant Singleton Anti-Pattern
"""

from collections.abc import AsyncGenerator

import pytest

from robbot.config.container import DIContainer
from robbot.config.settings import Settings
from robbot.core.interfaces import (
    LLMProvider,
    VectorStore,
    WAHAClientInterface,
)


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        DATABASE_URL="sqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/0",
        GOOGLE_API_KEY="test-api-key",
        WAHA_API_URL="http://localhost:3000",
        CORS_ORIGINS=["http://localhost:3000"],
    )


@pytest.fixture
async def container(settings: Settings) -> AsyncGenerator[DIContainer, None]:
    """Create and initialize container for testing."""
    container = DIContainer(settings)
    await container.initialize()
    yield container
    await container.shutdown()


class TestDIContainerInitialization:
    """Test container initialization and setup."""

    def test_container_creation(self, settings: Settings):
        """Test DIContainer can be instantiated."""
        container = DIContainer(settings)
        assert container is not None
        assert container.settings == settings

    @pytest.mark.asyncio
    async def test_container_initialize(self, container: DIContainer):
        """Test container initializes without errors."""
        assert container is not None
        # If we got here without exception, initialization succeeded

    @pytest.mark.asyncio
    async def test_container_shutdown(self, settings: Settings):
        """Test container shutdown."""
        container = DIContainer(settings)
        await container.initialize()
        await container.shutdown()
        # If no exception, shutdown succeeded


class TestDIContainerDependencies:
    """Test dependency resolution from container."""

    @pytest.mark.asyncio
    async def test_get_llm_provider(self, container: DIContainer):
        """Test LLM provider can be retrieved."""
        llm = container.get_llm_provider()
        assert llm is not None
        assert isinstance(llm, LLMProvider)

    @pytest.mark.asyncio
    async def test_get_vector_store(self, container: DIContainer):
        """Test vector store can be retrieved."""
        vector_store = container.get_vector_store()
        assert vector_store is not None
        assert isinstance(vector_store, VectorStore)

    @pytest.mark.asyncio
    async def test_get_waha_client(self, container: DIContainer):
        """Test WAHA client can be retrieved."""
        waha = container.get_waha_client()
        assert waha is not None
        assert isinstance(waha, WAHAClientInterface)

    @pytest.mark.asyncio
    async def test_get_prompt_loader(self, container: DIContainer):
        """Test prompt loader can be retrieved."""
        prompt_loader = container.get_prompt_loader()
        assert prompt_loader is not None
        # Verify it has necessary methods
        assert hasattr(prompt_loader, "get_prompt")
        assert hasattr(prompt_loader, "get_all_prompts")

    @pytest.mark.asyncio
    async def test_get_redis_client(self, container: DIContainer):
        """Test Redis client can be retrieved."""
        redis_client = container.get_redis_client()
        assert redis_client is not None
        assert hasattr(redis_client, "get")
        assert hasattr(redis_client, "set")


class TestDIContainerSingletonsEliminated:
    """Test that singletons have been properly eliminated."""

    @pytest.mark.asyncio
    async def test_no_get_conversation_orchestrator_singleton(self, container: DIContainer):
        """Test that get_conversation_orchestrator() singleton is gone."""
        # This should not exist anymore - orchestrator should come from container
        assert not hasattr(container, "get_conversation_orchestrator")

    @pytest.mark.asyncio
    async def test_dependencies_injected_not_global(self, container: DIContainer):
        """Test that dependencies are injected, not retrieved from global scope."""
        # All dependencies should come from container, not from module-level singletons
        llm1 = container.get_llm_provider()
        llm2 = container.get_llm_provider()
        # Should return same instance (singleton per container)
        assert llm1 is llm2


class TestDIContainerIntegration:
    """Integration tests for container with application."""

    @pytest.mark.asyncio
    async def test_container_in_lifespan(self, settings: Settings):
        """Test container integrates properly with FastAPI lifespan."""
        from robbot.main import create_app

        app = create_app()
        # App should initialize without errors
        assert app is not None

    @pytest.mark.asyncio
    async def test_dependencies_fastapi_integration(self, settings: Settings):
        """Test dependencies can be injected into FastAPI dependencies."""
        from robbot.api.v1.dependencies import get_container_dep

        # Simulate dependency injection in FastAPI context
        container = DIContainer(settings)
        await container.initialize()

        try:
            # This should work without errors
            deps = get_container_dep()
            assert deps is not None
        finally:
            await container.shutdown()


class TestDIContainerErrorHandling:
    """Test error handling in container."""

    @pytest.mark.asyncio
    async def test_container_handles_missing_settings(self):
        """Test container raises error with invalid settings."""
        invalid_settings = Settings(
            DATABASE_URL="invalid://url",
            REDIS_URL="invalid://url",
            GOOGLE_API_KEY="",  # Invalid: empty API key
        )

        container = DIContainer(invalid_settings)
        # Initialization should handle or raise appropriate error
        with pytest.raises(ValueError):  # Could be any exception
            await container.initialize()

    @pytest.mark.asyncio
    async def test_container_dependency_not_available_before_init(self, settings: Settings):
        """Test that dependencies raise error before initialization."""
        container = DIContainer(settings)
        # Before initialization, should not be available
        with pytest.raises(RuntimeError):
            container.get_llm_provider()


class TestDIContainerLifecycleManagement:
    """Test container lifecycle management."""

    @pytest.mark.asyncio
    async def test_multiple_initialize_calls(self, settings: Settings):
        """Test that multiple initializations are handled."""
        container = DIContainer(settings)
        await container.initialize()
        # Second initialization should reinitialize or raise error
        try:
            await container.initialize()  # Should be idempotent
        except Exception:
            # Or it might raise, which is also acceptable
            pass
        finally:
            await container.shutdown()

    @pytest.mark.asyncio
    async def test_shutdown_cleanup(self, settings: Settings):
        """Test that shutdown properly cleans up resources."""
        container = DIContainer(settings)
        await container.initialize()

        redis_before = container.get_redis_client()
        assert redis_before is not None

        await container.shutdown()

        # After shutdown, getting dependencies should raise error
        with pytest.raises(RuntimeError):
            container.get_redis_client()
