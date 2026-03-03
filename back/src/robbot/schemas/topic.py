"""Topic schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Create schemas
class TopicCreate(BaseModel):
    """Schema for creating topics."""

    name: str = Field(..., min_length=1, max_length=255, description="Topic name (unique)")
    description: str | None = Field(None, description="Detailed description")
    category: str | None = Field(None, max_length=100, description="Category for grouping")
    active: bool = Field(True, description="Whether topic is active")


# Update schemas
class TopicUpdate(BaseModel):
    """Schema for updating topics."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    active: bool | None = None


# Output schemas
class TopicOut(BaseModel):
    """Response schema for topics."""

    id: str
    name: str
    description: str | None
    category: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TopicList(BaseModel):
    """Response schema for listing topics."""

    topics: list[TopicOut]
    total: int


class DeletedResponse(BaseModel):
    """Response for delete operations."""

    message: str
    deleted_id: str
