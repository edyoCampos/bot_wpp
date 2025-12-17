"""Repository for LLMInteraction entity."""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from robbot.domain.entities.llm_interaction import LLMInteraction
from robbot.infra.db.models.llm_interaction_model import LLMInteractionModel

logger = logging.getLogger(__name__)


class LLMInteractionRepository:
    """Repository for LLM interactions CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with database session."""
        self.session = session

    def create(self, interaction: LLMInteraction) -> LLMInteraction:
        """
        Create new LLM interaction.
        
        Args:
            interaction: LLMInteraction entity
            
        Returns:
            Created entity with ID
        """
        # Criar model com campos que existem no banco
        model = LLMInteractionModel(
            id=interaction.id,
            conversation_id=interaction.conversation_id,
            prompt=interaction.prompt_text,  # Banco usa 'prompt' não 'prompt_text'
            response=interaction.response_text,  # Banco usa 'response' não 'response_text'
            model_name="gemini-1.5-flash",  # Campo obrigatório
            tokens_used=interaction.tokens_used,
            latency_ms=interaction.latency_ms,
            created_at=interaction.timestamp or datetime.now(timezone.utc),
        )
        
        self.session.add(model)
        self.session.flush()
        
        logger.info(f"✓ LLMInteraction created (id={model.id})")
        
        return self._to_entity(model)

    def get_by_id(self, interaction_id: str) -> Optional[LLMInteraction]:
        """
        Get LLM interaction by ID.
        
        Args:
            interaction_id: Interaction ID
            
        Returns:
            LLMInteraction or None
        """
        model = self.session.query(LLMInteractionModel).filter_by(id=interaction_id).first()
        
        if model:
            return self._to_entity(model)
        
        return None

    def get_by_conversation(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> list[LLMInteraction]:
        """
        Get interactions by conversation ID.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of interactions
            
        Returns:
            List of interactions ordered by timestamp
        """
        models = (
            self.session.query(LLMInteractionModel)
            .filter_by(conversation_id=conversation_id)
            .order_by(LLMInteractionModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        return [self._to_entity(m) for m in models]

    def get_all(self) -> list[LLMInteraction]:
        """
        Get all LLM interactions.
        
        Returns:
            List of all interactions
        """
        models = self.session.query(LLMInteractionModel).all()
        return [self._to_entity(m) for m in models]

    def update(self, interaction: LLMInteraction) -> LLMInteraction:
        """
        Update existing LLM interaction.
        
        Args:
            interaction: LLMInteraction entity
            
        Returns:
            Updated entity
        """
        model = self.session.query(LLMInteractionModel).filter_by(id=interaction.id).first()
        
        if not model:
            raise ValueError(f"LLMInteraction {interaction.id} not found")
        
        model.prompt = interaction.prompt_text
        model.response = interaction.response_text
        model.tokens_used = interaction.tokens_used
        model.latency_ms = interaction.latency_ms
        model.created_at = interaction.timestamp
        
        self.session.flush()
        
        logger.info(f"✓ LLMInteraction updated (id={interaction.id})")
        
        return self._to_entity(model)

    def delete(self, interaction_id: str) -> bool:
        """
        Delete LLM interaction.
        
        Args:
            interaction_id: Interaction ID
            
        Returns:
            True if deleted, False if not found
        """
        model = self.session.query(LLMInteractionModel).filter_by(id=interaction_id).first()
        
        if not model:
            return False
        
        self.session.delete(model)
        self.session.flush()
        
        logger.info(f"✓ LLMInteraction deleted (id={interaction_id})")
        
        return True

    def _to_entity(self, model: LLMInteractionModel) -> LLMInteraction:
        """Convert model to entity."""
        # Usar campos do banco real: prompt, response, tokens_used, created_at
        return LLMInteraction(
            id=model.id,
            conversation_id=model.conversation_id,
            prompt_text=model.prompt,
            response_text=model.response,
            tokens_used=model.tokens_used or 0,
            latency_ms=model.latency_ms or 0,
            timestamp=model.created_at,
        )
