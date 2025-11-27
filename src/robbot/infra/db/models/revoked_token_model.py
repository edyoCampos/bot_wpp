from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, func
from robbot.infra.db.base import Base


class RevokedTokenModel(Base):
    """
    Stores revoked refresh tokens (MVP). Persisted in Postgres so revocations
    survive restarts and work in multi-instance deployments.
    """

    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, unique=True, nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<RevokedToken id={self.id} revoked_at={self.revoked_at}>"