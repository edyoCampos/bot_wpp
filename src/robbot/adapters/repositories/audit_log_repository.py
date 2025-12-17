"""
Audit Log Repository - database operations for audit logs.
"""

from typing import List, Optional

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey, text, MetaData
from sqlalchemy.orm import Session

from robbot.adapters.repositories.base_repository import BaseRepository
from robbot.domain.entities.audit_log import AuditLog

metadata = MetaData()


# SQLAlchemy table definition
audit_logs_table = Table(
    'audit_logs',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
    Column('action', String(50), nullable=False),
    Column('entity_type', String(50), nullable=False, index=True),
    Column('entity_id', String(100), nullable=False, index=True),
    Column('old_value', Text, nullable=True),
    Column('new_value', Text, nullable=True),
    Column('ip_address', String(45), nullable=True),
    Column('created_at', DateTime(timezone=True), nullable=False, server_default=text('now()'), index=True),
)


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog entity."""

    def __init__(self, session: Session):
        super().__init__(session, table=audit_logs_table, entity_class=AuditLog)

    def get_by_user(self, user_id: int, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by user."""
        result = self.session.execute(
            self.table.select()
            .where(self.table.c.user_id == user_id)
            .order_by(self.table.c.created_at.desc())
            .limit(limit)
        ).fetchall()
        
        return [self._map_to_entity(row) for row in result]

    def get_by_entity(self, entity_type: str, entity_id: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by entity."""
        result = self.session.execute(
            self.table.select()
            .where(
                (self.table.c.entity_type == entity_type) &
                (self.table.c.entity_id == entity_id)
            )
            .order_by(self.table.c.created_at.desc())
            .limit(limit)
        ).fetchall()
        
        return [self._map_to_entity(row) for row in result]

    def get_recent(self, limit: int = 100) -> List[AuditLog]:
        """Get most recent audit logs."""
        result = self.session.execute(
            self.table.select()
            .order_by(self.table.c.created_at.desc())
            .limit(limit)
        ).fetchall()
        
        return [self._map_to_entity(row) for row in result]
