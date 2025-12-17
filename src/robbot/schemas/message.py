"""Message schemas for API requests and responses."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MediaFile(BaseModel):
    """Media file metadata schema."""

    mimetype: str
    filename: str
    url: Optional[str] = None


class Location(BaseModel):
    """Geographic location schema."""

    latitude: float
    longitude: float
    title: Optional[str] = None


# Create schemas
class MessageCreateText(BaseModel):
    """Schema for creating text messages."""

    type: Literal["text"]
    text: str
    title: Optional[str] = Field(None, max_length=255, description="Message title for organization")
    description: Optional[str] = Field(None, description="Description for LLM context")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")


class MessageCreateMedia(BaseModel):
    """Schema for creating media messages (image, voice, video, document)."""

    type: Literal["image", "voice", "video", "document"]
    file: MediaFile
    caption: Optional[str] = None
    title: Optional[str] = Field(None, max_length=255, description="Message title for organization")
    description: Optional[str] = Field(None, description="Description for LLM context")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")


class MessageCreateLocation(BaseModel):
    """Schema for creating location messages."""

    type: Literal["location"]
    latitude: float
    longitude: float
    title: Optional[str] = None
    description: Optional[str] = Field(None, description="Description for LLM context")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")


# Update schemas
class MessageUpdateText(BaseModel):
    """Schema for updating text messages."""

    text: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class MessageUpdateMedia(BaseModel):
    """Schema for updating media messages."""

    caption: Optional[str] = None
    file: Optional[MediaFile] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class MessageUpdateLocation(BaseModel):
    """Schema for updating location messages."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


# Output schemas
class MessageOutText(BaseModel):
    """Response schema for text messages."""

    id: UUID
    type: Literal["text"]
    text: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageOutMedia(BaseModel):
    """Response schema for media messages."""

    id: UUID
    type: Literal["image", "voice", "video", "document"]
    file: MediaFile
    caption: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageOutLocation(BaseModel):
    """Response schema for location messages."""

    id: UUID
    type: Literal["location"]
    latitude: float
    longitude: float
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# AI-assisted description generation
class MessageDescriptionGenerate(BaseModel):
    """Request schema for AI-assisted description generation."""

    message_id: UUID = Field(..., description="Message ID to generate description for")
    use_gemini_vision: bool = Field(True, description="Use Gemini Vision for image/video analysis")


class MessageDescriptionOut(BaseModel):
    """Response schema for generated description."""

    message_id: UUID
    generated_title: Optional[str]
    generated_description: str
    suggested_tags: Optional[str]


class DeletedResponse(BaseModel):
    """Response schema for deletion confirmation."""

    deleted: bool = True
