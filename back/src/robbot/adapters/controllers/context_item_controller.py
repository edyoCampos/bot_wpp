"""ContextItem Controller - REST endpoints for managing context items."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.common.utils import filter_none_values
from robbot.schemas.context_item import (
    ContextItemCreate,
    ContextItemList,
    ContextItemOut,
    ContextItemReorder,
    ContextItemUpdate,
)
from robbot.schemas.topic import DeletedResponse
from robbot.services.ai.context_service import ContextService

router = APIRouter()


@router.post("/", response_model=ContextItemOut, status_code=status.HTTP_201_CREATED)
def add_item(
    payload: ContextItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Add an item to a context.

    Item order is auto-assigned if not provided (appends to end).
    Automatically reindexes context for semantic search.

    Requires authentication.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        service = ContextService(db)

        created = service.add_item(
            context_id=payload.context_id,
            content_id=str(payload.content_id),
            item_order=payload.item_order,
            context_hint=payload.context_hint,
        )
        return ContextItemOut.model_validate(created)
    except Exception as e:
        logger.error("[ERROR] Failed to add item: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/context/{context_id}", response_model=ContextItemList)
def list_context_items(
    context_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all items for a context in order.

    Returns items sorted by item_order.
    """
    service = ContextService(db)
    items = service.get_context_items(context_id)

    return ContextItemList(items=[ContextItemOut.model_validate(i) for i in items], total=len(items))


@router.get("/context/{context_id}/details")
def list_context_items_with_details(
    context_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List items with full content details (for LLM use).

    Returns enriched data including:
    - Item order and context hint
    - Content type, title, description, tags
    - Content body (text, media URL, etc.)

    This endpoint is designed for LLM consumption.
    """
    service = ContextService(db)
    items_with_details = service.get_context_items_with_details(context_id)

    return {"context_id": context_id, "items": items_with_details, "total": len(items_with_details)}


@router.post("/reorder")
def reorder_items(
    payload: ContextItemReorder,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Reorder multiple items at once.

    All items must belong to the same context.
    """
    service = ContextService(db)

    # Extract context_id from first item
    if not payload.item_id_order:
        raise HTTPException(status_code=400, detail="At least one item required")

    first_item = service.item_repo.get_by_id(payload.item_id_order[0][0])
    if not first_item:
        raise HTTPException(status_code=404, detail="First item not found")

    context_id = first_item.context_id

    # Reorder
    success = service.reorder_items(context_id, payload.item_id_order)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reorder items")

    return {"message": "Items reordered successfully", "context_id": context_id}


@router.patch("/{item_id}", response_model=ContextItemOut)
def update_item(
    item_id: str,
    payload: ContextItemUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update item fields (order or context_hint)."""
    service = ContextService(db)

    # Build update dict (only non-None values)
    update_data = filter_none_values(payload)

    updated = service.item_repo.update(item_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    return ContextItemOut.model_validate(updated)


@router.delete("/{item_id}", response_model=DeletedResponse)
def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete item from context.

    Automatically reindexes context.
    """
    service = ContextService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    return DeletedResponse(message="Item deleted successfully", deleted_id=item_id)

