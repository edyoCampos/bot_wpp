"""
Context Builder - Manages conversational context via a VectorStore (e.g., ChromaDB).

Responsibilities:
- Retrieve conversation history from the vector store
- Persist new interactions to the vector store
- Format context for the LLM
"""

import logging
from typing import Any

from robbot.core.custom_exceptions import VectorDBError
from robbot.core.interfaces import VectorStore

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Manage conversational context using an injected `VectorStore`."""

    def __init__(self, vector_store: VectorStore):
        """
        Initialize ContextBuilder with DI.

        Args:
            vector_store: Injected VectorStore implementation (ChromaDB, Pinecone, etc.)
        """
        self.vector_store = vector_store

    async def get_conversation_context(self, conversation_id: str, limit: int = 10) -> str:
        """
        Retrieve formatted conversational context from the vector store.

        Args:
            conversation_id: Conversation identifier
            limit: Max number of past interactions to include (default 10 for better memory)

        Returns:
            Formatted context string (empty if no history)

        Raises:
            VectorDBError: If access to the vector store fails
        """
        try:
            results = await self.vector_store.search(conversation_id, limit=limit)

            if not results:
                return ""

            context_parts = [r.get("text", "") for r in results]
            context_text = "\n---\n".join(context_parts)

            # Limit context to ~5000 chars (2.5x increase for better context retention)
            MAX_CONTEXT_CHARS = 5000  # noqa: N806
            if len(context_text) > MAX_CONTEXT_CHARS:
                logger.warning(
                    "[CONTEXT_TRIM] Context too long (%s chars), trimming to %s chars",
                    len(context_text),
                    MAX_CONTEXT_CHARS,
                )
                # Keep most recent context (trim from beginning, not end)
                context_text = "[...older context trimmed]\n" + context_text[-MAX_CONTEXT_CHARS:]

            logger.info("[SUCCESS] Context retrieved (%s documents, %s chars)", len(results), len(context_text))

            return context_text

        except VectorDBError:
            raise
        except Exception as e:  # noqa: BLE001
            logger.warning("[WARNING] Failed to fetch context: %s", e)
            raise VectorDBError(f"Failed to get context: {e}") from e

    async def save_to_chroma(self, conversation_id: str, text: str, metadata: dict[str, Any]) -> None:
        """
        Persist a user/bot message pair into the vector store for future context.

        Args:
            conversation_id: Conversation identifier
            text: Text content of the interaction
            metadata: Metadata (intent, score, etc.)

        Raises:
            VectorDBError: If saving to the vector store fails
        """
        try:
            await self.vector_store.add(conversation_id, text, metadata)
            logger.info("[SUCCESS] Context saved to ChromaDB (conv_id=%s)", conversation_id)

        except VectorDBError:
            raise
        except Exception as e:  # noqa: BLE001
            logger.warning("[WARNING] Failed to save to ChromaDB: %s", e)
            raise VectorDBError(f"Failed to save to ChromaDB: {e}") from e
