"""
User management and authentication models
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Enum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel
from .enums import UserRole


class User(BaseModel):
    """Organization users with role-based access"""

    __tablename__ = "users"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    permissions = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    phone = Column(String(50))
    timezone = Column(String(50), default="UTC")
    preferences = Column(JSONB, default=dict)
    email_verified_at = Column(DateTime(timezone=True))
    last_login = Column(DateTime(timezone=True))
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("org_id", "email"),
        Index("idx_user_org_role", "org_id", "role"),
        Index("idx_user_email", "email"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="users")
    created_users = relationship(
        "User", remote_side="User.id", foreign_keys=[created_by]
    )
    updated_users = relationship(
        "User", remote_side="User.id", foreign_keys=[updated_by]
    )
    sessions = relationship("UserSession", back_populates="user")
    api_requests = relationship("APIRequest", back_populates="user")


class UserSession(BaseModel):
    """Active user sessions for authentication"""

    __tablename__ = "user_sessions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(JSONB)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default="NOW()")

    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
        Index("idx_session_expires", "expires_at"),
    )

    # Relationships
    user = relationship("User", back_populates="sessions")


class UserInvitation(BaseModel):
    """User invitations to join organizations"""

    __tablename__ = "user_invitations"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    permissions = Column(JSONB, default=dict)
    token = Column(String(255), unique=True, nullable=False)
    status = Column(
        String(50), default="pending"
    )  # pending, accepted, expired, cancelled
    expires_at = Column(DateTime(timezone=True), nullable=False)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    accepted_at = Column(DateTime(timezone=True))

    # Relationships
    inviter = relationship("User")
