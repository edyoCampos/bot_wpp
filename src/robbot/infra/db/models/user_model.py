"""UserModel ORM for application users."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base
from robbot.domain.enums import Role


class UserModel(Base):
    """User entity with authentication and role data."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default=Role.USER.value)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    
    # Relationships
    assigned_leads = relationship(
        "LeadModel",
        back_populates="assigned_to",
        foreign_keys="LeadModel.assigned_to_user_id"
    )
    
    # FASE 0 - New relationships for Auth refactoring
    credential = relationship(
        "CredentialModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    auth_sessions = relationship(
        "AuthSessionModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
