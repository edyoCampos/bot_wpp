"""LeadInteraction domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from robbot.domain.enums import InteractionType


@dataclass
class LeadInteraction:
    """
    LeadInteraction entity representing an interaction with a lead.
    
    Attributes:
        id: Unique interaction ID
        lead_id: Associated lead ID
        interaction_type: Type of interaction
        notes: Interaction notes/description
        timestamp: Interaction timestamp
    """
    
    lead_id: str
    interaction_type: InteractionType
    notes: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
