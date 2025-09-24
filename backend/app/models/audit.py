"""
Audit trail and security monitoring models
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Integer,
    Numeric,
    ForeignKey,
    Enum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import AuditAction, ActorType, SecurityEventType, SecurityEventSeverity


class AuditLog(BaseModel):
    """Comprehensive audit trail for all system activities"""

    __tablename__ = "audit_logs"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    actor_type = Column(Enum(ActorType), nullable=False)
    actor_id = Column(UUID(as_uuid=True), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    metadata = Column(JSONB, default=dict)

    __table_args__ = (
        Index("idx_audit_org", "org_id"),
        Index("idx_audit_actor", "actor_type", "actor_id"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_created", "created_at"),
        Index("idx_audit_org_entity", "org_id", "entity_type"),
        Index("idx_audit_entity_action", "entity_type", "action"),
    )

    # Relationships
    organization = relationship("Organization")

    @property
    def changed_fields(self):
        """Get list of fields that were changed"""
        if not self.old_values or not self.new_values:
            return []

        changed = []
        for field, new_value in self.new_values.items():
            old_value = self.old_values.get(field)
            if old_value != new_value:
                changed.append(field)

        return changed

    @property
    def has_sensitive_data(self):
        """Check if audit log contains sensitive information"""
        sensitive_fields = ["password", "ssn", "dob", "phone", "email", "address"]

        all_fields = set()
        if self.old_values:
            all_fields.update(self.old_values.keys())
        if self.new_values:
            all_fields.update(self.new_values.keys())

        return any(field.lower() in sensitive_fields for field in all_fields)

    def get_field_change(self, field_name):
        """Get before/after values for a specific field"""
        old_value = self.old_values.get(field_name) if self.old_values else None
        new_value = self.new_values.get(field_name) if self.new_values else None

        return {
            "field": field_name,
            "old_value": old_value,
            "new_value": new_value,
            "changed": old_value != new_value,
        }

    def get_actor_display_name(self):
        """Get human-readable actor name"""
        actor_names = {
            ActorType.PLATFORM_USER: "Platform Admin",
            ActorType.USER: "Organization User",
            ActorType.API_KEY: "API Client",
            ActorType.SYSTEM: "System Process",
        }
        return actor_names.get(self.actor_type, str(self.actor_type))

    @classmethod
    def create_audit_entry(
        cls,
        actor_type,
        actor_id,
        entity_type,
        entity_id,
        action,
        old_values=None,
        new_values=None,
        org_id=None,
        ip_address=None,
        user_agent=None,
        metadata=None,
        created_by=None,
    ):
        """Factory method to create audit log entries"""
        return cls(
            org_id=org_id,
            actor_type=actor_type,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            created_by=created_by,
        )


class SecurityEvent(BaseModel):
    """Security incidents and monitoring events"""

    __tablename__ = "security_events"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type = Column(Enum(SecurityEventType), nullable=False)
    severity = Column(Enum(SecurityEventSeverity), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    details = Column(JSONB, default=dict)
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    resolved_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_security_event_org", "org_id"),
        Index("idx_security_event_user", "user_id"),
        Index("idx_security_event_type", "event_type"),
        Index("idx_security_event_severity", "severity"),
        Index("idx_security_event_resolved", "resolved"),
        Index("idx_security_event_created", "created_at"),
        Index("idx_security_event_ip", "ip_address"),
    )

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    resolver = relationship("PlatformUser", foreign_keys=[resolved_by])

    @property
    def is_critical(self):
        """Check if security event is critical"""
        return self.severity == SecurityEventSeverity.CRITICAL

    @property
    def is_high_priority(self):
        """Check if security event needs immediate attention"""
        return self.severity in [
            SecurityEventSeverity.CRITICAL,
            SecurityEventSeverity.HIGH,
        ]

    @property
    def days_since_created(self):
        """Calculate days since event was created"""
        from datetime import datetime

        if self.created_at:
            delta = datetime.utcnow() - self.created_at.replace(tzinfo=None)
            return delta.days
        return 0

    @property
    def is_overdue(self):
        """Check if event resolution is overdue based on severity"""
        overdue_days = {
            SecurityEventSeverity.CRITICAL: 1,
            SecurityEventSeverity.HIGH: 3,
            SecurityEventSeverity.MEDIUM: 7,
            SecurityEventSeverity.LOW: 30,
        }

        max_days = overdue_days.get(self.severity, 30)
        return not self.resolved and self.days_since_created > max_days

    def resolve_event(self, resolved_by_id, resolution_notes=None):
        """Mark security event as resolved"""
        if not self.resolved:
            self.resolved = True
            self.resolved_by = resolved_by_id
            self.resolved_at = func.now()

            if resolution_notes:
                details = self.details or {}
                details["resolution_notes"] = resolution_notes
                self.details = details

            return True
        return False

    def add_investigation_note(self, note, added_by_id):
        """Add investigation notes to the security event"""
        details = self.details or {}
        notes = details.get("investigation_notes", [])

        notes.append(
            {
                "note": note,
                "added_by": str(added_by_id),
                "timestamp": (
                    func.now().isoformat()
                    if hasattr(func.now(), "isoformat")
                    else str(func.now())
                ),
            }
        )

        details["investigation_notes"] = notes
        self.details = details

    @classmethod
    def create_security_event(
        cls,
        event_type,
        severity,
        org_id=None,
        user_id=None,
        ip_address=None,
        user_agent=None,
        details=None,
        created_by=None,
    ):
        """Factory method to create security events"""
        return cls(
            org_id=org_id,
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            created_by=created_by,
        )


class FeatureFlag(BaseModel):
    """Feature flags for gradual rollouts and A/B testing"""

    __tablename__ = "feature_flags"

    name = Column(String(255), nullable=False)
    key = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=False, nullable=False)
    config = Column(JSONB, default=dict)
    targeting_rules = Column(JSONB, default=dict)
    rollout_percentage = Column(Numeric(5, 2), default=0.0)  # 0.00 to 100.00
    rollout_start = Column(DateTime(timezone=True))
    rollout_end = Column(DateTime(timezone=True))
    environments = Column(JSONB, default=list)  # production, staging, development

    __table_args__ = (
        Index("idx_feature_flag_key", "key"),
        Index("idx_feature_flag_active", "is_active"),
        Index("idx_feature_flag_rollout", "rollout_percentage"),
        Index("idx_feature_flag_dates", "rollout_start", "rollout_end"),
    )

    @property
    def is_fully_rolled_out(self):
        """Check if feature is fully rolled out (100%)"""
        return self.rollout_percentage >= 100.0

    @property
    def is_in_rollout_period(self):
        """Check if feature is within rollout time window"""
        from datetime import datetime

        now = datetime.utcnow()

        if self.rollout_start and now < self.rollout_start:
            return False

        if self.rollout_end and now > self.rollout_end:
            return False

        return True

    def is_enabled_for_org(self, org_id):
        """Check if feature is enabled for specific organization"""
        if not self.is_active or not self.is_in_rollout_period:
            return False

        # Check targeting rules
        if self.targeting_rules:
            # Organization-specific targeting
            target_orgs = self.targeting_rules.get("organizations", [])
            if target_orgs and str(org_id) not in target_orgs:
                return False

            # Excluded organizations
            excluded_orgs = self.targeting_rules.get("excluded_organizations", [])
            if excluded_orgs and str(org_id) in excluded_orgs:
                return False

        # Check rollout percentage (deterministic based on org_id)
        if self.rollout_percentage < 100.0:
            import hashlib

            hash_input = f"{self.key}:{org_id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            percentage = (hash_value % 10000) / 100.0  # 0.00 to 99.99

            if percentage >= self.rollout_percentage:
                return False

        return True

    def is_enabled_for_user(self, user_id, org_id):
        """Check if feature is enabled for specific user"""
        if not self.is_enabled_for_org(org_id):
            return False

        # User-specific targeting rules
        if self.targeting_rules:
            target_users = self.targeting_rules.get("users", [])
            if target_users and str(user_id) not in target_users:
                return False

            excluded_users = self.targeting_rules.get("excluded_users", [])
            if excluded_users and str(user_id) in excluded_users:
                return False

        return True

    def update_rollout_percentage(self, new_percentage):
        """Safely update rollout percentage with validation"""
        if 0.0 <= new_percentage <= 100.0:
            self.rollout_percentage = new_percentage
            return True
        return False

    def add_targeting_rule(self, rule_type, rule_values):
        """Add targeting rule for feature flag"""
        rules = self.targeting_rules or {}
        rules[rule_type] = rule_values
        self.targeting_rules = rules

    def get_usage_stats(self, session):
        """Get feature flag usage statistics"""
        # This would typically be implemented with additional tracking
        # For now, return basic configuration info
        return {
            "rollout_percentage": float(self.rollout_percentage),
            "is_active": self.is_active,
            "targeting_rules_count": len(self.targeting_rules or {}),
            "environments": self.environments or [],
            "is_fully_rolled_out": self.is_fully_rolled_out,
        }
