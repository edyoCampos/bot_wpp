"""ContextItem schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Create schemas
class ContextItemCreate(BaseModel):
    """Schema for creating context items."""

    context_id: str = Field(..., description="Associated context ID")
    content_id: UUID = Field(..., description="Associated content ID")
    item_order: int | None = Field(None, description="Sequential order (auto-assigned if None)")
    context_hint: str | None = Field(None, description="When to use this item (LLM guidance)")


# Update schemas
class ContextItemUpdate(BaseModel):
    """Schema for updating context items."""

    item_order: int | None = None
    context_hint: str | None = None


class ContextItemReorder(BaseModel):
    """Schema for reordering multiple items."""

    item_id_order: list[tuple[str, int]] = Field(
        ..., description="List of (item_id, new_order) tuples", examples=[[("item1", 1), ("item2", 2), ("item3", 3)]]
    )


# Output schemas
class ContextItemOut(BaseModel):
    """Response schema for context items."""

    id: str
    context_id: str
    content_id: UUID | str  # Can be UUID from DB or string from serialization
    item_order: int
    context_hint: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContextItemWithContent(ContextItemOut):
    """Response schema for context items with content details."""

    content_type: str
    content_title: str | None
    content_description: str | None


class ContextItemList(BaseModel):
    """Response schema for listing context items."""

    items: list[ContextItemOut]
    total: int
