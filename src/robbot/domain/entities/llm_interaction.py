"""LLMInteraction domain entity."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LLMInteraction:
    """
    LLMInteraction entity representing an interaction with LLM (Gemini).
    
    Attributes:
        id: Unique interaction ID
        conversation_id: Associated conversation ID
        prompt_text: Prompt sent to LLM
        response_text: Response from LLM
        tokens_used: Total tokens consumed
        latency_ms: Response latency in milliseconds
        timestamp: Interaction timestamp
    """
    
    conversation_id: str
    prompt_text: str
    response_text: str
    tokens_used: int
    latency_ms: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
