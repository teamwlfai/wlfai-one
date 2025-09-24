"""
Platform-level models for system administration
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Enum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel
from .enums import PlatformUserRole


class PlatformUser(BaseModel):
    """System-level platform administrators"""

    __tablename__ = "platform_users"

    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(
        Enum(PlatformUserRole), nullable=False, default=PlatformUserRole.SUPPORT
    )
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True))
    timezone = Column(String(50), default="UTC")

    __table_args__ = (
        Index("idx_platform_user_email", "email"),
        Index("idx_platform_user_role", "role"),
        Index("idx_platform_user_active", "is_active"),
    )

    # Relationships
    created_organizations = relationship(
        "Organization", foreign_keys="Organization.created_by", back_populates="creator"
    )

    # Self-referential relationships for audit trail
    created_platform_users = relationship(
        "PlatformUser",
        remote_side="PlatformUser.id",
        foreign_keys="PlatformUser.created_by",
        post_update=True,
    )
    updated_platform_users = relationship(
        "PlatformUser",
        remote_side="PlatformUser.id",
        foreign_keys="PlatformUser.updated_by",
        post_update=True,
    )

    @property
    def full_name(self):
        """Get the full name of the platform user"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_super_admin(self):
        """Check if user has super admin privileges"""
        return self.role == PlatformUserRole.SUPER_ADMIN

    @property
    def is_admin(self):
        """Check if user has admin or super admin privileges"""
        return self.role in [PlatformUserRole.SUPER_ADMIN, PlatformUserRole.ADMIN]


class PlatformSetting(BaseModel):
    """System-wide platform configuration settings"""

    __tablename__ = "platform_settings"

    key = Column(String(255), unique=True, nullable=False)
    value = Column(JSONB, nullable=False)
    description = Column(Text)

    __table_args__ = (Index("idx_platform_setting_key", "key"),)

    @property
    def string_value(self):
        """Get value as string if it's a simple string value"""
        if isinstance(self.value, str):
            return self.value
        return str(self.value)

    @property
    def bool_value(self):
        """Get value as boolean if it's a boolean value"""
        if isinstance(self.value, bool):
            return self.value
        if isinstance(self.value, str):
            return self.value.lower() in ("true", "1", "yes", "on")
        return bool(self.value)

    @property
    def int_value(self):
        """Get value as integer if it's a numeric value"""
        if isinstance(self.value, int):
            return self.value
        if isinstance(self.value, str) and self.value.isdigit():
            return int(self.value)
        return 0

    @classmethod
    def get_setting(cls, session, key, default=None):
        """Helper method to get a setting value"""
        setting = session.query(cls).filter(cls.key == key).first()
        return setting.value if setting else default

    @classmethod
    def set_setting(cls, session, key, value, description=None, updated_by=None):
        """Helper method to set a setting value"""
        setting = session.query(cls).filter(cls.key == key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
            if updated_by:
                setting.updated_by = updated_by
        else:
            setting = cls(
                key=key,
                value=value,
                description=description,
                created_by=updated_by,
                updated_by=updated_by,
            )
            session.add(setting)
        return setting
