"""
Historical data tracking models for audit trails
"""

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    Text,
    Integer,
    Numeric,
    ForeignKey,
    Enum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base  # Note: History tables don't inherit from BaseModel
from .enums import (
    PlatformUserRole,
    UserRole,
    Gender,
    PatientStatus,
    ProviderStatus,
    AgentType,
    AgentStatus,
    OrganizationStatus,
    BillingCycle,
    ChangeType,
)


class PlatformUsersHistory(Base):
    """Historical changes to platform users"""

    __tablename__ = "platform_users_history"

    id = Column(UUID(as_uuid=True), primary_key=True)
    platform_user_id = Column(
        UUID(as_uuid=True), ForeignKey("platform_users.id"), nullable=False
    )
    email = Column(String(255))
    password_hash = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(Enum(PlatformUserRole))
    is_active = Column(Boolean)
    last_login = Column(DateTime(timezone=True))
    timezone = Column(String(50))

    # Original timestamps
    original_created_at = Column(DateTime(timezone=True))
    original_updated_at = Column(DateTime(timezone=True))
    original_created_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_updated_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_deleted_at = Column(DateTime(timezone=True))
    original_deleted_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))

    # Change tracking
    change_type = Column(Enum(ChangeType), nullable=False)
    changed_fields = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    changed_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_platform_users_history_user", "platform_user_id"),
        Index("idx_platform_users_history_change", "change_type"),
        Index("idx_platform_users_history_changed_at", "changed_at"),
    )

    # Relationships
    platform_user = relationship("PlatformUser", foreign_keys=[platform_user_id])
    changer = relationship("PlatformUser", foreign_keys=[changed_by])


class SubscriptionPlansHistory(Base):
    """Historical changes to subscription plans"""

    __tablename__ = "subscription_plans_history"

    id = Column(UUID(as_uuid=True), primary_key=True)
    subscription_plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False
    )
    name = Column(String(255))
    description = Column(Text)
    monthly_price = Column(Numeric(10, 2))
    annual_price = Column(Numeric(10, 2))
    included_credits = Column(Integer)
    credit_overage_rate = Column(Numeric(10, 4))
    features = Column(JSONB)
    limits = Column(JSONB)
    is_active = Column(Boolean)
    trial_days = Column(Integer)
    trial_credits = Column(Integer)

    # Original timestamps
    original_created_at = Column(DateTime(timezone=True))
    original_updated_at = Column(DateTime(timezone=True))
    original_created_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_updated_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_deleted_at = Column(DateTime(timezone=True))
    original_deleted_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))

    # Change tracking
    change_type = Column(Enum(ChangeType), nullable=False)
    changed_fields = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    changed_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_subscription_plans_history_plan", "subscription_plan_id"),
        Index("idx_subscription_plans_history_change", "change_type"),
        Index("idx_subscription_plans_history_changed_at", "changed_at"),
    )

    # Relationships
    subscription_plan = relationship(
        "SubscriptionPlan", foreign_keys=[subscription_plan_id]
    )


class OrganizationHistory(Base):
    """Historical changes to organizations"""

    __tablename__ = "organizations_history"

    id = Column(UUID(as_uuid=True), primary_key=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255))
    domain = Column(String(255))
    slug = Column(String(100))
    subscription_plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id")
    )
    billing_cycle = Column(Enum(BillingCycle))
    status = Column(Enum(OrganizationStatus))
    current_credits = Column(Integer)
    monthly_credit_limit = Column(Integer)
    credit_balance = Column(Numeric(10, 2))
    auto_recharge_enabled = Column(Boolean)
    auto_recharge_threshold = Column(Integer)
    auto_recharge_package_id = Column(
        UUID(as_uuid=True), ForeignKey("credit_packages.id")
    )
    trial_ends_at = Column(DateTime(timezone=True))
    billing_date = Column(Date)
    stripe_customer_id = Column(String(255))
    tax_id = Column(String(100))
    billing_address = Column(JSONB)
    settings = Column(JSONB)

    # Original timestamps
    original_created_at = Column(DateTime(timezone=True))
    original_updated_at = Column(DateTime(timezone=True))
    original_created_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_updated_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_deleted_at = Column(DateTime(timezone=True))
    original_deleted_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))

    # Change tracking
    change_type = Column(Enum(ChangeType), nullable=False)
    changed_fields = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    changed_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_organizations_history_org", "org_id"),
        Index("idx_organizations_history_change", "change_type"),
        Index("idx_organizations_history_changed_at", "changed_at"),
    )

    # Relationships
    organization = relationship("Organization", foreign_keys=[org_id])


