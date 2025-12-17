"""Lead domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Lead:
    """
    Lead entity representing a sales lead.
    
    Attributes:
        id: Unique lead ID
        phone_number: Lead phone number
        name: Lead name
        email: Lead email
        maturity_score: Lead maturity score (0-100)
        assigned_to_user_id: Assigned user ID
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    phone_number: str
    name: str
    maturity_score: int = 0
    email: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    deleted_at: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
