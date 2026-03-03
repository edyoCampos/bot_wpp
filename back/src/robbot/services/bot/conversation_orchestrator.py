"""
Conversation Orchestrator - COORDINATOR ONLY.

Delegates to:
- ConversationService: for state and lifecycle
- ConversationPipeline: for message analysis and context
- ResponseDispatcher: for sending and logging
"""

import logging
from typing import Any

from robbot.infra.integrations.vector_store.chroma_vector_store import ChromaVectorStore
from robbot.infra.integrations.llm.llm_client import get_llm_client
from robbot.infra.integrations.waha.waha_client import WAHAClient
from robbot.config.prompts import get_prompt_templates
from robbot.core.custom_exceptions import BusinessRuleError
from robbot.domain.shared.enums import ConversationStatus
from robbot.infra.db.session import get_sync_session
from robbot.services.ai.answered_questions import AnsweredQuestionsMemory
from robbot.services.bot.conversation_service import ConversationService
from robbot.services.bot.conversation_pipeline import ConversationPipeline, PipelineState
from robbot.services.bot.response_dispatcher import ResponseDispatcher
from robbot.services.ai.persistent_memory import PersistentMemory
from robbot.core.text_sanitizer import enforce_whatsapp_style
from robbot.services.communication.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """
    Lean orchestrator that coordinates specialized services.
    """

    def __init__(self):
        self.llm = get_llm_client()
        self.prompt_templates = get_prompt_templates()
        self.waha_client = WAHAClient()
        self.transcription_service = TranscriptionService()
        self.vector_store = ChromaVectorStore()
        self.answered_questions_memory = AnsweredQuestionsMemory()
        self.persistent_memory = PersistentMemory()

        logger.info("[SUCCESS] Decomposed ConversationOrchestrator initialized")

    async def process_inbound_message(
        self,
        chat_id: str,
        phone_number: str,
        message_text: str,
        session_name: str = "default",
        **media_kwargs
    ) -> dict[str, Any]:
        """
        Main entry point for message processing.
        """
        try:
            with get_sync_session() as session:
                # 1. Initialize Collaborators
                conv_service = ConversationService(session)
                pipeline = ConversationPipeline(
                    session, self.transcription_service, self.vector_store, self.llm, self.prompt_templates
                )
                dispatcher = ResponseDispatcher(session, self.waha_client)

                # 2. Identify Conversation/Lead
                conversation = await conv_service.get_or_create(chat_id, phone_number)

                # 3. Guard: Silencing
                if self._should_bot_silence(conversation):
                    return await self._handle_silenced(session, conversation, message_text)

                # 4. Pipeline Execution (Ingestion & Analysis)
                state = await pipeline.execute(conversation, message_text, **media_kwargs)
                
                # Update urgency in DB if detected
                if state.is_urgent and not conversation.is_urgent:
                    conversation.is_urgent = True
                    session.flush()

                # 5. Guard: Answered Questions
                if self.answered_questions_memory.was_answered(state.message_text):
                    return await self._handle_repeated_question(session, conversation, dispatcher, state.message_text, session_name)

                # 6. Response Generation
                response_data = await self._generate_response(state, conversation)
                response_text = self._normalize_response_text(response_data["response"])

                # 7. Check Closure
                if state.intent == "ENCERRAMENTO":
                    conv_service.close(conversation.id, reason="CLIENT_REQUEST")
                    # Force a polite closing message if LLM didn't generate one well
                    response_text = "Entendido! Conversa encerrada. Se precisar de algo no futuro, é só chamar. Até mais! 👋"

                # 8. Check Handoff
                elif await self._should_handoff(conversation, state):
                    response_text = await self._trigger_handoff(session, conversation, state.new_score)
                    state.intent = "HANDOFF"

                # 8. Dispatch & Persist
                sent = await dispatcher.dispatch(
                    conversation.id, chat_id, phone_number, 
                    conversation.lead.id if conversation.lead else None,
                    response_text, state.intent, state.message_text,
                    response_data, session_name
                )

                # 9. Final record in Chroma (Vector Memory)
                await pipeline.context_builder.save_to_chroma(
                    conversation.id, f"User: {state.message_text}", {"intent": state.intent, "score": state.new_score}
                )

                session.commit()
                self.answered_questions_memory.add(state.message_text)

                return {
                    "conversation_id": conversation.id,
                    "response_sent": sent,
                    "intent": state.intent,
                    "maturity_score": state.new_score,
                }

        except Exception as e:
            logger.error("[ERROR] Orchestration failed: %s", e, exc_info=True)
            if 'session' in locals():
                session.rollback()
            raise BusinessRuleError(f"Failed to process message: {e}")

    # =========================================================================
    # Helpers
    # =========================================================================

    def _should_bot_silence(self, conversation):
        return conversation.status in [
            ConversationStatus.ACTIVE_HUMAN,
            ConversationStatus.PENDING_HANDOFF,
            ConversationStatus.COMPLETED,
            ConversationStatus.CLOSED,
        ]

    async def _handle_silenced(self, session, conversation, message_text):
        from robbot.services.communication.message_processor import MessageProcessor
        mp = MessageProcessor(session, None)
        await mp.save_inbound_message(session, conversation.id, message_text, from_phone=conversation.phone_number)
        session.commit()
        return {"conversation_id": conversation.id, "bot_silenced": True}

    async def _handle_repeated_question(self, session, conversation, dispatcher, message_text, session_name):
        resp = "Já respondi essa pergunta antes! Se precisar de mais detalhes, me avise. 😊"
        await dispatcher.dispatch(
            conversation.id, conversation.chat_id, conversation.phone_number,
            conversation.lead.id if conversation.lead else None,
            resp, "REPETIDA", message_text, {"tokens_used": 0, "latency_ms": 0}, session_name
        )
        session.commit()
        return {"conversation_id": conversation.id, "response_sent": True, "intent": "REPETIDA"}

    async def _generate_response(self, state: PipelineState, conversation) -> dict:
        # Get memory data
        questions_asked = await self.persistent_memory.get_all_questions(conversation.id)
        facts = await self.persistent_memory.get_all_facts(conversation.id)
        summary = "; ".join([f"{k}: {v}" for k, v in facts.items()]) if facts else "No facts"
        
        prompt = self.prompt_templates.format_response_prompt(
            user_message=state.message_text,
            intent=state.intent,
            spin_phase=state.spin_phase,
            context=state.context_text,
            lead_name=conversation.lead.name if conversation.lead else None,
            maturity_score=conversation.lead.maturity_score if conversation.lead else 0,
            lead_status=conversation.lead.status.value if conversation.lead else "NEW",
            questions_asked=questions_asked,
            conversation_summary=summary,
        )

        response_data = await self.llm.generate_response(prompt)
        
        # Update memory
        await self._update_memory(conversation.id, response_data.get("response", ""), conversation.lead)
        
        return response_data

    async def _update_memory(self, conv_id, response_text, lead):
        for line in str(response_text).split("\n"):
            if line.strip().endswith("?"):
                await self.persistent_memory.add_question(conv_id, line.strip())
        if lead and lead.name:
            await self.persistent_memory.save_fact(conv_id, "patient_name", lead.name)

    async def _should_handoff(self, conversation, state: PipelineState) -> bool:
        # Handoff if score is high or intent is explicit
        if state.new_score >= 85:
            return True
        if state.intent in ["AGENDAMENTO", "RECLAMACAO_PROBLEMA", "ESCALACAO_SOLICITADA"]:
            return True
        return False

    async def _trigger_handoff(self, session, conversation, score) -> str:
        from robbot.services.handoff.handoff_service import HandoffService
        from robbot.infra.persistence.repositories.conversation_repository import ConversationRepository
        from robbot.infra.persistence.repositories.lead_repository import LeadRepository
        
        handoff_service = HandoffService(ConversationRepository(session), LeadRepository(session))
        res = await handoff_service.trigger_handoff(
            session=session, conversation_id=conversation.id, 
            reason="score_high" if score >= 85 else "intent_triggered", score=score
        )
        return res["message"]

    def _normalize_response_text(self, text: Any) -> str:
        # Reuse existing logic but simplified
        return enforce_whatsapp_style(str(text), max_paragraphs=2)


# =========================================================================
# Factory
# =========================================================================

_orchestrator = None


def get_conversation_orchestrator() -> ConversationOrchestrator:
    """Singleton factory for ConversationOrchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ConversationOrchestrator()
    return _orchestrator

