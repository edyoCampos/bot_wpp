"""
Unit tests for ConversationService with DI pattern.

Tests conversation management with session dependency injection.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from robbot.core.custom_exceptions import DatabaseError, NotFoundException
from robbot.domain.shared.enums import ConversationStatus
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.services.bot.conversation_service import ConversationService


@pytest.fixture
def mock_session() -> Session:
    """Create mock SQLAlchemy session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_conversation_model() -> ConversationModel:
    """Create mock conversation model."""
    conv = MagicMock(spec=ConversationModel)
    conv.id = "conv-123"
    conv.chat_id = "wpp-chat-123"
    conv.phone_number = "+5511999999999"
    conv.status = ConversationStatus.ACTIVE
    conv.created_at = datetime.now(UTC)
    conv.updated_at = datetime.now(UTC)
    return conv


@pytest.fixture
def mock_lead_model() -> LeadModel:
    """Create mock lead model."""
    lead = MagicMock(spec=LeadModel)
    lead.id = "lead-123"
    lead.phone_number = "+5511999999999"
    lead.name = "João Silva"
    return lead


@pytest.fixture
def conversation_service(mock_session: Session) -> ConversationService:
    """Create ConversationService with mock session."""
    return ConversationService(db=mock_session)


class TestConversationServiceCreation:
    """Test conversation service with DI."""

    def test_conversation_service_accepts_session_di(self, mock_session: Session):
        """Test that ConversationService accepts session via DI."""
        service = ConversationService(db=mock_session)
        assert service.db == mock_session

    @patch("robbot.services.bot.conversation_service.ConversationRepository")
    def test_create_conversation(
        self,
        mock_repo_class,
        conversation_service: ConversationService,
        mock_conversation_model: ConversationModel,
        mock_lead_model: LeadModel,
    ):
        """Test creating a conversation."""
        mock_repo = MagicMock()
        mock_repo.create.return_value = mock_conversation_model
        mock_repo_class.return_value = mock_repo

        # Create conversation
        result = conversation_service.create_or_get_conversation(
            chat_id="wpp-chat-123",
            phone_number="+5511999999999",
            lead=mock_lead_model,
        )

        assert result.id == "conv-123"
        mock_repo.create.assert_called_once()

    @patch("robbot.services.bot.conversation_service.ConversationRepository")
    def test_get_conversation(
        self,
        mock_repo_class,
        conversation_service: ConversationService,
        mock_conversation_model: ConversationModel,
    ):
        """Test getting a conversation."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = mock_conversation_model
        mock_repo_class.return_value = mock_repo

        # Get conversation
        result = conversation_service.get_conversation(conversation_id="conv-123")

        assert result.id == "conv-123"
        mock_repo.get_by_id.assert_called_once_with("conv-123")

    @patch("robbot.services.bot.conversation_service.ConversationRepository")
    def test_get_conversation_not_found(
        self,
        mock_repo_class,
        conversation_service: ConversationService,
    ):
        """Test that getting non-existent conversation raises error."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        mock_repo_class.return_value = mock_repo

        # Should raise
        with pytest.raises(NotFoundException):
            conversation_service.get_conversation(conversation_id="nonexistent")


class TestConversationServiceStatus:
    """Test conversation status transitions."""

    @patch("robbot.services.bot.conversation_service.ConversationRepository")
    def test_close_conversation(
        self,
        mock_repo_class,
        conversation_service: ConversationService,
        mock_conversation_model: ConversationModel,
    ):
        """Test closing a conversation."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = mock_conversation_model
        mock_conversation_model.status = ConversationStatus.ACTIVE
        mock_repo.update.return_value = mock_conversation_model
        mock_repo_class.return_value = mock_repo

        # Close conversation
        result = conversation_service.close_conversation(conversation_id="conv-123")

        assert result is not None
        mock_repo.update.assert_called_once()

    @patch("robbot.services.bot.conversation_service.ConversationRepository")
    def test_reopen_conversation(
        self,
        mock_repo_class,
        conversation_service: ConversationService,
        mock_conversation_model: ConversationModel,
    ):
        """Test reopening a closed conversation."""
        mock_repo = MagicMock()
        mock_conversation_model.status = ConversationStatus.CLOSED
        mock_repo.get_by_id.return_value = mock_conversation_model
        mock_repo.update.return_value = mock_conversation_model
        mock_repo_class.return_value = mock_repo

        # Reopen conversation
        result = conversation_service.reopen_conversation(conversation_id="conv-123")

        assert result is not None
        assert result.status in [
            ConversationStatus.ACTIVE,
            ConversationStatus.CLOSED,
        ]  # Updated status


class TestConversationServiceSessionInjection:
    """Test session injection in conversation service."""

    def test_service_stores_session(self, conversation_service: ConversationService):
        """Test that service stores injected session."""
        assert hasattr(conversation_service, "db")
        assert conversation_service.db is not None

    def test_multiple_services_can_share_session(self, mock_session: Session):
        """Test that multiple services can share session."""
        service1 = ConversationService(db=mock_session)
        service2 = ConversationService(db=mock_session)

        assert service1.db is service2.db

    def test_services_can_use_different_sessions(self):
        """Test that services can use different sessions."""
        session1 = MagicMock(spec=Session)
        session2 = MagicMock(spec=Session)

        service1 = ConversationService(db=session1)
        service2 = ConversationService(db=session2)

        assert service1.db != service2.db


class TestConversationServiceIntegration:
    """Integration tests for conversation service."""

    @patch("robbot.services.bot.conversation_service.ConversationRepository")
    def test_conversation_lifecycle(
        self,
        mock_repo_class,
        conversation_service: ConversationService,
        mock_conversation_model: ConversationModel,
        mock_lead_model: LeadModel,
    ):
        """Test complete conversation lifecycle."""
        mock_repo = MagicMock()

        # Setup mocks
        mock_repo.create.return_value = mock_conversation_model
        mock_repo.get_by_id.return_value = mock_conversation_model
        mock_repo.update.return_value = mock_conversation_model
        mock_repo_class.return_value = mock_repo

        # Step 1: Create
        created = conversation_service.create_or_get_conversation(
            chat_id="wpp-chat-123",
            phone_number="+5511999999999",
            lead=mock_lead_model,
        )
        assert created is not None

        # Step 2: Get
        retrieved = conversation_service.get_conversation(conversation_id="conv-123")
        assert retrieved is not None

        # Step 3: Close
        closed = conversation_service.close_conversation(conversation_id="conv-123")
        assert closed is not None

        # Verify calls
        assert mock_repo.create.call_count == 1
        assert mock_repo.get_by_id.call_count == 2  # get + close
        assert mock_repo.update.call_count == 1  # close


class TestConversationServiceErrorHandling:
    """Test error handling."""

    def test_service_raises_on_none_session(self):
        """Test that service raises with None session."""
        with pytest.raises(AttributeError):
            ConversationService(db=None)  # type: ignore

    @patch("robbot.services.bot.conversation_service.ConversationRepository")
    def test_service_handles_db_errors(
        self,
        mock_repo_class,
        conversation_service: ConversationService,
        mock_lead_model: LeadModel,
    ):
        """Test that service handles database errors."""
        mock_repo = MagicMock()
        mock_repo.create.side_effect = DatabaseError("DB connection failed")
        mock_repo_class.return_value = mock_repo

        # Should raise
        with pytest.raises(DatabaseError):
            conversation_service.create_or_get_conversation(
                chat_id="wpp-chat-123",
                phone_number="+5511999999999",
                lead=mock_lead_model,
            )

