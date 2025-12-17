"""PlaybookStep Controller - REST endpoints for managing playbook steps."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.domain.entities.playbook_step import PlaybookStep
from robbot.schemas.playbook_step import (
    PlaybookStepCreate, 
    PlaybookStepList, 
    PlaybookStepOut, 
    PlaybookStepReorder, 
    PlaybookStepUpdate
)
from robbot.schemas.topic import DeletedResponse
from robbot.services.playbook_service import PlaybookService

router = APIRouter()


@router.post("/", response_model=PlaybookStepOut, status_code=status.HTTP_201_CREATED)
def add_step(
    payload: PlaybookStepCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Add a step to a playbook.
    
    Step order is auto-assigned if not provided (appends to end).
    Automatically reindexes playbook for semantic search.
    
    Requires authentication.
    """
    service = PlaybookService(db)
    
    step = PlaybookStep(
        playbook_id=payload.playbook_id,
        message_id=str(payload.message_id),
        step_order=payload.step_order or 0,  # Will be auto-assigned
        context_hint=payload.context_hint,
    )
    
    created = service.add_step(step)
    return PlaybookStepOut.model_validate(created)


@router.get("/playbook/{playbook_id}", response_model=PlaybookStepList)
def list_playbook_steps(
    playbook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all steps for a playbook in order.
    
    Returns steps sorted by step_order.
    """
    service = PlaybookService(db)
    steps = service.get_playbook_steps(playbook_id)
    
    return PlaybookStepList(
        steps=[PlaybookStepOut.model_validate(s) for s in steps],
        total=len(steps)
    )


@router.get("/playbook/{playbook_id}/details")
def list_playbook_steps_with_details(
    playbook_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List steps with full message details (for LLM use).
    
    Returns enriched data including:
    - Step order and context hint
    - Message type, title, description, tags
    - Message content (text, media URL, etc.)
    
    This endpoint is designed for LLM consumption.
    """
    service = PlaybookService(db)
    steps_with_details = service.get_playbook_steps_with_details(playbook_id)
    
    return {
        "playbook_id": playbook_id,
        "steps": steps_with_details,
        "total": len(steps_with_details)
    }


@router.post("/reorder")
def reorder_steps(
    payload: PlaybookStepReorder,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Reorder multiple steps at once.
    
    Body:
    {
      "step_id_order": [
        ["step_id_1", 1],
        ["step_id_2", 2],
        ["step_id_3", 3]
      ]
    }
    
    All steps must belong to the same playbook.
    """
    service = PlaybookService(db)
    
    # Extract playbook_id from first step
    if not payload.step_id_order:
        raise HTTPException(status_code=400, detail="At least one step required")
    
    first_step = service.step_repo.get_by_id(payload.step_id_order[0][0])
    if not first_step:
        raise HTTPException(status_code=404, detail="First step not found")
    
    playbook_id = first_step.playbook_id
    
    # Reorder
    success = service.reorder_steps(playbook_id, payload.step_id_order)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reorder steps")
    
    return {"message": "Steps reordered successfully", "playbook_id": playbook_id}


@router.patch("/{step_id}", response_model=PlaybookStepOut)
def update_step(
    step_id: str,
    payload: PlaybookStepUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update step fields (order or context_hint)."""
    service = PlaybookService(db)
    
    # Build update dict (only non-None values)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    
    updated = service.step_repo.update(step_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Step {step_id} not found")
    
    return PlaybookStepOut.model_validate(updated)


@router.delete("/{step_id}", response_model=DeletedResponse)
def delete_step(
    step_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete step from playbook.
    
    Automatically reindexes playbook.
    """
    service = PlaybookService(db)
    success = service.delete_step(step_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Step {step_id} not found")
    
    return DeletedResponse(message="Step deleted successfully", deleted_id=step_id)
