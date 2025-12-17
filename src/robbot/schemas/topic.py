"""Topic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Create schemas
class TopicCreate(BaseModel):
    """Schema for creating topics."""

    name: str = Field(..., min_length=1, max_length=255, description="Topic name (unique)")
    description: Optional[str] = Field(None, description="Detailed description")
    category: Optional[str] = Field(None, max_length=100, description="Category for grouping")
    active: bool = Field(True, description="Whether topic is active")


# Update schemas
class TopicUpdate(BaseModel):
    """Schema for updating topics."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    active: Optional[bool] = None


# Output schemas
class TopicOut(BaseModel):
    """Response schema for topics."""

    id: str
    name: str
    description: Optional[str]
    category: Optional[str]
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
