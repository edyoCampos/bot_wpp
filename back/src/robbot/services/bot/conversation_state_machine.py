"""
ConversationStateMachine - Manages conversation state transitions and lead lifecycle.

Extracted from ConversationOrchestrator (Issue #7: God Object Decomposition)

Responsibilities:
- Track conversation status (ACTIVE, CLOSED, etc)
- Update lead maturity score
- Detect escalation triggers
- Manage conversation state transitions
"""

import logging

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.conversation_repository import ConversationRepository
from robbot.infra.persistence.repositories.lead_repository import LeadRepository
from robbot.core.custom_exceptions import BusinessRuleError, NotFoundException
from robbot.domain.shared.enums import (
    ConversationStatus,
    IntentType,
    LeadStatus,
)
from robbot.infra.persistence.models.conversation_model import ConversationModel

logger = logging.getLogger(__name__)

# Score thresholds for state transitions
MATURITY_THRESHOLD_ENGAGED = 25
MATURITY_THRESHOLD_INTERESTED = 40
MATURITY_THRESHOLD_READY = 70
URGENCY_SCORE_INCREMENT = 20
INTENT_SCORE_INCREMENT = 15


class ConversationStateMachine:
    """
    Manage conversation state transitions and lead maturity progression.

    Replaces ConversationOrchestrator state management logic.
    """

    def __init__(self, db: Session):
        """
        Initialize state machine with dependencies.

        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.lead_repo = LeadRepository(db)
        self.conversation_repo = ConversationRepository(db)

    async def update_lead_maturity(
        self,
        conversation: ConversationModel,
        detected_intent: IntentType,
        is_urgent: bool = False,
    ) -> tuple[int, LeadStatus]:
        """
        Update lead maturity score based on detected intent and urgency.

        Transitions lead through SPIN selling phases:
        - 0-25: SITUATION (new inquiries)
        - 25-40: PROBLEM (pain points identified)
        - 40-70: IMPLICATION (exploring impact)
        - 70+: NEED-PAYOFF (ready to convert)

        Args:
            conversation: Conversation context
            detected_intent: Detected intent category
            is_urgent: Whether message indicates urgency

        Returns:
            Tuple of (new_score, new_status)

        Raises:
            NotFoundException: If lead not found
        """
        try:
            lead = conversation.lead
            if not lead:
                raise NotFoundException(f"Lead not found for conversation {conversation.id}")

            # Calculate score increment based on intent
            score_increment = self._get_intent_score(detected_intent)

            # Add urgency bonus
            if is_urgent:
                score_increment += URGENCY_SCORE_INCREMENT

            # Update score (capped at 100)
            old_score = lead.maturity_score
            new_score = min(old_score + score_increment, 100)

            # Determine new status based on score
            new_status = self._get_lead_status(new_score)

            # Update lead
            lead.maturity_score = new_score
            lead.status = new_status

            self.lead_repo.update(obj=lead)
            self.db.flush()

            logger.info(
                "[SUCCESS] Lead maturity updated (id=%s, %d -> %d, status=%s)",
                lead.id,
                old_score,
                new_score,
                new_status,
            )

            return new_score, new_status

        except Exception as e:
            logger.error("[ERROR] Failed to update lead maturity: %s", e)
            raise

    async def check_escalation_needed(
        self,
        conversation: ConversationModel,
        maturity_score: int,
        detected_intent: IntentType,
    ) -> bool:
        """
        Check if conversation needs escalation to human agent.

        Escalation triggers:
        - Maturity score > 70 (ready to schedule)
        - Urgent medical concern detected
        - Customer frustration/repeated questions
        - Explicit request for human

        Args:
            conversation: Conversation context
            maturity_score: Current maturity score
            detected_intent: Detected intent

        Returns:
            True if escalation needed
        """
        # Trigger 1: High maturity (ready to convert)
        if maturity_score > MATURITY_THRESHOLD_READY:
            logger.info(
                "[ESCALATION] High maturity score: %d (conversation_id=%s)",
                maturity_score,
                conversation.id,
            )
            return True

        # Trigger 2: Urgent medical concern
        if detected_intent == IntentType.URGENCIA_DOR:
            logger.info(
                "[ESCALATION] Urgent medical concern detected (conversation_id=%s)",
                conversation.id,
            )
            return True

        # Trigger 3: Customer explicitly requested human
        if detected_intent == IntentType.ESCALACAO_SOLICITADA:
            logger.info(
                "[ESCALATION] Customer requested escalation (conversation_id=%s)",
                conversation.id,
            )
            return True

        # Trigger 4: Problem/complaint
        if detected_intent == IntentType.RECLAMACAO_PROBLEMA:
            logger.warning(
                "[ESCALATION] Customer complaint detected (conversation_id=%s)",
                conversation.id,
            )
            return True

        return False

    async def close_conversation(
        self,
        conversation: ConversationModel,
        reason: str = "completed",
    ) -> ConversationModel:
        """
        Close conversation with reason tracking.

        Args:
            conversation: Conversation to close
            reason: Reason for closing (completed, transferred, timeout, etc)

        Returns:
            Updated conversation

        Raises:
            BusinessRuleError: If conversation already closed
        """
        if conversation.status == ConversationStatus.CLOSED:
            raise BusinessRuleError(f"Conversation {conversation.id} is already closed")

        # Update status
        conversation.status = ConversationStatus.CLOSED
        conversation.close_reason = reason

        updated = self.conversation_repo.update(obj=conversation)
        self.db.flush()

        logger.info(
            "[SUCCESS] Conversation closed (id=%s, reason=%s)",
            conversation.id,
            reason,
        )

        return updated

    @staticmethod
    def _get_intent_score(intent: IntentType) -> int:
        """
        Get score increment for detected intent.

        Args:
            intent: Detected intent type

        Returns:
            Score increment (0-25)
        """
        intent_scores = {
            IntentType.INTERESSE_TRATAMENTO: INTENT_SCORE_INCREMENT,
            IntentType.DUVIDA_PROCEDIMENTO: INTENT_SCORE_INCREMENT,
            IntentType.PRECO_VALOR: INTENT_SCORE_INCREMENT,
            IntentType.LOCALIZACAO_HORARIO: INTENT_SCORE_INCREMENT + 10,  # Scheduling = higher score
            IntentType.URGENCIA_DOR: URGENCY_SCORE_INCREMENT,
            IntentType.RESULTADO_TEMPO: INTENT_SCORE_INCREMENT,
            IntentType.COMPARACAO_OPCOES: INTENT_SCORE_INCREMENT,
            IntentType.AGENDAMENTO: INTENT_SCORE_INCREMENT + 15,  # Ready to schedule
            IntentType.RECLAMACAO_PROBLEMA: 0,  # No score increase for complaints
            IntentType.OUTRO: 5,  # Small increment for general conversation
        }

        return intent_scores.get(intent, 0)

    @staticmethod
    def _get_lead_status(score: int) -> LeadStatus:
        """
        Determine lead status based on maturity score.

        Args:
            score: Maturity score (0-100)

        Returns:
            Corresponding LeadStatus
        """
        if score < MATURITY_THRESHOLD_ENGAGED:
            return LeadStatus.NEW
        elif score < MATURITY_THRESHOLD_INTERESTED:
            return LeadStatus.ENGAGED
        elif score < MATURITY_THRESHOLD_READY:
            return LeadStatus.INTERESTED
        else:
            return LeadStatus.READY

