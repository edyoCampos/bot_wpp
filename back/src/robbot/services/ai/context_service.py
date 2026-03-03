"""ContextService orchestrating context business logic and RAG search."""

import logging

import chromadb
from chromadb.config import Settings as ChromaSettings
from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.content_repository import ContentRepository
from robbot.infra.persistence.repositories.context_embedding_repository import ContextEmbeddingRepository
from robbot.infra.persistence.repositories.context_repository import ContextRepository
from robbot.infra.persistence.repositories.context_item_repository import ContextItemRepository
from robbot.infra.persistence.repositories.topic_repository import TopicRepository
from robbot.config.settings import get_settings
from robbot.core.custom_exceptions import NotFoundException
from robbot.infra.persistence.models.context_embedding_model import ContextEmbeddingModel as ContextEmbedding
from robbot.infra.persistence.models.context_model import ContextModel
from robbot.infra.persistence.models.context_item_model import ContextItemModel
from robbot.infra.persistence.models.topic_model import TopicModel
from robbot.schemas.context import ContextSearchResult

logger = logging.getLogger(__name__)
settings = get_settings()


class ContextService:
    def __init__(self, db: Session):
        self.db = db
        self.topic_repo = TopicRepository(db)
        self.context_repo = ContextRepository(db)
        self.item_repo = ContextItemRepository(db)
        self.embedding_repo = ContextEmbeddingRepository(db)
        self.content_repo = ContentRepository(db)

        # ChromaDB client for semantic search
        try:
            self.chroma_client = chromadb.Client(
                ChromaSettings(
                    persist_directory=settings.CHROMA_PERSIST_DIR,
                    anonymized_telemetry=False,
                )
            )
            self.contexts_collection = self.chroma_client.get_or_create_collection(
                name="contexts",
                metadata={"hnsw:space": "cosine", "description": "Context embeddings for semantic search"},
            )
            logger.info("[SUCCESS] ContextService initialized (contexts count=%s)", self.contexts_collection.count())
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Failed to initialize ChromaDB for contexts: %s", e)
            raise

    # ===== TOPIC OPERATIONS =====

    def create_topic(
        self, name: str, description: str | None = None, category: str | None = None, active: bool = True
    ) -> TopicModel:
        """Create a new topic."""
        topic = TopicModel(name=name, description=description, category=category, active=active)
        return self.topic_repo.create(topic)

    def get_topic(self, topic_id: str) -> TopicModel | None:
        """Get topic by ID."""
        return self.topic_repo.get_by_id(topic_id)

    def list_topics(self, active_only: bool = False, skip: int = 0, limit: int = 100) -> list[TopicModel]:
        """List all topics."""
        return self.topic_repo.list_all(active_only=active_only, skip=skip, limit=limit)

    def update_topic(self, topic_id: str, **kwargs) -> TopicModel | None:
        """Update topic fields."""
        return self.topic_repo.update(topic_id, **kwargs)

    def delete_topic(self, topic_id: str) -> bool:
        """Delete topic (cascades to contexts)."""
        return self.topic_repo.delete(topic_id)

    # ===== CONTEXT OPERATIONS =====

    def create_context(
        self, topic_id: str, name: str, description: str | None = None, active: bool = True
    ) -> ContextModel:
        """
        Create context and auto-index for semantic search.
        """
        context = ContextModel(
            topic_id=topic_id,
            name=name,
            description=description,
            active=active,
        )
        created = self.context_repo.create(context)

        # Auto-generate embedding (will be populated when items are added)
        try:
            self._generate_context_embedding(created.id)
            logger.info("[SUCCESS] Context %s created and indexed", created.id)
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.warning("[WARNING] Context created but indexing failed: %s", e)

        return created

    def get_context(self, context_id: str) -> ContextModel | None:
        """Get context by ID."""
        return self.context_repo.get_by_id(context_id)

    def list_contexts_by_topic(self, topic_id: str) -> list[ContextModel]:
        """List contexts by topic."""
        return self.context_repo.list_by_topic(topic_id)

    def update_context(self, context_id: str, **kwargs) -> ContextModel | None:
        """Update context and reindex."""
        updated = self.context_repo.update(context_id, **kwargs)
        if updated:
            try:
                self._generate_context_embedding(context_id)
                logger.info("[SUCCESS] Context %s updated and reindexed", context_id)
            except Exception as e:  # noqa: BLE001 (blind exception)
                logger.warning("[WARNING] Context updated but reindexing failed: %s", e)
        return updated

    def delete_context(self, context_id: str) -> bool:
        """Delete context (cascades to items and removes from ChromaDB)."""
        # Remove from ChromaDB first
        embedding = self.embedding_repo.get_by_context_id(context_id)
        if embedding and embedding.chroma_doc_id:
            try:
                self.contexts_collection.delete(ids=[embedding.chroma_doc_id])
                logger.info("[SUCCESS] Removed context %s from ChromaDB", context_id)
            except Exception as e:  # noqa: BLE001 (blind exception)
                logger.warning("[WARNING] Failed to remove from ChromaDB: %s", e)

        # Delete from database (cascades)
        return self.context_repo.delete(context_id)

    # ===== CONTEXT ITEM OPERATIONS =====

    def add_item(
        self,
        context_id: str,
        content_id: str,
        item_order: int | None = None,
        context_hint: str | None = None,
    ) -> ContextItemModel:
        """Add item to context and reindex."""
        # Auto-assign order if not provided
        if not item_order:
            item_order = self.item_repo.get_next_order(context_id)

        item = ContextItemModel(
            context_id=context_id,
            content_id=content_id,
            item_order=item_order,
            context_hint=context_hint,
        )

        created = self.item_repo.create(item)

        # Reindex context
        try:
            self._generate_context_embedding(context_id)
            logger.info("[SUCCESS] Item added to context %s, reindexed", context_id)
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.warning("[WARNING] Item added but reindexing failed: %s", e)

        return created

    def get_context_items(self, context_id: str) -> list[ContextItemModel]:
        """Get all items for a context in order."""
        return self.item_repo.list_by_context(context_id)

    def get_context_items_with_details(self, context_id: str) -> list[dict]:
        """
        Get context items with full content details for LLM.
        """
        items = self.item_repo.list_by_context(context_id)
        result = []

        for item in items:
            # Get content details
            content = self.content_repo.get_by_id(item.content_id)
            if not content:
                logger.warning("[WARNING] Content %s not found for item %s", item.content_id, item.id)
                continue

            item_data = {
                "item_order": item.item_order,
                "item_id": item.id,
                "context_hint": item.context_hint,
                "content_id": item.content_id,
                "content_type": content.type,
                "content_title": content.title,
                "content_description": content.description,
                "content_tags": content.tags,
            }

            # Add type-specific fields
            if content.type == "text":
                item_data["content_text"] = content.text
            elif content.type in ("image", "voice", "video", "document"):
                item_data["content_caption"] = content.caption
                if content.media and len(content.media) > 0:
                    item_data["media_url"] = content.media[0].url
                    item_data["media_mimetype"] = content.media[0].mimetype
                    item_data["media_filename"] = content.media[0].filename
            elif content.type == "location" and content.location:
                item_data["latitude"] = content.location.latitude
                item_data["longitude"] = content.location.longitude
                item_data["location_title"] = content.location.title

            result.append(item_data)

        return result

    def reorder_items(self, context_id: str, item_id_order: list[tuple[str, int]]) -> bool:
        """Reorder multiple items at once."""
        return self.item_repo.reorder_items(context_id, item_id_order)

    def delete_item(self, item_id: str) -> bool:
        """Delete item and reindex context."""
        item = self.item_repo.get_by_id(item_id)
        if not item:
            return False

        context_id = item.context_id
        self.item_repo.delete(item_id)

        try:
            self._generate_context_embedding(context_id)
            logger.info("[SUCCESS] Item deleted from context %s, reindexed", context_id)
        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.warning("[WARNING] Item deleted but reindexing failed: %s", e)

        return True

    # ===== SEMANTIC SEARCH (RAG) =====

    def search_contexts(self, query: str, top_k: int = 3, active_only: bool = True) -> list[ContextSearchResult]:
        """
        Semantic search for relevant contexts using ChromaDB.
        """
        try:
            # Query ChromaDB
            where_filter = {"active": True} if active_only else None
            results = self.contexts_collection.query(query_texts=[query], n_results=top_k, where=where_filter)

            if not results["ids"][0]:
                logger.debug("[INFO] No contexts found for query: %s", query)
                return []

            # Format results
            context_results = []
            for i, _chroma_doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]

                context_results.append(
                    ContextSearchResult(
                        context_id=metadata["context_id"],
                        name=metadata["context_name"],
                        description=metadata.get("description"),
                        topic_name=metadata.get("topic_name", "Unknown"),
                        relevance_score=round(1 - distance, 3),
                    )
                )

            logger.info("[SUCCESS] Found %s contexts for query: %s", len(context_results), query)
            return context_results

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Semantic search failed for query '%s': %s", query, e, exc_info=True)
            return []

    # ===== PRIVATE METHODS =====

    def _generate_context_embedding(self, context_id: str) -> None:
        """
        Generate and store embedding for a context.
        """
        try:
            # Get context and related data
            context = self.context_repo.get_by_id(context_id)
            if not context:
                raise NotFoundException(f"Context {context_id} not found")

            topic = self.topic_repo.get_by_id(context.topic_id)
            items = self.get_context_items_with_details(context_id)

            # Build rich embedding text
            parts = []

            # Topic context
            if topic:
                parts.append(f"Topic: {topic.name}")
                if topic.category:
                    parts.append(f"Category: {topic.category}")
                if topic.description:
                    parts.append(f"Topic Description: {topic.description}")

            # Context info
            parts.append(f"Context: {context.name}")
            if context.description:
                parts.append(f"Description: {context.description}")

            # Items and contents
            for item in items:
                parts.append(f"Item {item['item_order']}: {item['content_type']}")
                if item.get("content_title"):
                    parts.append(f"Title: {item['content_title']}")
                if item.get("content_description"):
                    parts.append(f"Description: {item['content_description']}")
                if item.get("content_tags"):
                    parts.append(f"Tags: {item['content_tags']}")
                if item.get("context_hint"):
                    parts.append(f"Context: {item['context_hint']}")

            embedding_text = " ".join(parts)

            # Generate ChromaDB document ID
            chroma_doc_id = f"context_{context_id}"

            # Check if embedding already exists
            existing = self.embedding_repo.get_by_context_id(context_id)

            if existing:
                # Update in ChromaDB
                self.contexts_collection.update(
                    ids=[existing.chroma_doc_id],
                    documents=[embedding_text],
                    metadatas=[
                        {
                            "context_id": context_id,
                            "topic_id": context.topic_id,
                            "context_name": context.name,
                            "description": context.description or "",
                            "topic_name": topic.name if topic else "Unknown",
                            "active": context.active,
                        }
                    ],
                )

                # Update in database
                existing.embedding_text = embedding_text
                self.embedding_repo.update(existing)

                logger.debug("[SUCCESS] Updated embedding for context %s", context_id)
            else:
                # Add to ChromaDB
                self.contexts_collection.add(
                    ids=[chroma_doc_id],
                    documents=[embedding_text],
                    metadatas=[
                        {
                            "context_id": context_id,
                            "topic_id": context.topic_id,
                            "context_name": context.name,
                            "description": context.description or "",
                            "topic_name": topic.name if topic else "Unknown",
                            "active": context.active,
                        }
                    ],
                )

                # Save reference in database
                embedding = ContextEmbedding(
                    context_id=context_id, embedding_text=embedding_text, chroma_doc_id=chroma_doc_id
                )
                self.embedding_repo.create(embedding)

                logger.debug("[SUCCESS] Created embedding for context %s", context_id)

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Failed to generate embedding for context %s: %s", context_id, e, exc_info=True)
            raise

