"""Repository for playbook_embedding persistence and retrieval operations."""

from typing import Optional

from sqlalchemy.orm import Session

from robbot.domain.entities.playbook_embedding import PlaybookEmbedding
from robbot.infra.db.models.playbook_embedding_model import PlaybookEmbeddingModel


class PlaybookEmbeddingRepository:
    """Repository encapsulating DB access for playbook embeddings."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, embedding: PlaybookEmbedding) -> PlaybookEmbedding:
        """Create a new playbook embedding."""
        model = PlaybookEmbeddingModel(
            id=embedding.id,
            playbook_id=embedding.playbook_id,
            embedding_text=embedding.embedding_text,
            chroma_doc_id=embedding.chroma_doc_id,
            created_at=embedding.created_at,
            updated_at=embedding.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def get_by_playbook_id(self, playbook_id: str) -> Optional[PlaybookEmbedding]:
        """Retrieve embedding by playbook ID."""
        model = self.db.query(PlaybookEmbeddingModel).filter(
            PlaybookEmbeddingModel.playbook_id == playbook_id
        ).first()
        return self._to_entity(model) if model else None

    def get_by_chroma_id(self, chroma_doc_id: str) -> Optional[PlaybookEmbedding]:
        """Retrieve embedding by ChromaDB document ID."""
        model = self.db.query(PlaybookEmbeddingModel).filter(
            PlaybookEmbeddingModel.chroma_doc_id == chroma_doc_id
        ).first()
        return self._to_entity(model) if model else None

    def update(self, playbook_id: str, **kwargs) -> Optional[PlaybookEmbedding]:
        """Update embedding fields."""
        model = self.db.query(PlaybookEmbeddingModel).filter(
            PlaybookEmbeddingModel.playbook_id == playbook_id
        ).first()
        if not model:
            return None
        
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, playbook_id: str) -> bool:
        """Delete playbook embedding."""
        model = self.db.query(PlaybookEmbeddingModel).filter(
            PlaybookEmbeddingModel.playbook_id == playbook_id
        ).first()
        if not model:
            return False
        
        self.db.delete(model)
        self.db.commit()
        return True

    def _to_entity(self, model: PlaybookEmbeddingModel) -> PlaybookEmbedding:
        """Convert model to domain entity."""
        return PlaybookEmbedding(
            id=model.id,
            playbook_id=model.playbook_id,
            embedding_text=model.embedding_text,
            chroma_doc_id=model.chroma_doc_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
