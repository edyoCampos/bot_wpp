"""PlaybookEmbeddingModel ORM for RAG search integration."""

from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class ContextEmbeddingModel(Base):
    """
    ContextEmbedding entity storing vector embedding metadata for RAG search.
    """

    __tablename__ = "context_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    context_id = Column(
        String(36), ForeignKey("contexts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    embedding_text = Column(Text, nullable=False)  # Combined text from playbook + steps for embedding
    chroma_doc_id = Column(String(255), nullable=True, unique=True, index=True)  # ChromaDB document ID
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    context = relationship("ContextModel", back_populates="embedding")

    def __repr__(self) -> str:
        return f"<ContextEmbedding id={self.id} context_id={self.context_id}>"
