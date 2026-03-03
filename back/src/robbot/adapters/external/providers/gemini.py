"""Google Gemini LLM provider implementation.

Implements the LLMProvider interface for Google's Gemini models
using LangChain's ChatGoogleGenerativeAI with automatic model fallback.
"""

import logging
import time
from typing import Any
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from robbot.core.interfaces import LLMProvider
from robbot.core.custom_exceptions import LLMError

logger = logging.getLogger(__name__)

# Gemini models ordered by preference (speed, quota availability, capability)
GEMINI_FALLBACK_MODELS = [
    "gemini-2.0-flash",             # Latest and fastest
    "gemini-1.5-flash",             # Robust flash model
    "gemini-1.5-pro",               # Most capable
]


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider using LangChain.

    Wraps ChatGoogleGenerativeAI to provide a consistent interface
    for interacting with Google's Gemini models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        default_temperature: float = 0.7,
        default_max_tokens: int = 2048,
        timeout: int = 60,
    ):
        """Initialize Gemini provider."""
        self._api_key = api_key
        self._primary_model = model
        self._current_model = model
        self._default_temperature = default_temperature
        self._default_max_tokens = default_max_tokens
        self._timeout = timeout

        try:
            self._client = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=default_temperature,
                max_output_tokens=default_max_tokens,
                timeout=timeout,
            )
            self._embeddings_client = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=api_key,
            )
            logger.info(
                "Gemini provider initialized: model=%s, temp=%s",
                model,
                default_temperature,
            )
        except Exception as e:
            logger.error("Failed to initialize Gemini provider: %s", e)
            raise LLMError("Gemini", f"Initialization failed: {e}", original_error=e) from e

    async def generate_response(
        self,
        prompt: str,
        context: str | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Generate response using Gemini model with automatic fallback."""
        full_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}" if context else prompt
        
        start_time = time.time()
        # Build list of models to try: primary + fallbacks
        models_to_try = [self._primary_model] + [
            m for m in GEMINI_FALLBACK_MODELS if m != self._primary_model
        ]
        last_error = None

        for attempt in range(max_retries):
            for model_name in models_to_try:
                try:
                    # Switch model if needed
                    if model_name != self._current_model:
                        logger.info("[FALLBACK] Switching to Gemini model: %s", model_name)
                        self._client = ChatGoogleGenerativeAI(
                            model=model_name,
                            google_api_key=self._api_key,
                            temperature=self._default_temperature,
                            max_output_tokens=self._default_max_tokens,
                            timeout=self._timeout,
                        )
                        self._current_model = model_name

                    response = await self._client.ainvoke(full_prompt)
                    latency_ms = int((time.time() - start_time) * 1000)
                    
                    return {
                        "response": response.content,
                        "tokens_used": None,
                        "latency_ms": latency_ms,
                        "model": self._current_model,
                        "provider": "gemini",
                        "finish_reason": "stop",
                    }

                except Exception as e:
                    error_msg = str(e)
                    last_error = e

                    if "429" in error_msg or "resource_exhausted" in error_msg or "404" in error_msg:
                        logger.warning("[QUOTA/AVAILABILITY] Gemini model %s issue: %s", model_name, error_msg[:100])
                        continue  # Try next model

                    logger.error("Gemini generation failed: %s", e)
                    raise LLMError("Gemini", error_msg, original_error=e) from e

        raise LLMError("Gemini", "All models and retries failed", original_error=last_error)

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Generate structured response from Gemini."""
        # For now, simple implementation using prompt engineering
        # Gemini 1.5+ supports actual JSON mode, but for unification we start simple
        structured_prompt = f"{prompt}\n\nYour response MUST be a valid JSON object matching this schema: {schema}"
        result = await self.generate_response(structured_prompt, context)
        return result

    async def call_function(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Placeholder for tool usage."""
        # Future implementation with Gemini function calling
        return await self.generate_response(prompt, context)

    async def embed_text(self, text: str) -> list[float]:
        """Generate embeddings using Gemini Text Embedding model."""
        try:
            embeddings = await self._embeddings_client.aembed_query(text)
            return embeddings
        except Exception as e:
            logger.error("Gemini embedding failed: %s", e)
            raise LLMError("GeminiEmbeddings", str(e), original_error=e) from e

    async def close(self) -> None:
        """Cleanup."""
        pass

    # Keep these for internal manager usage if needed
    def is_available(self) -> bool:
        return self._client is not None

    def get_provider_name(self) -> str:
        return "gemini"

    def get_model_name(self) -> str:
        return self._current_model
