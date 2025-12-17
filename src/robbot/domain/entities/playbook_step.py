"""PlaybookStep domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class PlaybookStep:
    """
    PlaybookStep entity linking messages to playbooks in order.
    
    Each step represents a message at a specific position in the
    playbook sequence.
    
    Attributes:
        id: Unique step ID
        playbook_id: Associated playbook ID
        message_id: Associated message ID
        step_order: Sequential order (1, 2, 3...)
        context_hint: When to use this step (for LLM guidance)
        created_at: Creation timestamp
    """
    
    playbook_id: str
    message_id: str
    step_order: int
    context_hint: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
