"""
Response Dispatcher - Handles delivery and logging of robot responses.
"""

import logging
from typing import Any
from sqlalchemy.orm import Session

from robbot.infra.integrations.waha.waha_client import WAHAClient
from robbot.infra.persistence.repositories.lead_interaction_repository import LeadInteractionRepository
from robbot.infra.persistence.repositories.llm_interaction_repository import LLMInteractionRepository
from robbot.domain.shared.enums import InteractionType
from robbot.infra.persistence.models.lead_interaction_model import LeadInteractionModel
from robbot.infra.persistence.models.llm_interaction_model import LLMInteractionModel
from robbot.services.communication.message_processor import MessageProcessor

logger = logging.getLogger(__name__)


class ResponseDispatcher:
    """
    Coordinates delivering responses and persisting interaction logs.
    """
    def __init__(self, session: Session, waha_client: WAHAClient):
        self.session = session
        self.waha_client = waha_client
        self.message_processor = MessageProcessor(session, None) # transcription not needed for outbound
        self.lead_interaction_repo = LeadInteractionRepository(session)
        self.llm_interaction_repo = LLMInteractionRepository(session)

    async def dispatch(
        self,
        conversation_id: str,
        chat_id: str,
        phone_number: str,
        lead_id: str | None,
        response_text: str,
        intent: str,
        message_text: str, # original user message for logging
        response_data: dict[str, Any], # LLM metadata (tokens, latency)
        session_name: str = "default"
    ) -> bool:
        """
        Send response via WAHA and record all logs.
        """
        # 1. Send via WAHA
        sent = False
        try:
            await self.waha_client.send_text(chat_id=chat_id, text=response_text, session=session_name)
            sent = True
            logger.info("[SUCCESS] Response sent via WAHA (chat_id=%s)", chat_id)
        except Exception as e:
            logger.error("[ERROR] Failed to send via WAHA: %s", e)
            # We continue to save the message to DB even if WAHA failed - it marks intent was to send

        # 2. Save outbound message to DB
        await self.message_processor.save_outbound_message(
            self.session, conversation_id, response_text, to_phone=phone_number
        )

        # 3. Register Interaction
        await self._register_interaction(lead_id, intent, message_text, response_text)

        # 4. Log LLM interaction
        await self._log_llm_interaction(
            conversation_id,
            f"Intent: {intent} | Msg: {message_text[:100]}",
            response_text[:200],
            response_data.get("tokens_used", 0),
            response_data.get("latency_ms", 0),
        )

        return sent

    async def _register_interaction(self, lead_id: str | None, intent: str, inbound: str, outbound: str):
        if not lead_id:
            return
        
        type_map = {
            "INTERESSE_TRATAMENTO": InteractionType.MESSAGE,
            "AGENDAMENTO": InteractionType.MEETING,
            "URGENCIA_DOR": InteractionType.CALL,
        }
        
        interaction = LeadInteractionModel(
            lead_id=lead_id,
            interaction_type=type_map.get(intent, InteractionType.MESSAGE),
            notes=f"Inbound: {inbound[:50]}... | Outbound: {outbound[:50]}...",
        )
        self.lead_interaction_repo.create(interaction)

    async def _log_llm_interaction(self, conv_id: str, prompt: str, resp: str, tokens: int, latency: int):
        interaction = LLMInteractionModel(
            conversation_id=conv_id,
            prompt=prompt,
            response=resp,
            model_name="gemini-1.5-pro",
            tokens_used=tokens,
            latency_ms=latency,
        )
        self.llm_interaction_repo.create(interaction)

