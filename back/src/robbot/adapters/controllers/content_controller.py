"""Content controller handling HTTP endpoints for CRUD operations."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.schemas.content import (
    DeletedResponse,
    ContentCreateLocation,
    ContentCreateMedia,
    ContentCreateText,
    ContentOutLocation,
    ContentOutMedia,
    ContentOutText,
    ContentUpdateLocation,
    ContentUpdateMedia,
    ContentUpdateText,
)
from robbot.services.content.content_service import ContentService

router = APIRouter()


@router.post(
    "/",
    response_model=ContentOutText | ContentOutMedia | ContentOutLocation,
    status_code=status.HTTP_201_CREATED,
)
def create_content(
    payload: ContentCreateText | ContentCreateMedia | ContentCreateLocation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new content (text, media, or location).

    Requires authentication.
    """
    service = ContentService(db)
    return service.create_content(payload)


@router.get(
    "/{content_id}",
    response_model=ContentOutText | ContentOutMedia | ContentOutLocation,
)
def get_content(
    content_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieve content by ID.

    Requires authentication.
    """
    service = ContentService(db)
    return service.get_content(content_id)


@router.get(
    "/",
    response_model=list[ContentOutText | ContentOutMedia | ContentOutLocation],
)
def list_contents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all contents.

    Requires authentication.
    """
    service = ContentService(db)
    return service.list_contents()


@router.patch(
    "/{content_id}",
    response_model=ContentOutText | ContentOutMedia | ContentOutLocation,
)
def update_content(
    content_id: UUID,
    payload: ContentUpdateText | ContentUpdateMedia | ContentUpdateLocation,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update content fields.

    Requires authentication.
    """
    service = ContentService(db)
    return service.update_content(content_id, payload)


@router.delete("/{content_id}", response_model=DeletedResponse)
def delete_content(
    content_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete content.

    Requires authentication.
    """
    service = ContentService(db)
    return service.delete_content(content_id)


@router.post("/{content_id}/generate-description")
def generate_description(
    content_id: UUID,
    use_gemini_vision: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Generate AI-assisted title, description, and tags for a content.

    Requires authentication.
    """
    from robbot.services.content.description_service import DescriptionService

    service = DescriptionService(db)
    result = service.generate_description(str(content_id), use_gemini_vision)

    return {
        "content_id": str(content_id),
        "generated_title": result.get("generated_title"),
        "generated_description": result.get("generated_description"),
        "suggested_tags": result.get("suggested_tags"),
    }
