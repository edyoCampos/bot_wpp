"""
Unit tests for ConversationService.
Tests core business logic for conversation management using rich domain entities.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC

from robbot.core.custom_exceptions import NotFoundException
from robbot.domain.shared.enums import ConversationStatus
from robbot.infra.persistence.models.conversation_model import ConversationModel
from robbot.infra.persistence.models.lead_model import LeadModel
from robbot.infra.persistence.models.conversation_message_model import ConversationMessageModel
from robbot.services.bot.conversation_service import ConversationService
from robbot.infra.db.base import Base


@pytest.fixture()
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def service(db_session):
    """Create ConversationService instance."""
    return ConversationService(db_session)


# =====================================================================
# GET OR CREATE TESTS
# =====================================================================
@pytest.mark.asyncio
async def test_get_or_create_new_conversation(service):
    """Test creating a new conversation and lead."""
    chat_id = "5511999999999@c.us"
    phone_number = "5511999999999@c.us" # Using JID format to test LID resolution skip
    name = "Test User"

    conversation = await service.get_or_create(chat_id=chat_id, phone_number=phone_number, name=name)

    assert conversation is not None
    assert conversation.chat_id == chat_id
    # Resolved phone should match if it wasn't an LID
    assert conversation.lead is not None
    assert conversation.lead.phone_number == phone_number


@pytest.mark.asyncio
async def test_get_or_create_existing_conversation(service):
    """Test retrieving an existing conversation."""
    chat_id = "5511888888888@c.us"
    phone_number = "5511888888888"

    # Create first time
    conv1 = await service.get_or_create(chat_id=chat_id, phone_number=phone_number)

    # Get same conversation
    conv2 = await service.get_or_create(chat_id=chat_id, phone_number=phone_number)

    assert conv1.id == conv2.id


# =====================================================================
# STATUS & ESCALATION TESTS
# =====================================================================
@pytest.mark.asyncio
async def test_update_status(service):
    """Test updating conversation status via service."""
    conv = await service.get_or_create(chat_id="test@c.us", phone_number="123")
    
    updated = service.update_status(conv.id, ConversationStatus.ACTIVE_HUMAN)
    assert updated.status == ConversationStatus.ACTIVE_HUMAN


@pytest.mark.asyncio
async def test_escalation_service(service):
    """Test escalation logic in service."""
    conv = await service.get_or_create(chat_id="escalate@c.us", phone_number="123")
    
    escalated = service.escalate(conv.id, reason="Technical issue")
    
    assert escalated.status == ConversationStatus.PENDING_HANDOFF
    assert escalated.escalation_reason == "Technical issue"
    assert escalated.escalated_at is not None
    assert escalated.is_urgent is True


@pytest.mark.asyncio
async def test_close_conversation(service):
    """Test closing a conversation."""
    conv = await service.get_or_create(chat_id="close@c.us", phone_number="123")
    
    closed = service.close(conv.id, reason="Resolved")
    
    assert closed.status == ConversationStatus.CLOSED
    assert closed.closed_at is not None


# =====================================================================
# LISTING TESTS
# =====================================================================
@pytest.mark.asyncio
async def test_list_active_conversations(service):
    """Test retrieving only active conversations."""
    # Create 2 active, 1 closed
    await service.get_or_create("act1@c.us", "1")
    await service.get_or_create("act2@c.us", "2")
    c3 = await service.get_or_create("closed@c.us", "3")
    service.close(c3.id)
    
    active = service.get_active_conversations()
    assert len(active) == 2
    for c in active:
        assert c.status == ConversationStatus.ACTIVE_BOT

@pytest.mark.asyncio
async def test_list_with_filters(service):
    """Test advanced filtering in list_conversations."""
    c1 = await service.get_or_create("f1@c.us", "1")
    c2 = await service.get_or_create("f2@c.us", "2")
    
    service.escalate(c1.id, "Urgent!")
    
    # Filter by urgency
    urgent_list, total = service.list_conversations(is_urgent=True)
    assert total == 1
    assert urgent_list[0].id == c1.id
    
    # Filter by phone
    phone_list, _ = service.list_conversations(phone_number="2")
    assert len(phone_list) == 1
    assert phone_list[0].id == c2.id
