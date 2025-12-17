"""Audit Log domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class AuditLog:
    """
    Audit Log entity for tracking system actions.
    
    Attributes:
        id: Audit log ID (auto-generated)
        user_id: User who performed the action
        action: Action performed (CREATE, UPDATE, DELETE, etc.)
        entity_type: Type of entity (Lead, Conversation, User, etc.)
        entity_id: ID of the affected entity
        old_value: JSON string with old values
        new_value: JSON string with new values
        ip_address: IP address of the request
        created_at: Timestamp when action occurred
    """
    
    action: str
    entity_type: str
    entity_id: str
    user_id: Optional[int] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    id: int = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
