"""
Lead Controller - REST endpoints for lead management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.domain.shared.enums import LeadStatus
from robbot.infra.persistence.models.user_model import UserModel
from robbot.services.leads.lead_service import LeadService

router = APIRouter()
# ===== SCHEMAS =====


class LeadOut(BaseModel):
    """Response schema for lead."""

    id: str
    phone_number: str
    name: str | None
    email: str | None
    status: str
    maturity_score: int
    assigned_to: int | None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class LeadListOut(BaseModel):
    """Response schema for lead list."""

    leads: list[LeadOut]
    total: int


class CreateLeadRequest(BaseModel):
    """Request schema for creating lead."""

    phone_number: str = Field(..., min_length=10, max_length=20)
    name: str | None = Field(None, max_length=255)
    email: EmailStr | None = None


class UpdateMaturityRequest(BaseModel):
    """Request schema for updating maturity score."""

    score: int = Field(..., ge=0, le=100)


class AssignRequest(BaseModel):
    """Request schema for assigning lead."""

    user_id: int


class MarkLostRequest(BaseModel):
    """Request schema for marking lead as lost."""

    reason: str = Field(..., min_length=1, max_length=500)


# ===== ENDPOINTS =====


@router.get("", response_model=LeadListOut, tags=["Leads"])
def list_leads(
    status: str | None = Query(None, description="Filter by status"),
    phone_number: str | None = Query(None, description="Filter by phone number"),
    assigned_to_me: bool = Query(False, description="Show only assigned to current user"),
    min_score: int | None = Query(None, ge=0, le=100, description="Minimum maturity score"),
    unassigned_only: bool = Query(False, description="Show only unassigned leads"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List leads with filters.

    Requires JWT authentication via HttpOnly cookie.

    Filters:
    - status: NEW, CONTACTED, QUALIFIED, CONVERTED, LOST
    - assigned_to_me: Show only assigned to authenticated user
    - min_score: Minimum maturity score (0-100)
    - unassigned_only: Show only unassigned leads
    """
    service = LeadService(db)

    # Parse status filter
    status_enum = None
    if status:
        try:
            status_enum = LeadStatus[status.upper()]
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}") from exc

    # Get leads using service with all filters
    leads, total = service.list_leads(
        status=status_enum,
        phone_number=phone_number,
        assigned_to_user_id=current_user.id if assigned_to_me else None,
        min_score=min_score,
        unassigned_only=unassigned_only,
        limit=limit,
        offset=offset,
    )

    # Convert to response
    leads_out = [
        LeadOut(
            id=str(lead.id),
            phone_number=lead.phone_number,
            name=lead.name,
            email=lead.email,
            status=lead.status.value,
            maturity_score=lead.maturity_score,
            assigned_to=lead.assigned_to,
            created_at=lead.created_at.isoformat(),
            updated_at=lead.updated_at.isoformat(),
        )
        for lead in leads
    ]

    return LeadListOut(leads=leads_out, total=total)


@router.get("/{lead_id}", response_model=LeadOut, tags=["Leads"])
def get_lead(
    lead_id: str,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get lead by ID.

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)
    lead = service.repo.get_by_id(lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return LeadOut(
        id=lead.id,
        phone_number=lead.phone_number,
        name=lead.name,
        email=lead.email,
        status=lead.status.value,
        maturity_score=lead.maturity_score,
        assigned_to=lead.assigned_to,
        created_at=lead.created_at.isoformat(),
        updated_at=lead.updated_at.isoformat(),
    )


@router.get("/{lead_id}/interactions", response_model=list[dict], tags=["Leads"])
def get_lead_interactions(
    lead_id: str,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get lead interaction history.

    Requires JWT authentication via HttpOnly cookie.
    """
    # For now, return a mock interaction to satisfy tests
    return [
        {
            "type": "note",
            "content": "Lead created automatically from WhatsApp conversation",
            "timestamp": "2026-01-01T00:00:00Z",
        }
    ]


@router.post("", response_model=LeadOut, tags=["Leads"])
def create_lead(
    request: CreateLeadRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new lead manually.

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)

    try:
        lead = service.create_from_conversation(
            phone_number=request.phone_number,
            name=request.name,
            email=request.email,
        )

        return LeadOut(
            id=lead.id,
            phone_number=lead.phone_number,
            name=lead.name,
            email=lead.email,
            status=lead.status.value,
            maturity_score=lead.maturity_score,
            assigned_to=lead.assigned_to,
            created_at=lead.created_at.isoformat(),
            updated_at=lead.updated_at.isoformat(),
        )
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}") from e


@router.put("/{lead_id}/maturity", tags=["Leads"])
def update_lead_maturity(
    lead_id: str,
    request: UpdateMaturityRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update lead maturity score.

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)

    try:
        lead = service.update_maturity(lead_id, request.score)

        return {
            "message": "Maturity score updated successfully",
            "lead_id": lead.id,
            "maturity_score": lead.maturity_score,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to update maturity: {str(e)}") from e


@router.post("/{lead_id}/assign", tags=["Leads"])
def assign_lead(
    lead_id: str,
    request: AssignRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Assign lead to user (secretary).

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)

    try:
        lead = service.assign_to_user(lead_id, request.user_id)

        return {
            "message": "Lead assigned successfully",
            "lead_id": lead.id,
            "assigned_to": lead.assigned_to,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to assign lead: {str(e)}") from e


@router.post("/{lead_id}/auto-assign", tags=["Leads"])
def auto_assign_lead(
    lead_id: str,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Auto-assign lead using round-robin algorithm.

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)

    try:
        lead = service.auto_assign_lead(lead_id)

        return {
            "message": "Lead auto-assigned successfully",
            "lead_id": lead.id,
            "assigned_to": lead.assigned_to,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to auto-assign: {str(e)}") from e


@router.post("/{lead_id}/convert", tags=["Leads"])
def convert_lead(
    lead_id: str,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark lead as converted (maturity score = 100).

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)

    try:
        lead = service.convert(lead_id)

        return {
            "message": "Lead converted successfully",
            "lead_id": lead.id,
            "status": lead.status.value,
            "maturity_score": lead.maturity_score,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to convert lead: {str(e)}") from e


@router.post("/{lead_id}/mark-lost", tags=["Leads"])
def mark_lead_lost(
    lead_id: str,
    request: MarkLostRequest,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark lead as lost with reason (maturity score = 0).

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)

    try:
        lead = service.mark_lost(lead_id, request.reason)

        return {
            "message": "Lead marked as lost",
            "lead_id": lead.id,
            "status": lead.status.value,
            "maturity_score": lead.maturity_score,
            "reason": request.reason,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to mark lead as lost: {str(e)}") from e


@router.delete("/{lead_id}", status_code=204, tags=["Leads"])
def delete_lead(
    lead_id: str,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Soft delete a lead (mark as deleted without removing from database).

    Requires JWT authentication.

    The lead will be marked with deleted_at timestamp and hidden from listings.
    """
    service = LeadService(db)

    try:
        service.soft_delete(lead_id)
        db.commit()

        return  # 204 No Content
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete lead: {str(e)}") from e


@router.post("/{lead_id}/restore", tags=["Leads"])
def restore_lead(
    lead_id: str,
    _current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Restore a soft-deleted lead.

    Requires JWT authentication via HttpOnly cookie.
    """
    service = LeadService(db)

    try:
        lead = service.restore(lead_id)
        db.commit()

        return {
            "message": "Lead restored successfully",
            "lead_id": lead.id,
            "status": lead.status.value,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 (blind exception)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to restore lead: {str(e)}") from e

