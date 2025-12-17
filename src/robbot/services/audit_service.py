"""
Audit Service - business logic for audit logging.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from robbot.adapters.repositories.audit_log_repository import AuditLogRepository
from robbot.domain.entities.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for audit logging.
    
    Automatically logs critical actions:
    - CREATE: Entity creation
    - UPDATE: Entity updates
    - DELETE: Entity deletion (soft or hard)
    - STATUS_CHANGE: Status transitions
    - PERMISSION_CHANGE: Permission modifications
    """

    def __init__(self, session):
        self.session = session
        self.repo = AuditLogRepository(session)

    def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[int] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an action to audit trail.
        
        Args:
            action: Action type (CREATE, UPDATE, DELETE, etc.)
            entity_type: Type of entity (Lead, Conversation, User, etc.)
            entity_id: ID of the affected entity
            user_id: User who performed the action
            old_value: Dictionary with old values (will be JSON encoded)
            new_value: Dictionary with new values (will be JSON encoded)
            ip_address: IP address of the request
            
        Returns:
            Created AuditLog entity
        """
        # Serialize values to JSON
        old_json = json.dumps(old_value) if old_value else None
        new_json = json.dumps(new_value) if new_value else None
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_json,
            new_value=new_json,
            ip_address=ip_address,
        )
        
        self.repo.create(audit_log)
        self.session.flush()
        
        logger.info(
            f"✓ Audit log created (action={action}, entity={entity_type}:{entity_id}, "
            f"user={user_id})"
        )
        
        return audit_log

    def log_create(
        self,
        entity_type: str,
        entity_id: str,
        user_id: Optional[int] = None,
        entity_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log entity creation."""
        return self.log_action(
            action="CREATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            new_value=entity_data,
            ip_address=ip_address,
        )

    def log_update(
        self,
        entity_type: str,
        entity_id: str,
        user_id: Optional[int] = None,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log entity update."""
        return self.log_action(
            action="UPDATE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_value=old_data,
            new_value=new_data,
            ip_address=ip_address,
        )

    def log_delete(
        self,
        entity_type: str,
        entity_id: str,
        user_id: Optional[int] = None,
        entity_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log entity deletion."""
        return self.log_action(
            action="DELETE",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_value=entity_data,
            ip_address=ip_address,
        )

    def get_user_logs(self, user_id: int, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        return self.repo.get_by_user(user_id, limit)

    def get_entity_logs(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for a specific entity."""
        return self.repo.get_by_entity(entity_type, entity_id, limit)

    def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        """Get most recent audit logs (admin only)."""
        return self.repo.get_recent(limit)
