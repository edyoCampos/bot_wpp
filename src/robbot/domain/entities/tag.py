"""Tag domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Tag:
    """
    Tag entity for categorizing conversations.
    
    Attributes:
        id: Tag ID (auto-generated)
        name: Tag name (unique, max 50 chars)
        color: Hex color code (e.g., #FF0000)
        created_at: Creation timestamp
    """
    
    name: str
    color: str
    id: int = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
