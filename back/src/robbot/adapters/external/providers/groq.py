"""Groq LLM provider implementation.

Implements the LLMProvider interface for Groq's models
using LangChain's ChatGroq with automatic model fallback.
"""

import logging
import time
from typing import Any

from langchain_groq import ChatGroq

from robbot.core.interfaces import LLMProvider
from robbot.core.custom_exceptions import LLMError

logger = logging.getLogger(__name__)

# Groq models ordered by preference (speed, capability, availability)
GROQ_FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",      # Latest Llama 3.3, best balance
    "llama-3.1-8b-instant",         # Fast, lower capability
    "mixtral-8x7b-32768",           # Good for long context
]


class GroqProvider(LLMProvider):
    """Groq LLM provider using LangChain.

    Wraps ChatGroq to provide a consistent interface for interacting
    with Groq's fast inference models.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        default_temperature: float = 0.7,
        default_max_tokens: int = 2048,
        timeout: int = 60,
    ):
        """Initialize Groq provider."""
        self._api_key = api_key
        self._primary_model = model
        self._current_model = model
        self._default_temperature = default_temperature
        self._default_max_tokens = default_max_tokens
        self._timeout = timeout

        try:
            self._client = ChatGroq(
                model=model,
                groq_api_key=api_key,
                temperature=default_temperature,
                max_tokens=default_max_tokens,
                timeout=timeout,
            )
            logger.info(
                "Groq provider initialized: model=%s, temp=%s",
                model,
                default_temperature,
            )
        except Exception as e:
            logger.error("Failed to initialize Groq provider: %s", e)
            raise LLMError("Groq", f"Initialization failed: {e}", original_error=e) from e

    async def generate_response(
        self,
        prompt: str,
        context: str | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Generate response using Groq model with automatic fallback."""
        full_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}" if context else prompt
        
        start_time = time.time()
        # Build list of models to try: primary + fallbacks
        models_to_try = [self._primary_model] + [
            m for m in GROQ_FALLBACK_MODELS if m != self._primary_model
        ]
        last_error = None

        for attempt in range(max_retries):
            for model_name in models_to_try:
                try:
                    # Switch model if needed
                    if model_name != self._current_model:
                        logger.info("[FALLBACK] Switching to Groq model: %s", model_name)
                        self._client = ChatGroq(
                            model=model_name,
                            groq_api_key=self._api_key,
                            temperature=self._default_temperature,
                            max_tokens=self._default_max_tokens,
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
                        "provider": "groq",
                        "finish_reason": "stop",
                    }

                except Exception as e:
                    error_msg = str(e).lower()
                    last_error = e

                    if any(k in error_msg for k in ["rate_limit", "quota", "429", "503", "not found"]):
                        logger.warning("[QUOTA/AVAILABILITY] Groq model %s issue: %s", model_name, error_msg[:100])
                        continue  # Try next model

                    logger.error("Groq generation failed: %s", e)
                    raise LLMError("Groq", str(e), original_error=e) from e

        raise LLMError("Groq", "All models and retries failed", original_error=last_error)

    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        """Generate structured response from Groq."""
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
        return await self.generate_response(prompt, context)

    async def embed_text(self, text: str) -> list[float]:
        """Groq typically doesn't provide embeddings, so this is a placeholder or uses a fallback model."""
        # For now, we raise LLMError as Groq is primarily for inference
        raise LLMError("Groq", "Embeddings not supported natively by Groq provider")

    async def close(self) -> None:
        """Cleanup."""
        pass

    def is_available(self) -> bool:
        return self._client is not None

    def get_provider_name(self) -> str:
        return "groq"

    def get_model_name(self) -> str:
        return self._current_model
