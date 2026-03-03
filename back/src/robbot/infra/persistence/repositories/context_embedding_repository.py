"""Repository for context_embedding persistence and retrieval operations."""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.context_embedding_model import ContextEmbeddingModel


class ContextEmbeddingRepository(BaseRepository[ContextEmbeddingModel]):
    """Repository encapsulating DB access for context embeddings."""

    def __init__(self, db: Session):
        super().__init__(db, ContextEmbeddingModel)

    def get_by_context_id(self, context_id: str) -> ContextEmbeddingModel | None:
        """Retrieve embedding by context ID."""
        return self.db.query(ContextEmbeddingModel).filter(ContextEmbeddingModel.context_id == context_id).first()

    def get_by_chroma_id(self, chroma_doc_id: str) -> ContextEmbeddingModel | None:
        """Retrieve embedding by ChromaDB document ID."""
        return (
            self.db.query(ContextEmbeddingModel).filter(ContextEmbeddingModel.chroma_doc_id == chroma_doc_id).first()
        )

