"""Content schemas for API requests and responses."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MediaFile(BaseModel):
    """Media file metadata schema."""

    mimetype: str
    filename: str
    url: str | None = None


class Location(BaseModel):
    """Geographic location schema."""

    latitude: float
    longitude: float
    title: str | None = None


# Create schemas
class ContentCreateText(BaseModel):
    """Schema for creating text content."""

    type: Literal["text"]
    text: str
    title: str | None = Field(None, max_length=255, description="Content title for organization")
    description: str | None = Field(None, description="Description for LLM context")
    tags: str | None = Field(None, max_length=500, description="Comma-separated tags")


class ContentCreateMedia(BaseModel):
    """Schema for creating media content (image, voice, video, document)."""

    type: Literal["image", "voice", "video", "document"]
    file: MediaFile
    caption: str | None = None
    title: str | None = Field(None, max_length=255, description="Content title for organization")
    description: str | None = Field(None, description="Description for LLM context")
    tags: str | None = Field(None, max_length=500, description="Comma-separated tags")


class ContentCreateLocation(BaseModel):
    """Schema for creating location content."""

    type: Literal["location"]
    latitude: float
    longitude: float
    title: str | None = None
    description: str | None = Field(None, description="Description for LLM context")
    tags: str | None = Field(None, max_length=500, description="Comma-separated tags")


# Update schemas
class ContentUpdateText(BaseModel):
    """Schema for updating text content."""

    text: str | None = None
    title: str | None = None
    description: str | None = None
    tags: str | None = None


class ContentUpdateMedia(BaseModel):
    """Schema for updating media content."""

    caption: str | None = None
    file: MediaFile | None = None
    title: str | None = None
    description: str | None = None
    tags: str | None = None


class ContentUpdateLocation(BaseModel):
    """Schema for updating location content."""

    latitude: float | None = None
    longitude: float | None = None
    title: str | None = None
    description: str | None = None
    tags: str | None = None


# Output schemas
class ContentOutText(BaseModel):
    """Response schema for text content."""

    id: UUID
    type: Literal["text"]
    text: str
    title: str | None = None
    description: str | None = None
    tags: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContentOutMedia(BaseModel):
    """Response schema for media content."""

    id: UUID
    type: Literal["image", "voice", "video", "document"]
    file: MediaFile
    caption: str | None = None
    title: str | None = None
    description: str | None = None
    tags: str | None = None
    transcription: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContentOutLocation(BaseModel):
    """Response schema for location content."""

    id: UUID
    type: Literal["location"]
    latitude: float
    longitude: float
    title: str | None = None
    description: str | None = None
    tags: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# AI-assisted description generation
class ContentDescriptionGenerate(BaseModel):
    """Request schema for AI-assisted description generation."""

    content_id: UUID = Field(..., description="Content ID to generate description for")
    use_gemini_vision: bool = Field(True, description="Use Gemini Vision for image/video analysis")


class ContentDescriptionOut(BaseModel):
    """Response schema for generated description."""

    content_id: UUID
    generated_title: str | None
    generated_description: str
    suggested_tags: str | None


class DeletedResponse(BaseModel):
    """Response schema for deletion confirmation."""

    deleted: bool = True
