"""Context Controller - REST endpoints for context management and semantic search."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.common.utils import filter_none_values
from robbot.schemas.context import ContextCreate, ContextList, ContextOut, ContextSearchResults, ContextUpdate
from robbot.schemas.topic import DeletedResponse
from robbot.services.ai.context_service import ContextService

router = APIRouter()


@router.post("/", response_model=ContextOut, status_code=status.HTTP_201_CREATED)
def create_context(
    payload: ContextCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new context.

    Contexts are organized content sequences for specific topics.
    Automatically indexed for semantic search.

    Requires authentication.
    """
    service = ContextService(db)
    created = service.create_context(
        topic_id=payload.topic_id,
        name=payload.name,
        description=payload.description,
        active=payload.active,
    )
    return ContextOut.model_validate(created)


@router.get("/search", response_model=ContextSearchResults)
def search_contexts(
    query: str = Query(..., min_length=1, description="Search query (natural language)"),
    top_k: int = Query(3, ge=1, le=10, description="Number of results"),
    active_only: bool = Query(True, description="Only active contexts"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Semantic search for contexts using RAG (ChromaDB).

    Returns contexts ranked by relevance score (0-1).
    """
    service = ContextService(db)
    results = service.search_contexts(query, top_k=top_k, active_only=active_only)

    return ContextSearchResults(results=results, total=len(results))


@router.get("/{context_id}", response_model=ContextOut)
def get_context(
    context_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve context by ID."""
    service = ContextService(db)
    context = service.get_context(context_id)
    if not context:
        raise HTTPException(status_code=404, detail=f"Context {context_id} not found")
    return ContextOut.model_validate(context)


@router.get("/topic/{topic_id}", response_model=ContextList)
def list_contexts_by_topic(
    topic_id: str,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all contexts for a specific topic."""
    service = ContextService(db)
    contexts = service.list_contexts_by_topic(topic_id, active_only=active_only)
    return ContextList(contexts=[ContextOut.model_validate(c) for c in contexts], total=len(contexts))


@router.patch("/{context_id}", response_model=ContextOut)
def update_context(
    context_id: str,
    payload: ContextUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update context fields.

    Automatically reindexes for semantic search.
    """
    service = ContextService(db)

    # Build update dict (only non-None values)
    update_data = filter_none_values(payload)

    updated = service.update_context(context_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Context {context_id} not found")

    return ContextOut.model_validate(updated)


@router.delete("/{context_id}", response_model=DeletedResponse)
def delete_context(
    context_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete context.

    Cascades deletion to items and removes from ChromaDB index.
    """
    service = ContextService(db)
    success = service.delete_context(context_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Context {context_id} not found")

    return DeletedResponse(message="Context deleted successfully", deleted_id=context_id)

