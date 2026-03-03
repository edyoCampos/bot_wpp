"""
Filter DTOs for query parameters validation and parsing.

Centralizes filter logic that was previously scattered in controllers.
Enables reuse across multiple endpoints and easy testing.

Resolves Issue #2: Business Logic in Controllers (SRP Violation)
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

# ===== Enum Definitions =====


class LeadStatus(str, Enum):
    """Lead status enum."""

    NEW = "NEW"
    ENGAGED = "ENGAGED"
    INTERESTED = "INTERESTED"
    READY = "READY"
    SCHEDULED = "SCHEDULED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class ConversationStatus(str, Enum):
    """Conversation status enum."""

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class LeadSource(str, Enum):
    """Lead source channel enum."""

    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    GOOGLE_ADS = "GOOGLE_ADS"
    WHATSAPP = "WHATSAPP"
    ORGANIC = "ORGANIC"
    REFERRAL = "REFERRAL"


class SortOrder(str, Enum):
    """Sort direction enum."""

    ASC = "asc"
    DESC = "desc"


# ===== Filter DTOs =====


class LeadFilterDTO(BaseModel):
    """
    Filter DTO for lead queries.

    Validates and parses query parameters.
    Used by LeadService to build database filters.
    """

    # Pagination
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=500, description="Number of items to return")

    # Filtering
    status: LeadStatus | None = Field(default=None, description="Filter by lead status")
    source: LeadSource | None = Field(default=None, description="Filter by source channel")
    score_min: int | None = Field(default=None, ge=0, le=100, description="Min maturity score")
    score_max: int | None = Field(default=None, ge=0, le=100, description="Max maturity score")
    name: str | None = Field(default=None, description="Search by name (partial match)")
    phone: str | None = Field(default=None, description="Search by phone (exact match)")
    email: str | None = Field(default=None, description="Search by email (partial match)")

    # Date filtering
    created_after: datetime | None = Field(default=None, description="Leads created after this date")
    created_before: datetime | None = Field(default=None, description="Leads created before this date")
    updated_after: datetime | None = Field(default=None, description="Leads updated after this date")

    # Sorting
    sort_by: str = Field(
        default="created_at", description="Field to sort by (created_at, updated_at, maturity_score, name)"
    )
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort direction")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sort field to prevent SQL injection."""
        allowed_fields = {"created_at", "updated_at", "maturity_score", "name", "phone"}
        if v not in allowed_fields:
            raise ValueError(f"Invalid sort field. Allowed: {allowed_fields}")
        return v

    @field_validator("score_max")
    @classmethod
    def validate_score_range(cls, v, info):
        """Ensure max score >= min score."""
        if v is not None and info.data.get("score_min") is not None and v < info.data["score_min"]:
            raise ValueError("score_max must be >= score_min")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 50,
                "status": "INTERESTED",
                "source": "INSTAGRAM",
                "score_min": 50,
                "name": "Maria",
                "sort_by": "maturity_score",
                "sort_order": "desc",
            }
        }


class ConversationFilterDTO(BaseModel):
    """
    Filter DTO for conversation queries.

    Validates and parses query parameters.
    Used by ConversationService to build database filters.
    """

    # Pagination
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=500, description="Number of items to return")

    # Filtering
    status: ConversationStatus | None = Field(default=None, description="Filter by status")
    lead_id: int | None = Field(default=None, ge=1, description="Filter by lead ID")
    phone: str | None = Field(default=None, description="Filter by phone number")
    has_unread: bool | None = Field(default=None, description="Filter by unread messages")

    # Date filtering
    started_after: datetime | None = Field(default=None, description="Started after this date")
    started_before: datetime | None = Field(default=None, description="Started before this date")
    updated_after: datetime | None = Field(default=None, description="Updated after this date")

    # Sorting
    sort_by: str = Field(default="updated_at", description="Field to sort by (created_at, updated_at, message_count)")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort direction")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sort field."""
        allowed_fields = {"created_at", "updated_at", "message_count"}
        if v not in allowed_fields:
            raise ValueError(f"Invalid sort field. Allowed: {allowed_fields}")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 50,
                "status": "ACTIVE",
                "lead_id": 123,
                "has_unread": True,
                "sort_by": "updated_at",
                "sort_order": "desc",
            }
        }


class InteractionFilterDTO(BaseModel):
    """
    Filter DTO for interaction audit logs.

    Used to query what actions were taken on leads/conversations.
    """

    # Pagination
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)

    # Filtering
    lead_id: int | None = Field(default=None, description="Filter by lead")
    conversation_id: int | None = Field(default=None, description="Filter by conversation")
    interaction_type: str | None = Field(default=None, description="Type of interaction")

    # Date filtering
    date_after: datetime | None = Field(default=None)
    date_before: datetime | None = Field(default=None)

    # Sorting
    sort_by: str = Field(default="created_at")
    sort_order: SortOrder = Field(default=SortOrder.DESC)

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        """Validate sort field."""
        allowed_fields = {"created_at", "interaction_type", "lead_id"}
        if v not in allowed_fields:
            raise ValueError(f"Invalid sort field. Allowed: {allowed_fields}")
        return v
