"""
Audit Log Repository - database operations for audit logs.
"""

from sqlalchemy.orm import Session

from robbot.infra.persistence.repositories.base_repository import BaseRepository
from robbot.infra.persistence.models.audit_log_model import AuditLogModel


class AuditLogRepository(BaseRepository[AuditLogModel]):
    """Repository for AuditLog entity."""

    def __init__(self, session: Session):
        super().__init__(session, AuditLogModel)

    def get_by_user(self, user_id: int, limit: int = 100) -> list[AuditLogModel]:
        """Get audit logs by user."""
        return (
            self.session.query(AuditLogModel)
            .filter(AuditLogModel.user_id == user_id)
            .order_by(AuditLogModel.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_entity(self, entity_type: str, entity_id: str, limit: int = 100) -> list[AuditLogModel]:
        """Get audit logs by entity."""
        return (
            self.session.query(AuditLogModel)
            .filter(AuditLogModel.entity_type == entity_type, AuditLogModel.entity_id == entity_id)
            .order_by(AuditLogModel.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_recent(self, limit: int = 100) -> list[AuditLogModel]:
        """Get most recent audit logs."""
        return self.session.query(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(limit).all()

