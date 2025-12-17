from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    WAITING_SECRETARY = "WAITING_SECRETARY"
    TRANSFERRED = "TRANSFERRED"
    CLOSED = "CLOSED"


class LeadStatus(str, Enum):
    NEW = "NEW"
    ENGAGED = "ENGAGED"
    INTERESTED = "INTERESTED"
    READY = "READY"
    SCHEDULED = "SCHEDULED"
    LOST = "LOST"


class MessageDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class SessionStatus(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    SCAN_QR_CODE = "SCAN_QR_CODE"
    WORKING = "WORKING"
    FAILED = "FAILED"


class LLMProvider(str, Enum):
    GEMINI = "GEMINI"
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"


class InteractionType(str, Enum):
    NOTE = "NOTE"
    STATUS_CHANGE = "STATUS_CHANGE"
    CALL = "CALL"
    EMAIL = "EMAIL"
