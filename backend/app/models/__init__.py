"""
Healthcare SaaS Platform - Models Package
SQLAlchemy models with proper imports and exports
"""

from .base import Base, BaseModel
from .enums import *
from .platform import PlatformUser, PlatformSetting
from .billing import (
    SubscriptionPlan,
    CreditPackage,
    ServicePricing,
    Organization,
    Subscription,
    Invoice,
    PaymentMethod,
    CreditTransaction,
    CreditPurchase,
    ServiceConsumption,
    CreditAlert,
    UsageQuota,
)
from .users import User, UserSession, UserInvitation
from .api import APIKey, APIRequest, Integration, Webhook, WebhookDelivery
from .agents import Agent, AgentInteraction
from .healthcare import (
    Patient,
    Provider,
    Department,
    Facility,
    FacilityType,
    Location,
    AppointmentType,
    AppointmentStatus,
    Appointment,
)
from .communication import Communication, CommunicationTemplate
from .workflows import Workflow, WorkflowExecution
from .audit import AuditLog, SecurityEvent, FeatureFlag
from .history import (
    OrganizationHistory,
    UserHistory,
    PatientHistory,
    AppointmentHistory,
    AgentHistory,
    ProviderHistory,
    FacilityHistory,
)

# Export all models for easy importing
__all__ = [
    # Base
    "Base",
    "BaseModel",
    # Enums
    "PlatformUserRole",
    "UserRole",
    "OrganizationStatus",
    "BillingCycle",
    "SubscriptionStatus",
    "InvoiceStatus",
    "PaymentMethodType",
    "Gender",
    "PatientStatus",
    "ProviderStatus",
    "AgentType",
    "AgentStatus",
    "CommunicationType",
    "CommunicationDirection",
    "CommunicationStatus",
    "TransactionType",
    "CreditPurchaseStatus",
    "AuditAction",
    "ActorType",
    "SecurityEventType",
    "SecurityEventSeverity",
    "AlertType",
    "IntegrationType",
    "IntegrationStatus",
    "WorkflowExecutionStatus",
    "InteractionStatus",
    "ChangeType",
    # Platform
    "PlatformUser",
    "PlatformSetting",
    # Billing
    "SubscriptionPlan",
    "CreditPackage",
    "ServicePricing",
    "Organization",
    "Subscription",
    "Invoice",
    "PaymentMethod",
    "CreditTransaction",
    "CreditPurchase",
    "ServiceConsumption",
    "CreditAlert",
    "UsageQuota",
    # Users
    "User",
    "UserSession",
    "UserInvitation",
    # API & Integrations
    "APIKey",
    "APIRequest",
    "Integration",
    "Webhook",
    "WebhookDelivery",
    # Agents
    "Agent",
    "AgentInteraction",
    # Healthcare
    "Patient",
    "Provider",
    "Department",
    "Facility",
    "FacilityType",
    "Location",
    "AppointmentType",
    "AppointmentStatus",
    "Appointment",
    # Communication
    "Communication",
    "CommunicationTemplate",
    # Workflows
    "Workflow",
    "WorkflowExecution",
    # Audit & Security
    "AuditLog",
    "SecurityEvent",
    "FeatureFlag",
    # History
    "OrganizationHistory",
    "UserHistory",
    "PatientHistory",
    "AppointmentHistory",
    "AgentHistory",
    "ProviderHistory",
    "FacilityHistory",
]
