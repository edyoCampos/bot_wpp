"""
LLM client with multi-provider support and automatic fallback.

This module provides a singleton client to interact with LLM providers (Gemini, Groq)
using a provider abstraction layer. Handles connection setup, prompt formatting,
error handling, and automatic fallback when primary provider fails.
"""

import logging
import time
from typing import Any

from robbot.adapters.external.providers import LLMProviderManager, ProviderType
from robbot.adapters.external.providers.gemini import GeminiProvider
from robbot.adapters.external.providers.groq import GroqProvider
from robbot.config.settings import settings
from robbot.core.custom_exceptions import LLMError
from robbot.core.interfaces import LLMProvider

logger = logging.getLogger(__name__)

_singleton: dict[str, "LLMClient | None"] = {"client": None}


class LLMClient(LLMProvider):
    """
    LLM client with multi-provider support and automatic fallback.

    Uses provider abstraction to support multiple LLM services:
    - Gemini (Google)
    - Groq (Llama models)

    Responsibilities:
    - Initialize and manage LLM providers
    - Generate responses with automatic fallback
    - Provide a singleton interface for the application
    """

    def __init__(self):
        """
        Initialize LLMClient with provider manager and available providers.

        Raises:
            LLMError: If initialization fails
        """
        try:
            # Determine primary provider from settings
            primary: ProviderType = "gemini" if settings.LLM_PRIMARY_PROVIDER == "gemini" else "groq"

            # Initialize provider manager
            self.manager = LLMProviderManager(
                primary_provider=primary,
                enable_fallback=settings.LLM_ENABLE_FALLBACK,
            )

            # Register Gemini provider
            if settings.GOOGLE_API_KEY:
                gemini = GeminiProvider(
                    api_key=settings.GOOGLE_API_KEY,
                    model=settings.GEMINI_MODEL,
                    default_temperature=settings.GEMINI_TEMPERATURE,
                    default_max_tokens=settings.GEMINI_MAX_TOKENS,
                    timeout=settings.LLM_TIMEOUT,
                )
                self.manager.register_provider("gemini", gemini)
                logger.info("[PROVIDER] Gemini registered (model=%s)", settings.GEMINI_MODEL)

            # Register Groq provider
            if settings.GROQ_API_KEY:
                groq = GroqProvider(
                    api_key=settings.GROQ_API_KEY,
                    model=settings.GROQ_MODEL,
                    default_temperature=settings.GROQ_TEMPERATURE,
                    default_max_tokens=settings.GROQ_MAX_TOKENS,
                    timeout=settings.LLM_TIMEOUT,
                )
                self.manager.register_provider("groq", groq)
                logger.info("[PROVIDER] Groq registered (model=%s)", settings.GROQ_MODEL)

            active_provider = self.manager.get_active_provider_info()
            logger.info(
                "[SUCCESS] LLMClient initialized with %s as primary provider",
                active_provider["provider"],
            )
        except Exception as e:
            logger.error("[ERROR] Failed to initialize LLMClient: %s", e)
            raise LLMError("LLMClient", f"Initialization failed: {e}", original_error=e) from e

    async def generate_response(
        self,
        prompt: str,
        context: str | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """
        Generate a response from LLM with automatic provider fallback.
        """
        try:
            logger.info("[INFO] Generating LLM response via provider manager")
            
            # Provider manager handles fallback automatically
            # Note: We need to ensure LLMProviderManager.generate_response is async
            # or wrap it. Since we updated Providers to be async, let's update Manager too.
            result = await self.manager.generate_response(
                prompt=prompt,
                context=context,
                max_retries=max_retries,
            )
            return result

        except LLMError:
            raise
        except Exception as e:
            logger.error("[ERROR] Unexpected error generating response: %s", e, exc_info=True)
            raise LLMError("LLMClient", f"Unexpected error: {e}", original_error=e) from e

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Generate structured response via active provider."""
        provider = self.manager._select_provider()
        return await provider.generate_structured(prompt, schema, context)

    async def call_function(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Call function via active provider."""
        provider = self.manager._select_provider()
        return await provider.call_function(prompt, tools, context)

    async def embed_text(self, text: str) -> list[float]:
        """Generate embeddings via active provider."""
        provider = self.manager._select_provider()
        return await provider.embed_text(text)

    async def close(self) -> None:
        """Cleanup resources."""
        await self.manager.close()


def get_llm_client() -> LLMClient:
    """
    Get singleton instance of LLMClient.
    """
    client = _singleton.get("client")
    if client is None:
        _singleton["client"] = LLMClient()
        logger.info("LLMClient initialized as singleton")
    return _singleton["client"]  # type: ignore[return-value]


def close_llm_client() -> None:
    """
    Close LLMClient singleton instance.
    """
    if _singleton.get("client") is not None:
        logger.info("Closing LLMClient singleton")
    _singleton["client"] = None
