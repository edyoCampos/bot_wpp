from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ConversationStatus(str, Enum):
    ACTIVE_BOT = "ACTIVE_BOT"  # Bot conversando ativamente
    PENDING_HANDOFF = "PENDING_HANDOFF"  # Aguardando atendente assumir
    ACTIVE_HUMAN = "ACTIVE_HUMAN"  # Atendente conversando
    COMPLETED = "COMPLETED"  # Agendamento confirmado
    ESCALATED = "ESCALATED"  # Escalado (bot confuso)
    CLOSED = "CLOSED"  # Conversa finalizada

    # Mantido para compatibilidade
    ACTIVE = "ACTIVE_BOT"
    WAITING_SECRETARY = "PENDING_HANDOFF"
    TRANSFERRED = "ACTIVE_HUMAN"


class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
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
    GROQ = "GROQ"


class InteractionType(str, Enum):
    NOTE = "NOTE"
    STATUS_CHANGE = "STATUS_CHANGE"
    CALL = "CALL"
    EMAIL = "EMAIL"
    MESSAGE = "MESSAGE"
    MEETING = "MEETING"


class IntentType(str, Enum):
    """Intent classification for conversation messages."""

    INTERESSE_TRATAMENTO = "INTERESSE_TRATAMENTO"
    DUVIDA_PROCEDIMENTO = "DUVIDA_PROCEDIMENTO"
    PRECO_VALOR = "PRECO_VALOR"
    LOCALIZACAO_HORARIO = "LOCALIZACAO_HORARIO"
    URGENCIA_DOR = "URGENCIA_DOR"
    RESULTADO_TEMPO = "RESULTADO_TEMPO"
    COMPARACAO_OPCOES = "COMPARACAO_OPCOES"
    AGENDAMENTO = "AGENDAMENTO"
    RECLAMACAO_PROBLEMA = "RECLAMACAO_PROBLEMA"
    ESCALACAO_SOLICITADA = "ESCALACAO_SOLICITADA"
    OUTRO = "OUTRO"


class MessageType(str, Enum):
    """Message type enum."""

    TEXT = "text"
    MEDIA = "media"
    INTERACTIVE = "interactive"
    LOCATION = "location"
    CONTACT = "contact"
    AUDIO = "audio"
    VIDEO = "video"
