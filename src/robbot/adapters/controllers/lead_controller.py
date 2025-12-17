"""
Lead Controller - REST endpoints for lead management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from robbot.adapters.repositories.lead_repository import LeadRepository
from robbot.core.security import get_current_user
from robbot.domain.enums import LeadStatus
from robbot.infra.db.session import get_db
from robbot.services.lead_service import LeadService

router = APIRouter()


# ===== SCHEMAS =====

class LeadOut(BaseModel):
    """Response schema for lead."""
    id: str
    phone_number: str
    name: Optional[str]
    email: Optional[str]
    status: str
    maturity_score: int
    assigned_to: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class LeadListOut(BaseModel):
    """Response schema for lead list."""
    leads: List[LeadOut]
    total: int


class CreateLeadRequest(BaseModel):
    """Request schema for creating lead."""
    phone_number: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None


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

@router.get("/leads", response_model=LeadListOut, tags=["Leads"])
def list_leads(
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to_me: bool = Query(False, description="Show only assigned to current user"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum maturity score"),
    unassigned_only: bool = Query(False, description="Show only unassigned leads"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List leads with filters.
    
    Requires JWT authentication.
    
    Filters:
    - status: NEW, CONTACTED, QUALIFIED, CONVERTED, LOST
    - assigned_to_me: Show only assigned to authenticated user
    - min_score: Minimum maturity score (0-100)
    - unassigned_only: Show only unassigned leads
    """
    service = LeadService(db)
    
    # Get leads by filters
    if unassigned_only:
        leads = service.get_unassigned_leads()
    elif status:
        try:
            status_enum = LeadStatus[status.upper()]
            leads = service.get_leads_by_status(status_enum)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    else:
        repo = LeadRepository(db)
        leads = repo.get_all()
    
    # Apply additional filters
    if assigned_to_me:
        leads = [l for l in leads if l.assigned_to == current_user.id]
    
    if min_score is not None:
        leads = [l for l in leads if l.maturity_score >= min_score]
    
    # Pagination
    total = len(leads)
    leads = leads[offset:offset + limit]
    
    # Convert to response
    leads_out = [
        LeadOut(
            id=l.id,
            phone_number=l.phone_number,
            name=l.name,
            email=l.email,
            status=l.status.value,
            maturity_score=l.maturity_score,
            assigned_to=l.assigned_to,
            created_at=l.created_at.isoformat(),
            updated_at=l.updated_at.isoformat(),
        )
        for l in leads
    ]
    
    return LeadListOut(leads=leads_out, total=total)


@router.get("/leads/{lead_id}", response_model=LeadOut, tags=["Leads"])
def get_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get lead by ID.
    
    Requires JWT authentication.
    """
    repo = LeadRepository(db)
    lead = repo.get_by_id(lead_id)
    
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


@router.post("/leads", response_model=LeadOut, tags=["Leads"])
def create_lead(
    request: CreateLeadRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new lead manually.
    
    Requires JWT authentication.
    """
    service = LeadService(db)
    
    try:
        lead = service.create_from_conversation(
            phone=request.phone_number,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")


@router.put("/leads/{lead_id}/maturity", tags=["Leads"])
def update_lead_maturity(
    lead_id: str,
    request: UpdateMaturityRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update lead maturity score.
    
    Requires JWT authentication.
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update maturity: {str(e)}")


@router.post("/leads/{lead_id}/assign", tags=["Leads"])
def assign_lead(
    lead_id: str,
    request: AssignRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Assign lead to user (secretary).
    
    Requires JWT authentication.
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign lead: {str(e)}")


@router.post("/leads/{lead_id}/auto-assign", tags=["Leads"])
def auto_assign_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Auto-assign lead using round-robin algorithm.
    
    Requires JWT authentication.
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-assign: {str(e)}")


@router.post("/leads/{lead_id}/convert", tags=["Leads"])
def convert_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark lead as converted (maturity score = 100).
    
    Requires JWT authentication.
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert lead: {str(e)}")


@router.post("/leads/{lead_id}/mark-lost", tags=["Leads"])
def mark_lead_lost(
    lead_id: str,
    request: MarkLostRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark lead as lost with reason (maturity score = 0).
    
    Requires JWT authentication.
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark lead as lost: {str(e)}")


@router.delete("/leads/{lead_id}", status_code=204, tags=["Leads"])
def delete_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
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
        
        return None  # 204 No Content
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete lead: {str(e)}")


@router.post("/leads/{lead_id}/restore", tags=["Leads"])
def restore_lead(
    lead_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Restore a soft-deleted lead.
    
    Requires JWT authentication.
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
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to restore lead: {str(e)}")
