"""Topic domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Topic:
    """
    Topic entity representing a subject/context for organizing playbooks.
    
    Topics are generic containers (e.g., "Botox", "Preenchimento Labial")
    that group related playbooks together.
    
    Attributes:
        id: Unique topic ID
        name: Topic name (unique)
        description: Detailed description
        category: Category for grouping (e.g., "Estética Facial")
        active: Whether topic is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    name: str
    description: str | None = None
    category: str | None = None
    active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
