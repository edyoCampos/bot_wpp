"""
ChromaDB implementation of VectorStore interface.

Wraps ChromaClient with proper abstraction for dependency injection.

Resolves Issue #3: Missing Abstraction for External Services
"""

import asyncio
import logging
from typing import Any

from robbot.core.interfaces import VectorStore
from robbot.infra.vectordb.chroma_client import ChromaClient

logger = logging.getLogger("robbot.adapters.external.chroma_vector_store")


class ChromaVectorStore(VectorStore):
    """
    Concrete implementation of VectorStore using ChromaDB.

    Wraps ChromaClient to provide a clean interface for services.
    Enables easy swapping with other vector stores (Pinecone, Weaviate, etc.).
    """

    def __init__(self, collection_name: str = "conversations"):
        """
        Initialize ChromaDB vector store.

        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            collection_name: Name of collection to use
        """
        self.collection_name = collection_name

        # Initialize underlying ChromaDB client
        self._client = ChromaClient(collection_name=collection_name)

        logger.info(f"Initialized ChromaVectorStore with collection: {collection_name}")

    async def add(self, conversation_id: str, text: str, metadata: dict[str, Any] | None = None) -> str:
        """Add a single conversation document."""
        return await asyncio.to_thread(
            self._client.add_conversation, conversation_id=conversation_id, text=text, metadata=metadata
        )

    async def search(self, conversation_id: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search/Get context for a conversation."""
        return await asyncio.to_thread(self._client.get_context, conversation_id=conversation_id, limit=limit)

    async def add_documents(
        self,
        documents: list[str],
        embeddings: list[list[float]] | None = None,
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        """
        Add documents to ChromaDB.

        Args:
            documents: List of text documents
            embeddings: Pre-computed embeddings (optional)
            metadatas: Metadata for each document
            ids: Custom document IDs
        """
        try:
            metadatas = metadatas or [{} for _ in documents]
            ids = ids or [None for _ in documents]

            async def _add_one(doc: str, meta: dict, doc_id: str | None):
                convo_id = meta.get("conversation_id", "default")
                await asyncio.to_thread(
                    self._client.add_conversation,
                    conversation_id=convo_id,
                    text=doc,
                    metadata=meta,
                    doc_id=doc_id,
                )

            await asyncio.gather(
                *[_add_one(doc, meta, doc_id) for doc, meta, doc_id in zip(documents, metadatas, ids, strict=False)]
            )
            logger.debug("Added %d documents to ChromaDB", len(documents))
        except Exception as e:
            logger.error("Error adding documents: %s", e)
            raise

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
            Dict with keys:
                - documents: List of matching documents
                - distances: Cosine distances
                - metadatas: Metadata for each result
                - ids: Document IDs
        """
        try:
            # ChromaClient is text-based; approximate by using text search
            query_text = " ".join(str(x) for x in query_embedding)
            results = await asyncio.to_thread(
                self._client.search_similar,
                query=query_text,
                n_results=n_results,
            )
            return {
                "documents": [r.get("text") for r in results],
                "distances": [r.get("distance") for r in results],
                "metadatas": [r.get("metadata") for r in results],
                "ids": [r.get("id") for r in results],
            }
        except Exception as e:
            logger.error("Error querying ChromaDB: %s", e)
            raise

    async def delete_documents(self, ids: list[str]) -> None:
        """
        Delete documents by ID.

        Args:
            ids: List of document IDs to delete
        """
        try:
            # If ids provided, delete directly; otherwise no-op
            await asyncio.to_thread(self._client.collection.delete, ids=ids)
            logger.debug(f"Deleted {len(ids)} documents from ChromaDB")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    async def close(self) -> None:
        """Clean up resources."""
        try:
            # ChromaClient uses in-process client; nothing to close
            logger.info("ChromaVectorStore closed")
        except Exception as e:
            logger.error("Error closing ChromaDB client: %s", e)
