"""Topic Controller - REST endpoints for topic management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.domain.entities.topic import Topic
from robbot.schemas.topic import TopicCreate, TopicList, TopicOut, TopicUpdate, DeletedResponse
from robbot.services.playbook_service import PlaybookService

router = APIRouter()


@router.post("/", response_model=TopicOut, status_code=status.HTTP_201_CREATED)
def create_topic(
    payload: TopicCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new topic.
    
    Topics are generic containers for organizing playbooks by subject/context.
    Examples: "Botox", "Preenchimento Labial", "Clareamento Dental".
    
    Requires authentication.
    """
    service = PlaybookService(db)
    topic = Topic(
        name=payload.name,
        description=payload.description,
        category=payload.category,
        active=payload.active,
    )
    created = service.create_topic(topic)
    return TopicOut.model_validate(created)


@router.get("/{topic_id}", response_model=TopicOut)
def get_topic(
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve topic by ID."""
    service = PlaybookService(db)
    topic = service.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    return TopicOut.model_validate(topic)


@router.get("/", response_model=TopicList)
def list_topics(
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all topics.
    
    Query params:
    - active_only: Filter only active topics
    - skip: Pagination offset
    - limit: Max results (default 100)
    """
    service = PlaybookService(db)
    topics = service.list_topics(active_only=active_only, skip=skip, limit=limit)
    return TopicList(
        topics=[TopicOut.model_validate(t) for t in topics],
        total=len(topics)
    )


@router.patch("/{topic_id}", response_model=TopicOut)
def update_topic(
    topic_id: str,
    payload: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update topic fields.
    
    Only provided fields will be updated.
    """
    service = PlaybookService(db)
    
    # Build update dict (only non-None values)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    
    updated = service.update_topic(topic_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    
    return TopicOut.model_validate(updated)


@router.delete("/{topic_id}", response_model=DeletedResponse)
def delete_topic(
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete topic.
    
    Cascades deletion to all associated playbooks and steps.
    """
    service = PlaybookService(db)
    success = service.delete_topic(topic_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
    
    return DeletedResponse(message="Topic deleted successfully", deleted_id=topic_id)
