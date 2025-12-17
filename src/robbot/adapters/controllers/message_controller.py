"""Message controller handling HTTP endpoints for CRUD operations."""

from typing import Union
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.schemas.message import (
    DeletedResponse,
    MessageCreateLocation,
    MessageCreateMedia,
    MessageCreateText,
    MessageOutLocation,
    MessageOutMedia,
    MessageOutText,
    MessageUpdateLocation,
    MessageUpdateMedia,
    MessageUpdateText,
)
from robbot.services.message_service import MessageService

router = APIRouter()


@router.post(
    "/",
    response_model=Union[MessageOutText, MessageOutMedia, MessageOutLocation],
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    payload: Union[MessageCreateText, MessageCreateMedia, MessageCreateLocation],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new message (text, media, or location).

    - **type**: message type (text, image, voice, video, document, location)
    - **text**: message text (for text type)
    - **file**: media file metadata (for media types)
    - **caption**: optional caption for media
    - **latitude/longitude/title**: location coordinates (for location type)

    Requires authentication.
    """
    service = MessageService(db)
    return service.create_message(payload)


@router.get(
    "/{message_id}",
    response_model=Union[MessageOutText, MessageOutMedia, MessageOutLocation],
)
def get_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve message by ID.

    Returns the message with appropriate fields based on type.

    Requires authentication.
    """
    service = MessageService(db)
    return service.get_message(message_id)


@router.get(
    "/",
    response_model=list[Union[MessageOutText,
                              MessageOutMedia, MessageOutLocation]],
)
def list_messages(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all messages.

    Returns all messages with their respective type-specific fields.

    Requires authentication.
    """
    service = MessageService(db)
    return service.list_messages()


@router.patch(
    "/{message_id}",
    response_model=Union[MessageOutText, MessageOutMedia, MessageOutLocation],
)
def update_message(
    message_id: UUID,
    payload: Union[MessageUpdateText, MessageUpdateMedia, MessageUpdateLocation],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update message fields.

    Update text content, media caption/file, or location coordinates.
    Payload type must match message type.

    Requires authentication.
    """
    service = MessageService(db)
    return service.update_message(message_id, payload)


@router.delete("/{message_id}", response_model=DeletedResponse)
def delete_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete message.

    Cascades deletion to associated media/location records.

    Requires authentication.
    """
    service = MessageService(db)
    return service.delete_message(message_id)
