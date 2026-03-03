"""
Unit tests for LeadService.
Tests core business logic for lead management using rich domain entities.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from robbot.core.custom_exceptions import NotFoundException
from robbot.domain.shared.enums import LeadStatus
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.user_model import UserModel
from robbot.services.leads.lead_service import LeadService
from robbot.infra.db.base import Base


@pytest.fixture()
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_local()
    try:
        # Add a test user for assignment tests
        user = UserModel(id=123, email="test@example.com", full_name="Test User", role="user")
        session.add(user)
        session.commit()
        yield session
    finally:
        session.close()


@pytest.fixture()
def service(db_session):
    """Create LeadService instance."""
    return LeadService(db_session)


# =====================================================================
# CREATE LEAD TESTS
# =====================================================================
def test_create_lead_from_conversation(service):
    """Test creating a new lead from conversation."""
    phone = "+5511999999999"
    name = "John Doe"
    email = "john@example.com"

    lead = service.create_from_conversation(phone_number=phone, name=name, email=email)

    assert lead is not None
    assert lead.phone_number == phone
    assert lead.name == name
    assert lead.email == email
    assert lead.maturity_score == 0
    assert lead.status == LeadStatus.NEW


def test_create_lead_duplicate_phone_returns_existing(service):
    """Test creating lead with duplicate phone returns existing lead."""
    phone = "+5511888888888"

    # Create first lead
    lead1 = service.create_from_conversation(phone_number=phone, name="First Name")

    # Try to create duplicate
    lead2 = service.create_from_conversation(phone_number=phone, name="Second Name")

    # Should return the same lead
    assert lead1.id == lead2.id


# =====================================================================
# UPDATE MATURITY SCORE & STATUS TRANSITIONS
# =====================================================================
def test_update_maturity_score_clamping(service):
    """Test updating lead maturity score with clamping."""
    lead = service.create_from_conversation(phone_number="+5511666666666", name="Test Lead")

    # High clamping
    updated = service.update_maturity(lead_id=str(lead.id), new_score=150)
    assert updated.maturity_score == 100
    assert updated.status == LeadStatus.READY

    # Low clamping
    updated = service.update_maturity(lead_id=str(lead.id), new_score=-10)
    assert updated.maturity_score == 0


def test_status_transitions_via_service(service):
    """Test that status transitions happen when updating score through the service."""
    lead = service.create_from_conversation(phone_number="+5511555555555", name="Test Lead")
    lead_id = str(lead.id)

    # 10 -> CONTACTED
    service.update_maturity(lead_id, 10)
    assert service.repo.get_by_id(lead_id).status == LeadStatus.CONTACTED

    # 55 -> ENGAGED
    service.update_maturity(lead_id, 55)
    assert service.repo.get_by_id(lead_id).status == LeadStatus.ENGAGED

    # 85 -> READY
    service.update_maturity(lead_id, 85)
    assert service.repo.get_by_id(lead_id).status == LeadStatus.READY


# =====================================================================
# ASSIGNMENT TESTS
# =====================================================================
def test_assign_lead_to_user(service):
    """Test assigning lead to a user."""
    lead = service.create_from_conversation(phone_number="+5511222222222", name="Assignment Test")

    user_id = 123
    updated = service.assign_to_user(lead_id=str(lead.id), user_id=user_id)

    assert updated.assigned_to_user_id == user_id


# =====================================================================
# CONVERT & LOST TESTS
# =====================================================================
def test_convert_lead(service):
    """Test converting a lead sets maturity score to 100 and SCHEDULED status."""
    lead = service.create_from_conversation(phone_number="+5511000000000", name="Convert Test")

    converted = service.convert(str(lead.id))

    assert converted.maturity_score == 100
    assert converted.status == LeadStatus.SCHEDULED


def test_mark_lead_lost(service):
    """Test marking lead as lost sets maturity score to 0."""
    lead = service.create_from_conversation(phone_number="+5511888777666", name="Lost Test")
    service.update_maturity(str(lead.id), 80)

    lost = service.mark_lost(lead_id=str(lead.id), reason="Not interested")

    assert lost.maturity_score == 0


# =====================================================================
# SOFT DELETE TESTS
# =====================================================================
def test_soft_delete_and_restore(service):
    """Test soft delete and restore operations."""
    lead = service.create_from_conversation(phone_number="+5511777666444", name="Delete Test")
    lead_id = str(lead.id)

    # Delete
    deleted = service.soft_delete(lead_id)
    assert deleted.deleted_at is not None

    # Restore
    restored = service.restore(lead_id)
    assert restored.deleted_at is None


# =====================================================================
# LIST & FILTER TESTS
# =====================================================================
def test_list_leads_filtering(service):
    """Test listing leads with various filters."""
    # Create leads
    service.create_from_conversation("+5511100100100", "Lead A")
    lead_b = service.create_from_conversation("+5511200200200", "Lead B")
    
    # Assign Lead B
    service.assign_to_user(str(lead_b.id), 123)
    service.update_maturity(str(lead_b.id), 90)

    # Filter by user
    leads, total = service.list_leads(assigned_to_user_id=123)
    assert total == 1
    assert leads[0].id == lead_b.id

    # Filter by min_score
    leads, total = service.list_leads(min_score=50)
    assert total == 1
    assert leads[0].id == lead_b.id

    # Filter unassigned only
    leads, total = service.list_leads(unassigned_only=True)
    assert total == 1
    assert leads[0].name == "Lead A"

def test_auto_assign_logic(service, db_session):
    """Test auto-assignment workload balancing logic."""
    # Add another secretary
    sec2 = UserModel(id=456, email="sec2@example.com", full_name="Sec 2", role="user")
    db_session.add(sec2)
    db_session.commit()

    # Create lead and auto-assign
    lead1 = service.create_from_conversation("+5511500500501", "Auto Lead 1")
    # Mark as Engaged so it counts in workload
    service.update_maturity(str(lead1.id), 60)
    
    assigned1 = service.auto_assign_lead(str(lead1.id))
    assert assigned1.assigned_to_user_id in [123, 456]
    
    # Create another lead - should go to the OTHER secretary
    lead2 = service.create_from_conversation("+5511500500502", "Auto Lead 2")
    service.update_maturity(str(lead2.id), 60)
    assigned2 = service.auto_assign_lead(str(lead2.id))
    
    assert assigned2.assigned_to_user_id != assigned1.assigned_to_user_id
