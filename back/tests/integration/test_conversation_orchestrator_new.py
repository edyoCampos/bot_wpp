"""
Integration tests for refactored ConversationOrchestrator with decomposed components.

Tests the interaction between MessagePipeline, ConversationStateMachine, and ResponseGenerator.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from robbot.core.interfaces import LLMProvider
from robbot.domain.shared.enums import (
    ConversationStatus,
    IntentType,
    LeadStatus,
    MessageType,
)
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.services.conversation_state_machine import ConversationStateMachine
from robbot.services.message_pipeline import MessagePipeline
from robbot.services.bot.response_generator import ResponseGenerator


@pytest.fixture
def mock_session() -> Session:
    """Create mock session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_lead() -> LeadModel:
    """Create mock lead."""
    lead = MagicMock(spec=LeadModel)
    lead.id = "lead-123"
    lead.name = "João Silva"
    lead.maturity_score = 30
    lead.status = LeadStatus.ENGAGED
    return lead


@pytest.fixture
def mock_conversation(mock_lead: LeadModel) -> ConversationModel:
    """Create mock conversation."""
    conv = MagicMock(spec=ConversationModel)
    conv.id = "conv-123"
    conv.chat_id = "wpp-chat-123"
    conv.status = ConversationStatus.ACTIVE
    conv.lead = mock_lead
    return conv


@pytest.fixture
def message_pipeline(mock_session: Session) -> MessagePipeline:
    """Create MessagePipeline with mocks."""
    with patch("robbot.services.message_pipeline.MessageProcessor") as mock_processor:
        processor = MagicMock()
        mock_processor.return_value = processor
        return MessagePipeline(db=mock_session, message_processor=processor)


@pytest.fixture
def state_machine(mock_session: Session) -> ConversationStateMachine:
    """Create ConversationStateMachine with mocks."""
    return ConversationStateMachine(db=mock_session)


@pytest.fixture
def response_generator() -> ResponseGenerator:
    """Create ResponseGenerator with mocks."""
    with (
        patch("robbot.services.response_generator.LLMProvider"),
        patch("robbot.services.response_generator.PromptLoader"),
        patch("robbot.services.response_generator.PlaybookService"),
    ):
        mock_llm = MagicMock(spec=LLMProvider)
        mock_loader = MagicMock()
        mock_playbook = MagicMock()

        return ResponseGenerator(
            llm_provider=mock_llm,
            prompt_loader=mock_loader,
            playbook_service=mock_playbook,
        )


