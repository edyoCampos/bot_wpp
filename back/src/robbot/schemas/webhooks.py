"""
Webhook payload schemas for WAHA WhatsApp API validation.

Validates inbound messages from WhatsApp before processing.
Prevents SQL injection, resource exhaustion, and malformed data.

Resolves Issue #8: Missing Input Validation at API Layer (Security Risk)
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator


class MediaType(str, Enum):
    """Types of media in WhatsApp messages."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"


class MessageType(str, Enum):
    """Message type enum."""

    TEXT = "text"
    MEDIA = "media"
    INTERACTIVE = "interactive"
    LOCATION = "location"
    CONTACT = "contact"


class WAHAMessageContact(BaseModel):
    """Contact information in message."""

    name: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20, pattern=r"^\+?[\d\s\-\(\)]+$")


class WAHAMessageLocation(BaseModel):
    """Location information in message."""

    latitude: float
    longitude: float
    name: str | None = Field(None, max_length=255)


class WAHAMessageMedia(BaseModel):
    """Media attachment in message."""

    media_type: MediaType
    mime_type: str = Field(..., max_length=100)
    sha256: str = Field(..., max_length=64)
    file_size: int = Field(..., ge=0, le=100 * 1024 * 1024)  # 100MB max
    url: str | None = Field(None, max_length=500)


class WAHAMessagePayload(BaseModel):
    """
    Schema for validating inbound WhatsApp messages.

    Validates all required fields and enforces security constraints.
    Rejects oversized payloads, invalid formats, suspicious content.
    """

    # Message identification
    message_id: str = Field(..., min_length=1, max_length=100, description="Unique message ID")
    chat_id: str = Field(..., min_length=1, max_length=20, description="WhatsApp chat ID (phone)")
    from_user: str = Field(..., min_length=1, max_length=20, alias="from")
    timestamp: datetime = Field(..., description="Message timestamp (ISO 8601)")

    # Message content
    type: MessageType = Field(..., description="Type of message")
    text: str | None = Field(None, max_length=4096, description="Text message body")

    # Media (optional)
    media: WAHAMessageMedia | None = None

    # Contact/Location (optional)
    contact: WAHAMessageContact | None = None
    location: WAHAMessageLocation | None = None

    # Reply information (optional)
    reply_to: str | None = Field(None, max_length=100, description="Message ID being replied to")

    # Sender information
    sender_name: str | None = Field(None, max_length=255, description="Display name of sender")

    # Group (optional)
    group_id: str | None = Field(None, max_length=100, description="Group ID if group message")
    group_name: str | None = Field(None, max_length=255, description="Group name")

    @validator("text")
    @classmethod
    def validate_text_content(cls, v):
        """Validate text doesn't contain SQL injection patterns."""
        if v is None:
            return v

        # Check for obvious SQL injection patterns
        dangerous_patterns = [
            "'; DROP",
            "' OR '1'='1",
            "'; DELETE",
            "UNION SELECT",
            "exec(",
            "execute(",
        ]

        text_upper = v.upper()
        for pattern in dangerous_patterns:
            if pattern in text_upper:
                raise ValueError("Message contains potentially malicious content")

        return v

    @validator("chat_id", "from_user")
    @classmethod
    def validate_phone_numbers(cls, v):
        """Validate phone number format."""
        if not v.isdigit() or len(v) < 10 or len(v) > 20:
            raise ValueError("Invalid phone number format")
        return v

    @validator("message_id", "reply_to", "group_id")
    @classmethod
    def validate_ids(cls, v):
        """Validate message IDs are alphanumeric."""
        if v and not all(c.isalnum() or c in "-_." for c in v):
            raise ValueError("ID contains invalid characters")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "message_id": "wamid.abc123",
                "chat_id": "5551234567",
                "from": "5551234567",
                "timestamp": "2024-01-15T14:30:00Z",
                "type": "text",
                "text": "Olá, gostaria de agendar uma consulta",
                "sender_name": "Maria Silva",
            }
        }


class WAHAWebhookPayload(BaseModel):
    """
    Wrapper for webhook payloads from WAHA.

    Can contain multiple messages in a single webhook call.
    """

    messages: list[WAHAMessagePayload] = Field(..., min_items=1, max_items=100)
    timestamp: datetime = Field(..., description="Webhook timestamp")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "message_id": "wamid.abc123",
                        "chat_id": "5551234567",
                        "from": "5551234567",
                        "timestamp": "2024-01-15T14:30:00Z",
                        "type": "text",
                        "text": "Hello!",
                    }
                ],
                "timestamp": "2024-01-15T14:30:01Z",
            }
        }
