"""Health-check response schemas for the API."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class HealthComponent(BaseModel):
    """Status of an individual system component."""

    ok: bool
    error: str | None = None


class HealthOut(BaseModel):
    """Overall health-check response with per-component status."""

    status: str
    components: Dict[str, Any]
    active_sessions: int = 0
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
