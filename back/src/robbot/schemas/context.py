"""Context schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Create schemas
class ContextCreate(BaseModel):
    """Schema for creating contexts."""

    topic_id: str = Field(..., description="Associated topic ID")
    name: str = Field(..., min_length=1, max_length=255, description="Context name")
    description: str | None = Field(None, description="Detailed description")
    active: bool = Field(True, description="Whether context is active")


# Update schemas
class ContextUpdate(BaseModel):
    """Schema for updating contexts."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    active: bool | None = None


# Output schemas
class ContextOut(BaseModel):
    """Response schema for contexts."""

    id: str
    topic_id: str
    name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContextList(BaseModel):
    """Response schema for listing contexts."""

    contexts: list[ContextOut]
    total: int


class ContextSearchResult(BaseModel):
    """Response schema for context search results."""

    context_id: str
    name: str
    description: str | None
    topic_name: str
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")


class ContextSearchResults(BaseModel):
    """Response schema for multiple search results."""

    results: list[ContextSearchResult]
    total: int
