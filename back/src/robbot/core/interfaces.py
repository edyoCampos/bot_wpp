"""
Abstract interfaces for core services and external integrations.

These define contracts that implementations must fulfill.
Enables dependency inversion and testability.

Resolves:
- Issue #3: Missing Abstraction for External Services
- Issue #5: No Abstraction Layer for Repository Pattern
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

# ===== LLM Provider Interface =====


class LLMProvider(ABC):
    """
    Abstract interface for Language Model providers.

    Enables swapping between Gemini, Claude, GPT, etc. without changing services.
    Supports text generation, structured output, embeddings, and tool usage.
    """

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        context: str | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """
        Generate a text response from the LLM.

        Args:
            prompt: User message/prompt
            context: Additional context
            max_retries: Max retry attempts

        Returns:
            Dict with keys: response, tokens_used, latency_ms, model, provider, finish_reason
        """

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a structured JSON response following a specific schema.

        Args:
            prompt: User message/prompt
            schema: JSON schema or dictionary describing the expected structure
            context: Additional context

        Returns:
            Dict containing the parsed JSON response and metadata
        """

    @abstractmethod
    async def call_function(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        context: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a response that may include tool/function calls.

        Args:
            prompt: User message/prompt
            tools: List of tool definitions
            context: Additional context

        Returns:
            Dict containing tool calls and/or text response
        """

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embeddings for text (for vector search).

        Args:
            text: Text to embed

        Returns:
            Vector embeddings
        """

    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources (optional override)."""


# ===== Vector Database Interface =====


class VectorStore(ABC):
    """
    Abstract interface for vector database.

    Enables swapping between ChromaDB, Pinecone, Weaviate, etc.
    """

    @abstractmethod
    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]] | None = None,
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        """
        Add documents to vector store.

        Args:
            documents: List of text documents
            embeddings: Pre-computed embeddings (optional)
            metadatas: Metadata for each document
            ids: Custom document IDs
        """

    @abstractmethod
    async def add(self, conversation_id: str, text: str, metadata: dict[str, Any] | None = None) -> str:
        """Add a single document with automatic embedding."""

    @abstractmethod
    async def search(self, conversation_id: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search context for a specific conversation."""

    @abstractmethod
    async def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> dict[str, Any]:
        """
        Query documents by vector similarity.

        Args:
            query_embedding: Query vector
            n_results: Number of results to return

        Returns:
            Dict with keys: documents, distances, metadatas, ids
        """

    @abstractmethod
    async def delete_documents(self, ids: list[str]) -> None:
        """Delete documents by ID."""

    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources (optional override)."""


# ===== WhatsApp Client Interface =====


class WAHAClientInterface(ABC):
    """
    Abstract interface for WhatsApp HTTP API (WAHA).

    Enables swapping WAHA, official WhatsApp API, Twilio, etc.
    """

    @abstractmethod
    async def send_message(
        self,
        chat_id: str,
        message: str,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        """
        Send text message via WhatsApp.

        Args:
            chat_id: WhatsApp chat ID (phone number)
            message: Message text
            reply_to: Message ID to reply to (thread)

        Returns:
            Response with message ID and status
        """

    @abstractmethod
    async def send_media(
        self,
        chat_id: str,
        media_url: str,
        media_type: str,  # image, video, audio, document
        caption: str | None = None,
    ) -> dict[str, Any]:
        """Send media file via WhatsApp."""

    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources (optional override)."""


# ===== Repository Interface =====

ModelType = TypeVar("ModelType")


class IRepository(ABC, Generic[ModelType]):
    """
    Abstract interface for repository pattern.

    Enables testable services with mock repositories.
    Enables swapping between SQLAlchemy, SQLite, MongoDB, etc.
    """

    @abstractmethod
    def create(self, obj: ModelType) -> ModelType:
        """Create and persist a new object."""

    @abstractmethod
    def get_by_id(self, id: Any) -> ModelType | None:
        """Retrieve object by ID."""

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """List all objects with pagination."""

    @abstractmethod
    def update(self, id: Any, obj: ModelType) -> ModelType | None:
        """Update an existing object."""

    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete an object by ID. Returns True if deleted."""

    @abstractmethod
    def exists(self, id: Any) -> bool:
        """Check if object exists."""


# ===== Mock Implementations for Testing =====


class MockLLMProvider(LLMProvider):
    """
    In-memory LLM provider for testing.

    Allows queuing preset responses without calling real API.
    """

    def __init__(self):
        self.response_queue: list[dict[str, Any]] = []
        self.last_prompt: str | None = None
        self.call_count = 0

    async def generate_response(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 500,
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Return preset response from queue."""
        self.last_prompt = prompt
        self.call_count += 1

        if not self.response_queue:
            return {
                "text": "Mock response",
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            }

        return self.response_queue.pop(0)

    async def embed_text(self, text: str) -> list[float]:
        """Return dummy embeddings."""
        return [0.1] * 768  # Mock embedding vector


class MockVectorStore(VectorStore):
    """
    In-memory vector store for testing.

    Stores documents without actually computing similarity.
    """

    def __init__(self):
        self.documents: dict[str, str] = {}
        self.metadatas: dict[str, dict] = {}

    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]] | None = None,
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        """Store documents in memory."""
        for i, doc in enumerate(documents):
            doc_id = ids[i] if ids else str(i)
            self.documents[doc_id] = doc
            if metadatas:
                self.metadatas[doc_id] = metadatas[i]

    async def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> dict[str, Any]:
        """Return all stored documents (no real similarity)."""
        doc_ids = list(self.documents.keys())[:n_results]
        return {
            "documents": [[self.documents[id] for id in doc_ids]],
            "distances": [[0.1] * len(doc_ids)],
            "metadatas": [[self.metadatas.get(id, {}) for id in doc_ids]],
            "ids": [doc_ids],
        }

    async def delete_documents(self, ids: list[str]) -> None:
        """Delete documents from memory."""
        for id in ids:
            self.documents.pop(id, None)
            self.metadatas.pop(id, None)


class MockRepository(IRepository[ModelType]):
    """
    In-memory repository for testing.

    Stores objects in dict without database.
    """

    def __init__(self):
        self._data: dict[Any, ModelType] = {}
        self._next_id = 1

    def create(self, obj: ModelType) -> ModelType:
        """Create object with auto-generated ID."""
        if not hasattr(obj, "id") or obj.id is None:
            obj.id = self._next_id
            self._next_id += 1
        self._data[obj.id] = obj
        return obj

    def get_by_id(self, id: Any) -> ModelType | None:
        """Retrieve by ID."""
        return self._data.get(id)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """List all objects."""
        return list(self._data.values())[skip : skip + limit]

    def update(self, id: Any, obj: ModelType) -> ModelType | None:
        """Update object."""
        if id in self._data:
            self._data[id] = obj
            return obj
        return None

    def delete(self, id: Any) -> bool:
        """Delete by ID."""
        if id in self._data:
            del self._data[id]
            return True
        return False

    def exists(self, id: Any) -> bool:
        """Check if exists."""
        return id in self._data
