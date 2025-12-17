"""PlaybookService orchestrating playbook business logic and RAG search."""

import logging
from typing import Optional
from uuid import UUID

import chromadb
from chromadb.config import Settings as ChromaSettings
from sqlalchemy.orm import Session

from robbot.adapters.repositories.message_repository import MessageRepository
from robbot.adapters.repositories.playbook_embedding_repository import PlaybookEmbeddingRepository
from robbot.adapters.repositories.playbook_repository import PlaybookRepository
from robbot.adapters.repositories.playbook_step_repository import PlaybookStepRepository
from robbot.adapters.repositories.topic_repository import TopicRepository
from robbot.config.settings import get_settings
from robbot.core.exceptions import NotFoundException
from robbot.domain.entities.playbook import Playbook
from robbot.domain.entities.playbook_embedding import PlaybookEmbedding
from robbot.domain.entities.playbook_step import PlaybookStep
from robbot.domain.entities.topic import Topic
from robbot.infra.db.models.message_model import MessageModel
from robbot.schemas.playbook import PlaybookSearchResult

logger = logging.getLogger(__name__)
settings = get_settings()


class PlaybookService:
    """
    Service layer for playbook operations with RAG semantic search.
    
    Responsibilities:
    - CRUD operations for topics, playbooks, steps
    - Semantic search using ChromaDB embeddings
    - Automatic indexing when playbooks are created/updated
    - Retrieve playbook steps with message details for LLM
    """

    def __init__(self, db: Session):
        self.db = db
        self.topic_repo = TopicRepository(db)
        self.playbook_repo = PlaybookRepository(db)
        self.step_repo = PlaybookStepRepository(db)
        self.embedding_repo = PlaybookEmbeddingRepository(db)
        self.message_repo = MessageRepository(db)
        
        # ChromaDB client for semantic search
        try:
            self.chroma_client = chromadb.Client(
                ChromaSettings(
                    persist_directory=settings.CHROMA_PERSIST_DIR,
                    anonymized_telemetry=False,
                )
            )
            self.playbooks_collection = self.chroma_client.get_or_create_collection(
                name="playbooks",
                metadata={"hnsw:space": "cosine", "description": "Playbook embeddings for semantic search"}
            )
            logger.info(f"✓ PlaybookService initialized (playbooks count={self.playbooks_collection.count()})")
        except Exception as e:
            logger.error(f"✗ Failed to initialize ChromaDB for playbooks: {e}")
            raise

    # ===== TOPIC OPERATIONS =====

    def create_topic(self, topic: Topic) -> Topic:
        """Create a new topic."""
        return self.topic_repo.create(topic)

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        """Get topic by ID."""
        return self.topic_repo.get_by_id(topic_id)

    def list_topics(self, active_only: bool = False, skip: int = 0, limit: int = 100) -> list[Topic]:
        """List all topics."""
        return self.topic_repo.list_all(active_only=active_only, skip=skip, limit=limit)

    def update_topic(self, topic_id: str, **kwargs) -> Optional[Topic]:
        """Update topic fields."""
        return self.topic_repo.update(topic_id, **kwargs)

    def delete_topic(self, topic_id: str) -> bool:
        """Delete topic (cascades to playbooks)."""
        return self.topic_repo.delete(topic_id)

    # ===== PLAYBOOK OPERATIONS =====

    def create_playbook(self, playbook: Playbook) -> Playbook:
        """Create playbook and auto-index for semantic search."""
        # Create playbook
        created = self.playbook_repo.create(playbook)
        
        # Auto-generate embedding (will be populated when steps are added)
        try:
            self._generate_playbook_embedding(created.id)
            logger.info(f"✓ Playbook {created.id} created and indexed")
        except Exception as e:
            logger.warning(f"⚠️ Playbook created but indexing failed: {e}")
        
        return created

    def get_playbook(self, playbook_id: str) -> Optional[Playbook]:
        """Get playbook by ID."""
        return self.playbook_repo.get_by_id(playbook_id)

    def list_playbooks_by_topic(self, topic_id: str, active_only: bool = False) -> list[Playbook]:
        """List playbooks by topic."""
        return self.playbook_repo.list_by_topic(topic_id, active_only=active_only)

    def update_playbook(self, playbook_id: str, **kwargs) -> Optional[Playbook]:
        """Update playbook and reindex."""
        updated = self.playbook_repo.update(playbook_id, **kwargs)
        if updated:
            try:
                self._generate_playbook_embedding(playbook_id)
                logger.info(f"✓ Playbook {playbook_id} updated and reindexed")
            except Exception as e:
                logger.warning(f"⚠️ Playbook updated but reindexing failed: {e}")
        return updated

    def delete_playbook(self, playbook_id: str) -> bool:
        """Delete playbook (cascades to steps and removes from ChromaDB)."""
        # Remove from ChromaDB first
        embedding = self.embedding_repo.get_by_playbook_id(playbook_id)
        if embedding and embedding.chroma_doc_id:
            try:
                self.playbooks_collection.delete(ids=[embedding.chroma_doc_id])
                logger.info(f"✓ Removed playbook {playbook_id} from ChromaDB")
            except Exception as e:
                logger.warning(f"⚠️ Failed to remove from ChromaDB: {e}")
        
        # Delete from database (cascades)
        return self.playbook_repo.delete(playbook_id)

    # ===== PLAYBOOK STEP OPERATIONS =====

    def add_step(self, step: PlaybookStep) -> PlaybookStep:
        """Add step to playbook and reindex."""
        # Auto-assign order if not provided
        if not step.step_order:
            step.step_order = self.step_repo.get_next_order(step.playbook_id)
        
        created = self.step_repo.create(step)
        
        # Reindex playbook
        try:
            self._generate_playbook_embedding(step.playbook_id)
            logger.info(f"✓ Step added to playbook {step.playbook_id}, reindexed")
        except Exception as e:
            logger.warning(f"⚠️ Step added but reindexing failed: {e}")
        
        return created

    def get_playbook_steps(self, playbook_id: str, include_messages: bool = False) -> list[PlaybookStep]:
        """Get all steps for a playbook in order."""
        return self.step_repo.list_by_playbook(playbook_id, include_messages=include_messages)

    def get_playbook_steps_with_details(self, playbook_id: str) -> list[dict]:
        """
        Get playbook steps with full message details for LLM.
        
        Returns list of dicts with step + message information:
        {
            "step_order": 1,
            "step_id": "step_123",
            "context_hint": "Use when client asks about price",
            "message_id": "msg_456",
            "message_type": "document",
            "message_title": "Botox Price Table",
            "message_description": "PDF with all botox pricing...",
            "message_tags": "botox, price, table",
            "message_text": "...",  # For text messages
            "message_caption": "...",  # For media
            "media_url": "..."  # For media/document
        }
        """
        steps = self.step_repo.list_by_playbook(playbook_id, include_messages=True)
        result = []
        
        for step in steps:
            # Get message details
            msg = self.message_repo.get_by_id(UUID(step.message_id))
            if not msg:
                logger.warning(f"⚠️ Message {step.message_id} not found for step {step.id}")
                continue
            
            step_data = {
                "step_order": step.step_order,
                "step_id": step.id,
                "context_hint": step.context_hint,
                "message_id": step.message_id,
                "message_type": msg.type,
                "message_title": msg.title,
                "message_description": msg.description,
                "message_tags": msg.tags,
            }
            
            # Add type-specific fields
            if msg.type == "text":
                step_data["message_text"] = msg.text
            elif msg.type in ("image", "voice", "video", "document"):
                step_data["message_caption"] = msg.caption
                if msg.media and len(msg.media) > 0:
                    step_data["media_url"] = msg.media[0].url
                    step_data["media_mimetype"] = msg.media[0].mimetype
                    step_data["media_filename"] = msg.media[0].filename
            elif msg.type == "location":
                if msg.location:
                    step_data["latitude"] = msg.location.latitude
                    step_data["longitude"] = msg.location.longitude
                    step_data["location_title"] = msg.location.title
            
            result.append(step_data)
        
        return result

    def reorder_steps(self, playbook_id: str, step_id_order: list[tuple[str, int]]) -> bool:
        """Reorder multiple steps at once."""
        return self.step_repo.reorder_steps(playbook_id, step_id_order)

    def delete_step(self, step_id: str) -> bool:
        """Delete step and reindex playbook."""
        step = self.step_repo.get_by_id(step_id)
        if not step:
            return False
        
        playbook_id = step.playbook_id
        success = self.step_repo.delete(step_id)
        
        if success:
            try:
                self._generate_playbook_embedding(playbook_id)
                logger.info(f"✓ Step deleted from playbook {playbook_id}, reindexed")
            except Exception as e:
                logger.warning(f"⚠️ Step deleted but reindexing failed: {e}")
        
        return success

    # ===== SEMANTIC SEARCH (RAG) =====

    def search_playbooks(self, query: str, top_k: int = 3, active_only: bool = True) -> list[PlaybookSearchResult]:
        """
        Semantic search for relevant playbooks using ChromaDB.
        
        Args:
            query: Natural language query (e.g., "botox preço procedimento")
            top_k: Number of results to return
            active_only: Only return active playbooks
            
        Returns:
            List of PlaybookSearchResult with relevance scores
        """
        try:
            # Query ChromaDB
            where_filter = {"active": True} if active_only else None
            results = self.playbooks_collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter
            )
            
            if not results['ids'][0]:
                logger.info(f"No playbooks found for query: {query}")
                return []
            
            # Format results
            playbook_results = []
            for i, chroma_doc_id in enumerate(results['ids'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                playbook_results.append(PlaybookSearchResult(
                    playbook_id=metadata['playbook_id'],
                    name=metadata['playbook_name'],
                    description=metadata.get('description'),
                    topic_name=metadata.get('topic_name', 'Unknown'),
                    relevance_score=round(1 - distance, 3)  # Convert distance to similarity score
                ))
            
            logger.info(f"✓ Found {len(playbook_results)} playbooks for query: {query}")
            return playbook_results
            
        except Exception as e:
            logger.error(f"✗ Semantic search failed for query '{query}': {e}", exc_info=True)
            return []

    # ===== PRIVATE METHODS =====

    def _generate_playbook_embedding(self, playbook_id: str) -> None:
        """
        Generate and store embedding for a playbook.
        
        Combines playbook metadata + step descriptions into rich text for embedding.
        """
        try:
            # Get playbook and related data
            playbook = self.playbook_repo.get_by_id(playbook_id)
            if not playbook:
                raise NotFoundException(f"Playbook {playbook_id} not found")
            
            topic = self.topic_repo.get_by_id(playbook.topic_id)
            steps = self.get_playbook_steps_with_details(playbook_id)
            
            # Build rich embedding text
            parts = []
            
            # Topic context
            if topic:
                parts.append(f"Topic: {topic.name}")
                if topic.category:
                    parts.append(f"Category: {topic.category}")
                if topic.description:
                    parts.append(f"Topic Description: {topic.description}")
            
            # Playbook info
            parts.append(f"Playbook: {playbook.name}")
            if playbook.description:
                parts.append(f"Description: {playbook.description}")
            
            # Steps and messages
            for step in steps:
                parts.append(f"Step {step['step_order']}: {step['message_type']}")
                if step.get('message_title'):
                    parts.append(f"Title: {step['message_title']}")
                if step.get('message_description'):
                    parts.append(f"Description: {step['message_description']}")
                if step.get('message_tags'):
                    parts.append(f"Tags: {step['message_tags']}")
                if step.get('context_hint'):
                    parts.append(f"Context: {step['context_hint']}")
            
            embedding_text = " ".join(parts)
            
            # Generate ChromaDB document ID
            chroma_doc_id = f"playbook_{playbook_id}"
            
            # Check if embedding already exists
            existing = self.embedding_repo.get_by_playbook_id(playbook_id)
            
            if existing:
                # Update in ChromaDB
                self.playbooks_collection.update(
                    ids=[existing.chroma_doc_id],
                    documents=[embedding_text],
                    metadatas=[{
                        "playbook_id": playbook_id,
                        "topic_id": playbook.topic_id,
                        "playbook_name": playbook.name,
                        "description": playbook.description or "",
                        "topic_name": topic.name if topic else "Unknown",
                        "active": playbook.active
                    }]
                )
                
                # Update in database
                self.embedding_repo.update(
                    playbook_id=playbook_id,
                    embedding_text=embedding_text
                )
                
                logger.debug(f"✓ Updated embedding for playbook {playbook_id}")
            else:
                # Add to ChromaDB
                self.playbooks_collection.add(
                    ids=[chroma_doc_id],
                    documents=[embedding_text],
                    metadatas=[{
                        "playbook_id": playbook_id,
                        "topic_id": playbook.topic_id,
                        "playbook_name": playbook.name,
                        "description": playbook.description or "",
                        "topic_name": topic.name if topic else "Unknown",
                        "active": playbook.active
                    }]
                )
                
                # Save reference in database
                embedding = PlaybookEmbedding(
                    playbook_id=playbook_id,
                    embedding_text=embedding_text,
                    chroma_doc_id=chroma_doc_id
                )
                self.embedding_repo.create(embedding)
                
                logger.debug(f"✓ Created embedding for playbook {playbook_id}")
                
        except Exception as e:
            logger.error(f"✗ Failed to generate embedding for playbook {playbook_id}: {e}", exc_info=True)
            raise
