"""Playbook Controller - REST endpoints for playbook management and semantic search."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.schemas.playbook import (
    PlaybookCreate, 
    PlaybookList, 
    PlaybookOut, 
    PlaybookSearchResults, 
    PlaybookUpdate
)
from robbot.schemas.topic import DeletedResponse
from robbot.services.playbook_service import PlaybookService

router = APIRouter()


@router.post("/", response_model=PlaybookOut, status_code=status.HTTP_201_CREATED)
def create_playbook(
    payload: PlaybookCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new playbook.
    
    Playbooks are organized message sequences for specific topics.
    Automatically indexed for semantic search.
    
    Requires authentication.
    """
    service = PlaybookService(db)
    created = service.create_playbook(
        topic_id=payload.topic_id,
        name=payload.name,
        description=payload.description,
        active=payload.active,
    )
    return PlaybookOut.model_validate(created)


@router.get("/search", response_model=PlaybookSearchResults)
def search_playbooks(
    query: str = Query(..., min_length=1, description="Search query (natural language)"),
    top_k: int = Query(3, ge=1, le=10, description="Number of results"),
    active_only: bool = Query(True, description="Only active playbooks"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Semantic search for playbooks using RAG (ChromaDB).
    
    Example queries:
    - "botox preço procedimento"
    - "clareamento dental informações"
    - "preenchimento labial antes depois"
    
    Returns playbooks ranked by relevance score (0-1).
    """
    service = PlaybookService(db)
    results = service.search_playbooks(query, top_k=top_k, active_only=active_only)
    
    return PlaybookSearchResults(
        results=results,
        total=len(results)
    )


@router.get("/{playbook_id}", response_model=PlaybookOut)
def get_playbook(
    playbook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve playbook by ID."""
    service = PlaybookService(db)
    playbook = service.get_playbook(playbook_id)
    if not playbook:
        raise HTTPException(status_code=404, detail=f"Playbook {playbook_id} not found")
    return PlaybookOut.model_validate(playbook)


@router.get("/topic/{topic_id}", response_model=PlaybookList)
def list_playbooks_by_topic(
    topic_id: str,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all playbooks for a specific topic."""
    service = PlaybookService(db)
    playbooks = service.list_playbooks_by_topic(topic_id, active_only=active_only)
    return PlaybookList(
        playbooks=[PlaybookOut.model_validate(p) for p in playbooks],
        total=len(playbooks)
    )


@router.patch("/{playbook_id}", response_model=PlaybookOut)
def update_playbook(
    playbook_id: str,
    payload: PlaybookUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update playbook fields.
    
    Automatically reindexes for semantic search.
    """
    service = PlaybookService(db)
    
    # Build update dict (only non-None values)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    
    updated = service.update_playbook(playbook_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Playbook {playbook_id} not found")
    
    return PlaybookOut.model_validate(updated)


@router.delete("/{playbook_id}", response_model=DeletedResponse)
def delete_playbook(
    playbook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete playbook.
    
    Cascades deletion to steps and removes from ChromaDB index.
    """
    service = PlaybookService(db)
    success = service.delete_playbook(playbook_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Playbook {playbook_id} not found")
    
    return DeletedResponse(message="Playbook deleted successfully", deleted_id=playbook_id)
