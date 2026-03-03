import logging
import time
from typing import Any, Literal

from robbot.core.interfaces import LLMProvider
from robbot.core.custom_exceptions import LLMError

logger = logging.getLogger(__name__)

ProviderType = Literal["gemini", "groq"]


class LLMProviderManager:
    """Manages LLM providers with automatic fallback.

    Implements Strategy Pattern to allow runtime selection of LLM providers.
    Supports fallback to secondary provider if primary fails.
    """

    def __init__(
        self,
        primary_provider: ProviderType,
        enable_fallback: bool = True,
    ):
        """Initialize provider manager."""
        self._primary_provider_type = primary_provider
        self._enable_fallback = enable_fallback
        self._providers: dict[ProviderType, LLMProvider | None] = {
            "gemini": None,
            "groq": None,
        }

    def register_provider(self, provider_type: ProviderType, provider: LLMProvider) -> None:
        """Register a provider instance."""
        self._providers[provider_type] = provider
        # provider.get_model_name() might not be available if GeminiProvider doesn't have it anymore,
        # but I kept it in the previous step.
        logger.info("Registered %s provider", provider_type)

    def _select_provider(self) -> LLMProvider:
        """Select best available provider."""
        primary = self._providers.get(self._primary_provider_type)
        if primary: # and primary.is_available():
            return primary

        if self._enable_fallback:
            for provider_type, provider in self._providers.items():
                if provider_type != self._primary_provider_type and provider: # and provider.is_available():
                    logger.warning(
                        "Primary provider %s unavailable, falling back to %s",
                        self._primary_provider_type,
                        provider_type,
                    )
                    return provider

        raise LLMError(
            "ProviderManager",
            f"No available providers. Primary: {self._primary_provider_type}, Fallback: {self._enable_fallback}",
        )

    async def generate_response(
        self,
        prompt: str,
        context: str | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Generate response using best available provider with automatic fallback."""
        provider = self._select_provider()

        try:
            return await provider.generate_response(prompt, context, max_retries)

        except LLMError as e:
            if self._enable_fallback and provider.get_provider_name() == self._primary_provider_type:
                logger.warning("Primary provider failed, attempting fallback: %s", e)

                for provider_type, fallback_provider in self._providers.items():
                    if provider_type != self._primary_provider_type and fallback_provider:
                        try:
                            return await fallback_provider.generate_response(prompt, context, max_retries)
                        except LLMError as fallback_error:
                            logger.error("Fallback provider failed: %s", fallback_error)
                            continue

            raise

    async def close(self) -> None:
        """Cleanup all providers."""
        for provider in self._providers.values():
            if provider:
                await provider.close()

    def get_active_provider_info(self) -> dict[str, str]:
        """Get information about current active provider."""
        try:
            provider = self._select_provider()
            return {
                "provider": provider.get_provider_name(),
                "model": provider.get_model_name(),
            }
        except Exception:
            return {
                "provider": "none",
                "model": "unavailable",
            }
