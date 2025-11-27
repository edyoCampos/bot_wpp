"""AlertModel ORM for critical incident persistence."""

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from robbot.infra.db.base import Base


class AlertModel(Base):
    """
    Tabela para persistir alertas/erros críticos.
    Útil para auditoria e acionamento de workflows de incident.
    """

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Alert id={self.id} level={self.level} created_at={self.created_at}>"
