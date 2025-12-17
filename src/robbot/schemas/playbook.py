"""Playbook schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Create schemas
class PlaybookCreate(BaseModel):
    """Schema for creating playbooks."""

    topic_id: str = Field(..., description="Associated topic ID")
    name: str = Field(..., min_length=1, max_length=255, description="Playbook name")
    description: Optional[str] = Field(None, description="Detailed description")
    active: bool = Field(True, description="Whether playbook is active")


# Update schemas
class PlaybookUpdate(BaseModel):
    """Schema for updating playbooks."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    active: Optional[bool] = None


# Output schemas
class PlaybookOut(BaseModel):
    """Response schema for playbooks."""

    id: str
    topic_id: str
    name: str
    description: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaybookList(BaseModel):
    """Response schema for listing playbooks."""

    playbooks: list[PlaybookOut]
    total: int


class PlaybookSearchResult(BaseModel):
    """Response schema for playbook search results."""

    playbook_id: str
    name: str
    description: Optional[str]
    topic_name: str
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")


class PlaybookSearchResults(BaseModel):
    """Response schema for multiple search results."""

    results: list[PlaybookSearchResult]
    total: int
