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


class MessageCreateMedia(BaseModel):
    """Schema for creating media messages (image, voice, video, document)."""

    type: Literal["image", "voice", "video", "document"]
    file: MediaFile
    caption: Optional[str] = None


class MessageCreateLocation(BaseModel):
    """Schema for creating location messages."""

    type: Literal["location"]
    latitude: float
    longitude: float
    title: Optional[str] = None


# Update schemas
class MessageUpdateText(BaseModel):
    """Schema for updating text messages."""

    text: Optional[str] = None


class MessageUpdateMedia(BaseModel):
    """Schema for updating media messages."""

    caption: Optional[str] = None
    file: Optional[MediaFile] = None


class MessageUpdateLocation(BaseModel):
    """Schema for updating location messages."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    title: Optional[str] = None


# Output schemas
class MessageOutText(BaseModel):
    """Response schema for text messages."""

    id: UUID
    type: Literal["text"]
    text: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageOutMedia(BaseModel):
    """Response schema for media messages."""

    id: UUID
    type: Literal["image", "voice", "video", "document"]
    file: MediaFile
    caption: Optional[str] = None
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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeletedResponse(BaseModel):
    """Response schema for deletion confirmation."""

    deleted: bool = True
