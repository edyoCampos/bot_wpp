import pytest
from datetime import datetime, timedelta
from robbot.domain.entities import Lead, Conversation
from robbot.domain.value_objects import LeadScore, PhoneNumber
from robbot.domain.shared.enums import LeadStatus, ConversationStatus

def test_lead_score_clamping():
    """Ensure LeadScore value is always between 0 and 100."""
    assert LeadScore(150).value == 100
    assert LeadScore(-50).value == 0
    assert LeadScore(50).value == 50

def test_lead_score_adjustment():
    """Test relative adjustments to scores."""
    score = LeadScore(50)
    assert score.apply_adjustment(20).value == 70
    assert score.apply_adjustment(100).value == 100
    assert score.apply_adjustment(-100).value == 0

def test_lead_status_transitions():
    """Test automatic status transitions based on score rules."""
    lead = Lead.create(name="Test", phone_number="5511999999999")
    assert lead.status == LeadStatus.NEW
    
    # 0 -> 10: CONTACTED
    lead.update_score(10)
    assert lead.status == LeadStatus.CONTACTED
    
    # 10 -> 55: ENGAGED
    lead.update_score(55)
    assert lead.status == LeadStatus.ENGAGED
    
    # 55 -> 85: READY
    lead.update_score(85)
    assert lead.status == LeadStatus.READY
    
    # Conversion
    lead.convert()
    assert lead.status == LeadStatus.SCHEDULED
    assert lead.maturity_score.value == 100

def test_lead_soft_delete():
    """Test soft delete and restore."""
    lead = Lead.create(name="Delete Me", phone_number="5511999999999")
    assert lead.deleted_at is None
    
    lead.soft_delete()
    assert lead.deleted_at is not None
    
    lead.restore()
    assert lead.deleted_at is None

def test_conversation_lifecycle():
    """Test conversation state transitions and escalations."""
    conv = Conversation(id="conv-1", chat_id="123@c.us", phone_number="5511999999999")
    assert conv.status == ConversationStatus.ACTIVE_BOT
    
    # Escalate
    conv.escalate(reason="High priority patient")
    assert conv.status == ConversationStatus.PENDING_HANDOFF
    assert conv.is_urgent is True
    assert conv.metadata["escalation_reason"] == "High priority patient"
    
    # Human takeover
    conv.silence_bot()
    assert conv.status == ConversationStatus.ACTIVE_HUMAN
    
    # Resume bot
    conv.resume_bot()
    assert conv.status == ConversationStatus.ACTIVE_BOT
    
    # Close
    conv.close()
    assert conv.status == ConversationStatus.CLOSED

def test_phone_number_value_object():
    """Test WhatsApp JID detection and cleaning."""
    jid = PhoneNumber("5511999999999@c.us")
    assert jid.is_whatsapp is True
    assert jid.clean() == "5511999999999@c.us"
    
    regular = PhoneNumber("(11) 99999-9999")
    assert regular.is_whatsapp is False
    assert regular.clean() == "11999999999"

