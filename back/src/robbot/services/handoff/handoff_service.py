"""HandoffService - Manages seamless bot→human transition."""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.conversation_repository import ConversationRepository
from robbot.infra.persistence.repositories.lead_repository import LeadRepository
from robbot.core.custom_exceptions import BusinessRuleError, NotFoundException
from robbot.domain.shared.enums import ConversationStatus, LeadStatus
from robbot.infra.persistence.models.conversation_model import ConversationModel

logger = logging.getLogger(__name__)


class HandoffService:
    """
    Service to manage bot→human handoff.

    Responsibilities:
    - Trigger handoff when high score or bot confused
    - Assign conversation to attendant
    - Mark as completed after scheduling
    - Generate natural transition messages
    """

    def __init__(
        self,
        conversation_repo: ConversationRepository,
        lead_repo: LeadRepository,
    ):
        self.conversation_repo = conversation_repo
        self.lead_repo = lead_repo

    async def trigger_handoff(
        self,
        session: Session,
        conversation_id: str,
        reason: str,
        score: int | None = None,
        additional_context: str | None = None,
    ) -> dict:
        """
        Trigger bot→human handoff.

        Args:
            conversation_id: Conversation ID
            reason: Reason (score_high, bot_confused, manual)
            score: Current maturity score
            additional_context: Additional context

        Returns:
            dict with status and transition message
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Validate allowed states
        if conversation.status in [
            ConversationStatus.COMPLETED,
            ConversationStatus.CLOSED,
        ]:
            raise BusinessRuleError(f"Cannot handoff conversation in status {conversation.status}")

        # Update status, reason, and escalation timestamp
        conversation.status = ConversationStatus.PENDING_HANDOFF
        conversation.escalation_reason = reason
        conversation.escalated_at = datetime.now(UTC)
        conversation.updated_at = datetime.now(UTC)

        self.conversation_repo.update(conversation)
        session.flush()

        logger.info("[SUCCESS] Handoff triggered: conv=%s, reason=%s, score=%s", conversation_id, reason, score)

        # Generate natural transition message based on context
        transition_message = self._generate_transition_message(reason, score)

        return {
            "status": "handoff_triggered",
            "conversation_id": conversation_id,
            "reason": reason,
            "message": transition_message,
        }

    async def assign_to_human(
        self,
        session: Session,
        conversation_id: str,
        user_id: str,
    ) -> ConversationModel:
        """
        Assign conversation to human attendant.

        Args:
            conversation_id: Conversation ID
            user_id: Attendant UUID

        Returns:
            Updated conversation
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Validate state
        if conversation.status not in [
            ConversationStatus.PENDING_HANDOFF,
            ConversationStatus.ACTIVE_BOT,
            ConversationStatus.ESCALATED,
        ]:
            raise BusinessRuleError(f"Cannot assign conversation in status {conversation.status}")

        # Assign to attendant
        conversation.status = ConversationStatus.ACTIVE_HUMAN
        conversation.assigned_to = user_id
        conversation.assigned_at = datetime.now(UTC)
        conversation.updated_at = datetime.now(UTC)

        self.conversation_repo.update(conversation)
        session.flush()

        logger.info("[SUCCESS] Conversation assigned: conv=%s, user=%s", conversation_id, user_id)

        return conversation

    async def mark_as_completed(
        self,
        session: Session,
        conversation_id: str,
        user_id: str,
    ) -> dict:
        """
        Mark conversation as completed after scheduling.

        Args:
            conversation_id: Conversation ID
            user_id: UUID of attendant who confirmed

        Returns:
            dict with calculated metrics
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Validate state
        if conversation.status != ConversationStatus.ACTIVE_HUMAN:
            raise BusinessRuleError(
                f"Can only complete conversations in ACTIVE_HUMAN status, got {conversation.status}"
            )

        # Validate assignment
        if conversation.assigned_to != user_id:
            raise BusinessRuleError(
                f"User {user_id} cannot complete conversation assigned to {conversation.assigned_to}"
            )

        # Mark as completed
        conversation.status = ConversationStatus.COMPLETED
        conversation.completed_at = datetime.now(UTC)
        conversation.updated_at = datetime.now(UTC)

        # Update lead to converted
        if conversation.lead:
            lead = self.lead_repo.get_by_id(conversation.lead.id)
            if lead:
                lead.status = LeadStatus.SCHEDULED
                lead.maturity_score = 100
                lead.updated_at = datetime.now(UTC)
                self.lead_repo.update(lead)

        self.conversation_repo.update(conversation)
        session.flush()

        # Calculate metrics
        metrics = self._calculate_metrics(conversation)

        logger.info("[SUCCESS] Conversation completed: conv=%s, metrics=%s", conversation_id, metrics)

        return {
            "status": "completed",
            "conversation_id": conversation_id,
            "metrics": metrics,
        }

    def _generate_transition_message(self, reason: str, score: int | None = None) -> str:
        """Generates natural transition message based on context."""
        messages = {
            "score_high": (
                "Vejo que você está bem interessado! 🎯\n\n"
                "Vou transferir você para nossa equipe de agendamento "
                "que vai conseguir te ajudar melhor com horários e detalhes finais. "
                "Aguarde só um momento, ok?"
            ),
            "bot_confused": (
                "Entendo que você precisa de uma orientação mais específica. "
                "Vou te conectar com alguém da equipe que pode te ajudar "
                "melhor nessa situação. Aguarde só um instante."
            ),
            "manual": (
                "Um de nossos atendentes vai assumir essa conversa agora "
                "para te dar um atendimento mais personalizado. 👤"
            ),
        }

        return messages.get(
            reason,
            "Vou transferir você para um atendente humano. Aguarde um momento.",
        )

    def _calculate_metrics(self, conversation: ConversationModel) -> dict:
        """Calculates conversion metrics."""
        metrics = {}

        # Total conversation time
        if conversation.created_at and conversation.completed_at:
            total_time = conversation.completed_at - conversation.created_at
            metrics["total_conversation_time_minutes"] = int(total_time.total_seconds() / 60)

        # Time to handoff
        if conversation.created_at and conversation.assigned_at:
            handoff_time = conversation.assigned_at - conversation.created_at
            metrics["time_to_handoff_minutes"] = int(handoff_time.total_seconds() / 60)

        # Human interaction time
        if conversation.assigned_at and conversation.completed_at:
            human_time = conversation.completed_at - conversation.assigned_at
            metrics["human_interaction_time_minutes"] = int(human_time.total_seconds() / 60)

        # Final score
        if conversation.lead and conversation.lead.maturity_score:
            metrics["final_score"] = conversation.lead.maturity_score

        # Escalation reason
        if conversation.escalation_reason:
            metrics["escalation_reason"] = conversation.escalation_reason

        return metrics

    async def return_to_bot(
        self,
        session: Session,
        conversation_id: str,
        user_id: str,
    ) -> ConversationModel:
        """
        Returns conversation to bot (if human decides).

        Args:
            conversation_id: Conversation ID
            user_id: UUID of attendant returning the chat

        Returns:
            Updated conversation
        """
        conversation = self.conversation_repo.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")

        # Validate state and assignment
        if conversation.status != ConversationStatus.ACTIVE_HUMAN:
            raise BusinessRuleError("Can only return conversations in ACTIVE_HUMAN status")

        if conversation.assigned_to != user_id:
            raise BusinessRuleError(f"User {user_id} cannot return conversation assigned to {conversation.assigned_to}")

        # Return to bot
        conversation.status = ConversationStatus.ACTIVE_BOT
        conversation.assigned_to = None
        conversation.assigned_at = None
        conversation.escalation_reason = None
        conversation.updated_at = datetime.now(UTC)

        self.conversation_repo.update(conversation)
        session.flush()

        logger.info("[SUCCESS] Conversation returned to bot: conv=%s, by_user=%s", conversation_id, user_id)

        return conversation

