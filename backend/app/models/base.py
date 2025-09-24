"""
Base models and database configuration
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BaseModel(Base):
    """Abstract base model with common fields"""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("platform_users.id"), nullable=True
    )
    updated_by = Column(
        UUID(as_uuid=True), ForeignKey("platform_users.id"), nullable=True
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(
        UUID(as_uuid=True), ForeignKey("platform_users.id"), nullable=True
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    @property
    def is_deleted(self):
        """Check if the record is soft deleted"""
        return self.deleted_at is not None

    def soft_delete(self, deleted_by_user_id=None):
        """Soft delete the record"""
        self.deleted_at = func.now()
        if deleted_by_user_id:
            self.deleted_by = deleted_by_user_id