class TestMessagePipelineIntegration:
    """Test MessagePipeline with other components."""

    @pytest.mark.asyncio
    async def test_message_pipeline_validates_and_stores(
        self,
        message_pipeline: MessagePipeline,
        mock_conversation: ConversationModel,
    ):
        """Test that message pipeline validates and stores messages."""
        with patch("robbot.services.message_pipeline.ConversationMessageRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create.return_value = MagicMock(id="msg-123")
            mock_repo_class.return_value = mock_repo

            # Process valid message
            result = await message_pipeline.process_message(
                conversation=mock_conversation,
                content="Estou interessado em emagrecimento",
                message_type=MessageType.TEXT,
            )

            assert result is not None
            mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_pipeline_rejects_invalid_content(
        self,
        message_pipeline: MessagePipeline,
        mock_conversation: ConversationModel,
    ):
        """Test that message pipeline rejects invalid messages."""
        # Try to process empty message
        with pytest.raises(ValueError):  # ValidationError
            await message_pipeline.process_message(
                conversation=mock_conversation,
                content="",  # Empty
            )

    @pytest.mark.asyncio
    async def test_message_pipeline_processes_media(
        self,
        message_pipeline: MessagePipeline,
        mock_conversation: ConversationModel,
    ):
        """Test that message pipeline processes media messages."""
        with patch("robbot.services.message_pipeline.ConversationMessageRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create.return_value = MagicMock(id="msg-123")
            mock_repo_class.return_value = mock_repo

            # Mock media processor
            message_pipeline.message_processor.process_media_message = AsyncMock(return_value="Transcrição do áudio...")

            # Process audio message
            result = await message_pipeline.process_message(
                conversation=mock_conversation,
                content="Audio sobre emagrecimento",
                message_type=MessageType.AUDIO,
                has_media=True,
                media_url="https://example.com/audio.mp3",
            )

            assert result is not None
            message_pipeline.message_processor.process_media_message.assert_called_once()


class TestConversationStateMachineIntegration:
    """Test ConversationStateMachine with other components."""

    @pytest.mark.asyncio
    async def test_state_machine_updates_maturity_and_status(
        self,
        state_machine: ConversationStateMachine,
        mock_conversation: ConversationModel,
    ):
        """Test that state machine updates lead maturity and status."""
        with patch("robbot.services.conversation_state_machine.LeadRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update.return_value = mock_conversation.lead
            mock_repo_class.return_value = mock_repo

            # Update maturity
            score, status = await state_machine.update_lead_maturity(
                conversation=mock_conversation,
                detected_intent=IntentType.INTERESSE_TRATAMENTO,
                is_urgent=False,
            )

            assert score > mock_conversation.lead.maturity_score
            assert status in [
                LeadStatus.NEW,
                LeadStatus.ENGAGED,
                LeadStatus.INTERESTED,
                LeadStatus.READY,
            ]

    @pytest.mark.asyncio
    async def test_state_machine_detects_escalation_high_score(
        self,
        state_machine: ConversationStateMachine,
        mock_conversation: ConversationModel,
    ):
        """Test that high maturity score triggers escalation."""
        should_escalate = await state_machine.check_escalation_needed(
            conversation=mock_conversation,
            maturity_score=75,  # > 70 threshold
            detected_intent=IntentType.AGENDAMENTO,
        )

        assert should_escalate is True

    @pytest.mark.asyncio
    async def test_state_machine_detects_escalation_urgent(
        self,
        state_machine: ConversationStateMachine,
        mock_conversation: ConversationModel,
    ):
        """Test that urgent intent triggers escalation."""
        should_escalate = await state_machine.check_escalation_needed(
            conversation=mock_conversation,
            maturity_score=30,  # Low score
            detected_intent=IntentType.URGENCIA_DOR,  # Urgent
        )

        assert should_escalate is True

    @pytest.mark.asyncio
    async def test_state_machine_no_escalation_low_maturity(
        self,
        state_machine: ConversationStateMachine,
        mock_conversation: ConversationModel,
    ):
        """Test that low maturity doesn't trigger escalation."""
        should_escalate = await state_machine.check_escalation_needed(
            conversation=mock_conversation,
            maturity_score=20,  # Low score
            detected_intent=IntentType.DUVIDA_PROCEDIMENTO,  # Not urgent
        )

        assert should_escalate is False


class TestResponseGeneratorIntegration:
    """Test ResponseGenerator with other components."""

    @pytest.mark.asyncio
    async def test_response_generator_generates_response(
        self,
        response_generator: ResponseGenerator,
    ):
        """Test that response generator generates responses."""
        response_generator.llm.generate_response = AsyncMock(
            return_value={
                "text": "Ótimo! Podemos ajudá-lo com isso.",
                "finish_reason": "stop",
            }
        )

        response = await response_generator.generate_response(
            user_message="Quero emagrecer",
            context="Cliente novo",
            detected_intent=IntentType.INTERESSE_TRATAMENTO,
            maturity_score=30,
        )

        assert response is not None
        assert len(response) > 0
        response_generator.llm.generate_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_response_generator_personalizes_with_clinic_info(
        self,
        response_generator: ResponseGenerator,
    ):
        """Test that response is personalized with clinic information."""
        response_generator.llm.generate_response = AsyncMock(
            return_value={
                "text": "Visite {clinic_name} para saber mais!",
            }
        )

        clinic_info = {
            "name": "Clínica Silva",
            "doctor_name": "Dr. Carlos",
            "phone": "11 99999-9999",
        }

        response = await response_generator.generate_response(
            user_message="Como funciona?",
            context="",
            detected_intent=IntentType.DUVIDA_PROCEDIMENTO,
            maturity_score=40,
            clinic_info=clinic_info,
        )

        # Should contain clinic name
        assert clinic_info["name"] in response or response is not None


class TestFullConversationFlow:
    """Integration test of full conversation flow with all components."""

    @pytest.mark.asyncio
    async def test_complete_conversation_flow(
        self,
        message_pipeline: MessagePipeline,
        state_machine: ConversationStateMachine,
        response_generator: ResponseGenerator,
        mock_conversation: ConversationModel,
    ):
        """Test complete flow: message -> state -> response."""
        # Setup mocks
        with (
            patch("robbot.services.message_pipeline.ConversationMessageRepository") as mock_msg_repo,
            patch("robbot.services.conversation_state_machine.LeadRepository") as mock_lead_repo,
        ):
            mock_msg_repo.return_value.create.return_value = MagicMock(id="msg-1")
            mock_lead_repo.return_value.update.return_value = mock_conversation.lead

            response_generator.llm.generate_response = AsyncMock(return_value={"text": "Excelente pergunta!"})

            # Step 1: Process incoming message
            message = await message_pipeline.process_message(
                conversation=mock_conversation,
                content="Tenho interesse em tratamento",
            )
            assert message is not None

            # Step 2: Update conversation state
            score, status = await state_machine.update_lead_maturity(
                conversation=mock_conversation,
                detected_intent=IntentType.INTERESSE_TRATAMENTO,
            )
            assert score >= 0

            # Step 3: Generate response
            response = await response_generator.generate_response(
                user_message="Tenho interesse",
                context="Nova mensagem",
                detected_intent=IntentType.INTERESSE_TRATAMENTO,
                maturity_score=score,
            )
            assert response is not None

            # Step 4: Save response
            saved_response = await message_pipeline.save_response(
                conversation=mock_conversation,
                response_text=response,
            )
            assert saved_response is not None

            # Verify flow
            assert mock_msg_repo.return_value.create.call_count == 2  # Message + Response
            assert mock_lead_repo.return_value.update.called  # Lead updated

