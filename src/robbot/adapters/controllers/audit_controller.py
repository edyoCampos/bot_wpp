"""
Audit Log Controller - REST endpoints for audit logs.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from robbot.core.security import get_current_user
from robbot.domain.enums import Role
from robbot.infra.db.session import get_db
from robbot.services.audit_service import AuditService

router = APIRouter()


# ===== SCHEMAS =====

class AuditLogOut(BaseModel):
    """Response schema for audit log."""
    id: int
    user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: str
    old_value: Optional[str]
    new_value: Optional[str]
    ip_address: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# ===== ENDPOINTS =====

@router.get("/audit-logs", response_model=List[AuditLogOut], tags=["Audit"])
def list_audit_logs(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List audit logs (admin only).
    
    Requires JWT authentication and admin role.
    
    Filters:
    - entity_type: Filter by entity type (Lead, Conversation, etc.)
    - entity_id: Filter by specific entity ID
    - user_id: Filter by user who performed actions
    """
    # Check admin permission
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    
    # Apply filters
    if entity_type and entity_id:
        logs = service.get_entity_logs(entity_type, entity_id, limit)
    elif user_id:
        logs = service.get_user_logs(user_id, limit)
    else:
        logs = service.get_recent_logs(limit)
    
    return [
        AuditLogOut(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            old_value=log.old_value,
            new_value=log.new_value,
            ip_address=log.ip_address,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get("/audit-logs/entity/{entity_type}/{entity_id}", response_model=List[AuditLogOut], tags=["Audit"])
def get_entity_audit_trail(
    entity_type: str,
    entity_id: str,
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get audit trail for a specific entity (admin only).
    
    Requires JWT authentication and admin role.
    
    Shows complete history of actions on the entity.
    """
    # Check admin permission
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    service = AuditService(db)
    logs = service.get_entity_logs(entity_type, entity_id, limit)
    
    return [
        AuditLogOut(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            old_value=log.old_value,
            new_value=log.new_value,
            ip_address=log.ip_address,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]
