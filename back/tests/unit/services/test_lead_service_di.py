"""
Unit tests for LeadService with mock session and MockRepository.

Tests lead operations with dependency injection of Session.

Resolves Issue #4: Session Management Anti-Pattern
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from robbot.core.custom_exceptions import BusinessRuleError, NotFoundException
from robbot.domain.shared.enums import LeadStatus
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.services.leads.lead_service import LeadService


@pytest.fixture
def mock_session() -> Session:
    """Create mock SQLAlchemy session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_lead_model() -> LeadModel:
    """Create mock lead model."""
    lead = MagicMock(spec=LeadModel)
    lead.id = "lead-123"
    lead.phone_number = "+5511999999999"
    lead.name = "João Silva"
    lead.email = "joao@example.com"
    lead.maturity_score = 45
    lead.status = LeadStatus.ENGAGED
    lead.created_at = datetime.now(UTC)
    return lead


@pytest.fixture
def lead_service(mock_session: Session) -> LeadService:
    """Create LeadService with mock session."""
    return LeadService(db=mock_session)


class TestLeadServiceCreation:
    """Test lead creation with DI."""

    def test_lead_service_accepts_session_di(self, mock_session: Session):
        """Test that LeadService accepts session via DI."""
        service = LeadService(db=mock_session)
        assert service.db == mock_session
        assert service.db is not None

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_create_from_conversation(self, mock_repo_class, lead_service: LeadService, mock_lead_model: LeadModel):
        """Test creating lead from conversation."""
        mock_repo = MagicMock()
        mock_repo.get_by_phone.return_value = None
        mock_repo.create.return_value = mock_lead_model
        mock_repo_class.return_value = mock_repo

        # Create lead
        result = lead_service.create_from_conversation(
            phone_number="+5511999999999",
            name="João Silva",
            email="joao@example.com",
        )

        # Verify
        assert result.id == "lead-123"
        assert result.phone_number == "+5511999999999"
        mock_repo.create.assert_called_once()

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_create_from_conversation_already_exists(
        self, mock_repo_class, lead_service: LeadService, mock_lead_model: LeadModel
    ):
        """Test that creating existing lead returns existing lead."""
        mock_repo = MagicMock()
        mock_repo.get_by_phone.return_value = mock_lead_model
        mock_repo_class.return_value = mock_repo

        # Create lead (already exists)
        result = lead_service.create_from_conversation(
            phone_number="+5511999999999",
            name="João Silva",
        )

        # Should return existing
        assert result.id == mock_lead_model.id
        mock_repo.create.assert_not_called()


class TestLeadServiceMaturityUpdate:
    """Test lead maturity score updates."""

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_update_maturity_valid_score(self, mock_repo_class, lead_service: LeadService, mock_lead_model: LeadModel):
        """Test updating lead maturity with valid score."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = mock_lead_model
        mock_repo.update.return_value = mock_lead_model
        mock_repo_class.return_value = mock_repo

        # Update maturity
        result = lead_service.update_maturity(
            lead_id="lead-123",
            new_score=75,
        )

        assert result is not None
        mock_repo.update.assert_called_once()

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_update_maturity_invalid_score_too_high(self, mock_repo_class, lead_service: LeadService):
        """Test that invalid score (>100) raises error."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Score > 100 should raise
        with pytest.raises(BusinessRuleError):
            lead_service.update_maturity(lead_id="lead-123", new_score=150)

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_update_maturity_invalid_score_negative(self, mock_repo_class, lead_service: LeadService):
        """Test that invalid score (<0) raises error."""
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Score < 0 should raise
        with pytest.raises(BusinessRuleError):
            lead_service.update_maturity(lead_id="lead-123", new_score=-10)

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_update_maturity_lead_not_found(self, mock_repo_class, lead_service: LeadService):
        """Test that updating non-existent lead raises error."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None
        mock_repo_class.return_value = mock_repo

        # Lead not found should raise
        with pytest.raises(NotFoundException):
            lead_service.update_maturity(lead_id="nonexistent", new_score=50)


class TestLeadServiceSessionInjection:
    """Test that session is properly injected and used."""

    def test_service_has_session_attribute(self, lead_service: LeadService):
        """Test that service stores session."""
        assert hasattr(lead_service, "db")
        assert lead_service.db is not None

    def test_multiple_services_can_share_session(self, mock_session: Session):
        """Test that multiple services can share same session."""
        service1 = LeadService(db=mock_session)
        service2 = LeadService(db=mock_session)

        assert service1.db is service2.db
        assert service1.db == mock_session

    def test_services_can_use_different_sessions(self):
        """Test that services can use different sessions."""
        session1 = MagicMock(spec=Session)
        session2 = MagicMock(spec=Session)

        service1 = LeadService(db=session1)
        service2 = LeadService(db=session2)

        assert service1.db != service2.db
        assert service1.db is session1
        assert service2.db is session2


class TestLeadServiceIntegration:
    """Integration-like tests with mocked database."""

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_lead_lifecycle(self, mock_repo_class, lead_service: LeadService, mock_lead_model: LeadModel):
        """Test complete lead lifecycle: create -> update maturity -> transition status."""
        mock_repo = MagicMock()

        # Setup mock returns
        mock_repo.get_by_phone.return_value = None
        mock_repo.create.return_value = mock_lead_model
        mock_repo.get_by_id.return_value = mock_lead_model
        mock_repo.update.return_value = mock_lead_model
        mock_repo_class.return_value = mock_repo

        # Step 1: Create lead
        created = lead_service.create_from_conversation(
            phone_number="+5511999999999",
            name="João Silva",
        )
        assert created.id == "lead-123"

        # Step 2: Update maturity
        updated = lead_service.update_maturity(
            lead_id="lead-123",
            new_score=60,
        )
        assert updated is not None

        # Verify calls
        assert mock_repo.create.call_count == 1
        assert mock_repo.update.call_count == 1


class TestLeadServiceErrorHandling:
    """Test error handling in LeadService."""

    def test_service_raises_on_invalid_session(self):
        """Test that service raises error with invalid session."""
        with pytest.raises(AttributeError):
            LeadService(db=None)  # type: ignore

    @patch("robbot.services.leads.lead_service.LeadRepository")
    def test_service_handles_database_errors(self, mock_repo_class, lead_service: LeadService):
        """Test that service handles database errors gracefully."""
        mock_repo = MagicMock()
        mock_repo.get_by_phone.side_effect = Exception("Database connection error")
        mock_repo_class.return_value = mock_repo

        # Should raise when repository fails
        with pytest.raises(ValueError):
            lead_service.create_from_conversation(
                phone_number="+5511999999999",
                name="João Silva",
            )

