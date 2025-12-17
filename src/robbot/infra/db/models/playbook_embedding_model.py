"""PlaybookEmbeddingModel ORM for RAG search integration."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class PlaybookEmbeddingModel(Base):
    """
    PlaybookEmbedding entity storing vector embedding metadata for RAG search.
    
    This table links playbooks to their ChromaDB document representations,
    enabling semantic search for relevant playbooks during conversations.
    """

    __tablename__ = "playbook_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    playbook_id = Column(
        String(36), 
        ForeignKey('playbooks.id', ondelete='CASCADE'), 
        nullable=False, 
        unique=True, 
        index=True
    )
    embedding_text = Column(Text, nullable=False)  # Combined text from playbook + steps for embedding
    chroma_doc_id = Column(String(255), nullable=True, unique=True, index=True)  # ChromaDB document ID
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    playbook = relationship("PlaybookModel", back_populates="embedding")

    def __repr__(self) -> str:
        return f"<PlaybookEmbedding id={self.id} playbook_id={self.playbook_id}>"