class UserHistory(Base):
    """Historical changes to users"""

    __tablename__ = "users_history"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    email = Column(String(255))
    password_hash = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(Enum(UserRole))
    permissions = Column(JSONB)
    is_active = Column(Boolean)
    is_blocked = Column(Boolean)
    phone = Column(String(50))
    timezone = Column(String(50))
    preferences = Column(JSONB)
    email_verified_at = Column(DateTime(timezone=True))
    last_login = Column(DateTime(timezone=True))
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime(timezone=True))

    # Original timestamps
    original_created_at = Column(DateTime(timezone=True))
    original_updated_at = Column(DateTime(timezone=True))
    original_created_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_updated_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_deleted_at = Column(DateTime(timezone=True))
    original_deleted_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))

    # Change tracking
    change_type = Column(Enum(ChangeType), nullable=False)
    changed_fields = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    changed_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_users_history_user", "user_id"),
        Index("idx_users_history_org", "org_id"),
        Index("idx_users_history_change", "change_type"),
        Index("idx_users_history_changed_at", "changed_at"),
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization", foreign_keys=[org_id])


class PatientHistory(Base):
    """Historical changes to patients"""

    __tablename__ = "patients_history"

    id = Column(UUID(as_uuid=True), primary_key=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    mrn = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    dob = Column(Date)
    gender = Column(Enum(Gender))
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(JSONB)
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(50))
    insurance_info = Column(JSONB)
    preferences = Column(JSONB)
    status = Column(Enum(PatientStatus))
    consent_ai_communication = Column(Boolean)

    # Original timestamps
    original_created_at = Column(DateTime(timezone=True))
    original_updated_at = Column(DateTime(timezone=True))
    original_created_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_updated_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_deleted_at = Column(DateTime(timezone=True))
    original_deleted_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))

    # Change tracking
    change_type = Column(Enum(ChangeType), nullable=False)
    changed_fields = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    changed_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_patients_history_patient", "patient_id"),
        Index("idx_patients_history_org", "org_id"),
        Index("idx_patients_history_change", "change_type"),
        Index("idx_patients_history_changed_at", "changed_at"),
    )

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])
    organization = relationship("Organization", foreign_keys=[org_id])


class ProviderHistory(Base):
    """Historical changes to providers"""

    __tablename__ = "providers_history"

    id = Column(UUID(as_uuid=True), primary_key=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    first_name = Column(String(100))
    last_name = Column(String(100))
    specialty = Column(String(255))
    npi_number = Column(String(20))
    license_number = Column(String(50))
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"))
    schedule = Column(JSONB)
    accepts_new_patients = Column(Boolean)
    status = Column(Enum(ProviderStatus))

    # Original timestamps
    original_created_at = Column(DateTime(timezone=True))
    original_updated_at = Column(DateTime(timezone=True))
    original_created_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_updated_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_deleted_at = Column(DateTime(timezone=True))
    original_deleted_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))

    # Change tracking
    change_type = Column(Enum(ChangeType), nullable=False)
    changed_fields = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    changed_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_providers_history_provider", "provider_id"),
        Index("idx_providers_history_org", "org_id"),
        Index("idx_providers_history_change", "change_type"),
        Index("idx_providers_history_changed_at", "changed_at"),
    )

    # Relationships
    provider = relationship("Provider", foreign_keys=[provider_id])
    organization = relationship("Organization", foreign_keys=[org_id])


class AgentHistory(Base):
    """Historical changes to agents"""

    __tablename__ = "agents_history"

    id = Column(UUID(as_uuid=True), primary_key=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    name = Column(String(255))
    description = Column(Text)
    type = Column(Enum(AgentType))
    status = Column(Enum(AgentStatus))
    config = Column(JSONB)
    api_keys = Column(JSONB)
    version = Column(String(50))
    metrics = Column(JSONB)
    is_public = Column(Boolean)

    # Original timestamps
    original_created_at = Column(DateTime(timezone=True))
    original_updated_at = Column(DateTime(timezone=True))
    original_created_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_updated_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    original_deleted_at = Column(DateTime(timezone=True))
    original_deleted_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))

    # Change tracking
    change_type = Column(Enum(ChangeType), nullable=False)
    changed_fields = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("platform_users.id"))
    changed_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_agents_history_agent", "agent_id"),
        Index("idx_agents_history_org", "org_id"),
        Index("idx_agents_history_change", "change_type"),
        Index("idx_agents_history_changed_at", "changed_at"),
    )

    # Relationships
    agent = relationship("Agent", foreign_keys=[agent_id])
    organization = relationship("Organization", foreign_keys=[org_id])


# class AppointmentHistory(Base):
#     """Historical changes to appointments"""

#     __tablename__ = "appointments_history"

#     id = Column(UUID(as_uuid=True), primary_key=True)
#     appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False)
#     org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
#     confirmation_code = Column(String(20))
#     patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"))
#     provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"))
#     department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
#     facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id"))
#     appointment_type_id = Column(UUID(as_uuid=True), ForeignKey("appointment_types.id"))
#     status_id = Column(UUID(as_uuid=True), Foreign
