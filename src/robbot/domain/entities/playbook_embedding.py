"""PlaybookEmbedding domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class PlaybookEmbedding:
    """
    PlaybookEmbedding entity for RAG search integration.
    
    Stores metadata linking playbooks to their vector embeddings
    in ChromaDB for semantic search.
    
    Attributes:
        id: Unique embedding ID
        playbook_id: Associated playbook ID
        embedding_text: Combined text used for embedding
        chroma_doc_id: ChromaDB document ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    playbook_id: str
    embedding_text: str
    chroma_doc_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
