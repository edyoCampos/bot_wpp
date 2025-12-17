"""Playbook domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Playbook:
    """
    Playbook entity representing an organized message sequence for a topic.
    
    Playbooks contain multiple steps (messages) that guide conversation
    flow about a specific subject.
    
    Attributes:
        id: Unique playbook ID
        topic_id: Associated topic ID
        name: Playbook name
        description: Detailed description
        active: Whether playbook is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    topic_id: str
    name: str
    description: str | None = None
    active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
