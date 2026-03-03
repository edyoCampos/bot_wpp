"""
Conversation Service - Business logic for conversation management.

This service orchestrates conversation operations using rich domain entities.
"""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from robbot.core.custom_exceptions import BusinessRuleError, NotFoundException
from robbot.domain.shared.enums import ConversationStatus
from robbot.domain.conversations.mapper import ConversationMapper
from robbot.domain.conversations.conversation import Conversation
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service to manage conversations (business logic).

    Responsibilities:
    - Conversation CRUD operations
    - Status transitions (Domain logic)
    - Transfers and Escalations
    - Conversation closure
    """

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
        self.repo = ConversationRepository(db)

    async def get_or_create(
        self,
        chat_id: str,
        phone_number: str,
        name: str | None = None,
    ) -> ConversationModel:
        """
        Get or create conversation and associated lead.
        Includes LID resolution logic.
        """
        conversation_model = self.repo.get_by_chat_id(chat_id)
        
        if conversation_model:
            # Re-open if closed/completed
            if conversation_model.status in [ConversationStatus.CLOSED, ConversationStatus.COMPLETED]:
                logger.info("[RE-OPEN] Detecting new message on closed conversation %s. Re-opening...", conversation_model.id)
                conversation_model.status = ConversationStatus.ACTIVE_BOT
                conversation_model.closed_at = None
                conversation_model.updated_at = datetime.now(UTC)
                self.db.commit()
                self.db.refresh(conversation_model)
            
            logger.info("[SUCCESS] Conversation found (id=%s, status=%s)", conversation_model.id, conversation_model.status)
            return conversation_model

        # 1. LID Resolution (WhatsApp specific logic)
        resolved_phone = phone_number
        from robbot.services.leads.lid_resolver_service import get_lid_resolver
        lid_resolver = get_lid_resolver()
        
        if lid_resolver.is_lid_format(phone_number):
            try:
                resolved = await lid_resolver.try_resolve_lid(phone_number, timeout_seconds=1.0)
                if resolved:
                    resolved_phone = resolved
                    logger.info("[LID] Phone resolved: %s -> %s", phone_number, resolved_phone)
            except Exception as e:
                logger.debug("[LID] Resolution skipped, will retry later: %s", e)

        # 2. Create Conversation
        conversation_domain = Conversation(
            id=None,
            chat_id=chat_id,
            phone_number=phone_number,
        )
        
        conversation_model = ConversationMapper.to_model(conversation_domain)
        conversation_model.name = name or resolved_phone
        conversation_model = self.repo.create(conversation_model)
        
        # 3. Create Lead
        from robbot.infra.persistence.repositories.lead_repository import LeadRepository
        from robbot.infra.persistence.models.lead_model import LeadModel
        
        lead_repo = LeadRepository(self.db)
        lead = LeadModel(
            phone_number=resolved_phone,
            name=name or resolved_phone,
            maturity_score=0,
            conversation_id=conversation_model.id,
        )
        lead_repo.create(lead)
        self.db.flush()
        
        logger.info("[SUCCESS] Created conversation %s and lead for %s", conversation_model.id, resolved_phone)
        return conversation_model

    def update_status(
        self,
        conversation_id: str,
        new_status: ConversationStatus,
    ) -> ConversationModel:
        """Update conversation status with transition validation."""
        conversation_model = self.repo.get_by_id(conversation_id)
        if not conversation_model:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Map to domain to perform logic
        conversation_domain = ConversationMapper.to_domain(conversation_model)
        
        # Simple transition check (can be expanded in domain entity)
        old_status = conversation_domain.status
        conversation_domain.status = new_status
        
        ConversationMapper.to_model(conversation_domain, conversation_model)
        updated = self.repo.update(conversation_model)

        logger.info("[SUCCESS] Status updated (conv_id=%s, %s → %s)", conversation_id, old_status, new_status)
        return updated

    def close(self, conversation_id: str, reason: str | None = None) -> ConversationModel:
        """Close conversation."""
        conversation_model = self.repo.get_by_id(conversation_id)
        if not conversation_model:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        conversation_domain = ConversationMapper.to_domain(conversation_model)
        conversation_domain.close()
        
        ConversationMapper.to_model(conversation_domain, conversation_model)
        conversation_model.closed_at = datetime.now(UTC)
        updated = self.repo.update(conversation_model)

        logger.info("[SUCCESS] Conversation closed (id=%s, reason=%s)", conversation_id, reason)
        return updated

    def escalate(self, conversation_id: str, reason: str) -> ConversationModel:
        """Escalate conversation to human."""
        conversation_model = self.repo.get_by_id(conversation_id)
        if not conversation_model:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        conversation_domain = ConversationMapper.to_domain(conversation_model)
        conversation_domain.escalate(reason)
        
        ConversationMapper.to_model(conversation_domain, conversation_model)
        conversation_model.escalated_at = datetime.now(UTC)
        conversation_model.escalation_reason = reason
        
        updated = self.repo.update(conversation_model)
        logger.info("[SUCCESS] Conversation escalated (id=%s, reason=%s)", conversation_id, reason)
        return updated

    def get_active_conversations(self, limit: int = 100) -> list[ConversationModel]:
        """Get active conversations."""
        return self.repo.get_active(limit=limit)

    def list_conversations(
        self,
        phone_number: str | None = None,
        status: ConversationStatus | None = None,
        is_urgent: bool | None = None,
        assigned_to_user_id: int | None = None,
        conversation_ids: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ConversationModel], int]:
        """List conversations with filters."""
        filters = {
            "status": status,
            "phone_number": phone_number,
            "is_urgent": is_urgent,
            "assigned_to_user_id": assigned_to_user_id,
            "conversation_ids": conversation_ids
        }
        
        conversations = self.repo.find_by_criteria(filters, limit=limit, offset=offset)
        # For count, we use a separate count method in repo or simple count
        total = self.repo.db.query(ConversationModel).filter_by(**{k: v for k, v in filters.items() if v is not None and k != "conversation_ids"}).count()

        return conversations, total

