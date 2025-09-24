"""
Enums for the Healthcare SaaS Platform
All enumeration types used across the models
"""

import enum


# Platform User Roles
class PlatformUserRole(str, enum.Enum):
    """Roles for platform administrators"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPPORT = "support"
    DEVELOPER = "developer"


# Organization User Roles
class UserRole(str, enum.Enum):
    """Roles for organization users"""

    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


# Organization Status
class OrganizationStatus(str, enum.Enum):
    """Organization account status"""

    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING = "pending"


# Billing Cycles
class BillingCycle(str, enum.Enum):
    """Billing cycle options"""

    MONTHLY = "monthly"
    ANNUAL = "annual"


# Subscription Status
class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""

    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"


# Invoice Status
class InvoiceStatus(str, enum.Enum):
    """Invoice status"""

    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


# Payment Method Types
class PaymentMethodType(str, enum.Enum):
    """Payment method types"""

    CARD = "card"
    BANK_ACCOUNT = "us_bank_account"
    SEPA_DEBIT = "sepa_debit"
    PAYPAL = "paypal"


# Gender
class Gender(str, enum.Enum):
    """Patient gender options"""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


# Patient Status
class PatientStatus(str, enum.Enum):
    """Patient account status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DECEASED = "deceased"


# Provider Status
class ProviderStatus(str, enum.Enum):
    """Healthcare provider status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


# Agent Types
class AgentType(str, enum.Enum):
    """AI agent types"""

    APPOINTMENT_SCHEDULER = "appointment_scheduler"
    REMINDER_AGENT = "reminder_agent"
    TRIAGE_AGENT = "triage_agent"
    FOLLOW_UP_AGENT = "follow_up_agent"
    CUSTOM = "custom"


# Agent Status
class AgentStatus(str, enum.Enum):
    """AI agent status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    ERROR = "error"
    MAINTENANCE = "maintenance"


# Communication Types
class CommunicationType(str, enum.Enum):
    """Communication channel types"""

    SMS = "sms"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    VOICE_MESSAGE = "voice_message"
    CHAT = "chat"
    PUSH_NOTIFICATION = "push_notification"


# Communication Direction
class CommunicationDirection(str, enum.Enum):
    """Communication direction"""

    INBOUND = "inbound"
    OUTBOUND = "outbound"


# Communication Status
class CommunicationStatus(str, enum.Enum):
    """Communication delivery status"""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Transaction Types
class TransactionType(str, enum.Enum):
    """Credit transaction types"""

    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    BONUS = "bonus"
    ADJUSTMENT = "adjustment"
    EXPIRATION = "expiration"


# Credit Purchase Status
class CreditPurchaseStatus(str, enum.Enum):
    """Credit purchase status"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


# Audit Actions
class AuditAction(str, enum.Enum):
    """Audit log actions"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    VIEW = "view"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"


# Actor Types
class ActorType(str, enum.Enum):
    """Types of actors performing actions"""

    PLATFORM_USER = "platform_user"
    USER = "user"
    API_KEY = "api_key"
    SYSTEM = "system"


# Security Event Types
class SecurityEventType(str, enum.Enum):
    """Security event types"""

    LOGIN_FAILURE = "login_failure"
    SUSPICIOUS_LOGIN = "suspicious_login"
    PASSWORD_BREACH = "password_breach"
    ACCOUNT_LOCKOUT = "account_lockout"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXPORT = "data_export"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    API_ABUSE = "api_abuse"
    BRUTE_FORCE = "brute_force"


# Security Event Severity
class SecurityEventSeverity(str, enum.Enum):
    """Security event severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Alert Types
class AlertType(str, enum.Enum):
    """Credit alert types"""

    LOW_BALANCE = "low_balance"
    USAGE_SPIKE = "usage_spike"
    MONTHLY_LIMIT = "monthly_limit"
    OVERAGE = "overage"


# Integration Types
class IntegrationType(str, enum.Enum):
    """Third-party integration types"""

    EHR = "ehr"  # Electronic Health Records
    TELEPHONY = "telephony"
    EMAIL = "email"
    SMS = "sms"
    CALENDAR = "calendar"
    PAYMENT = "payment"
    CRM = "crm"
    ANALYTICS = "analytics"
    WEBHOOK = "webhook"


# Integration Status
class IntegrationStatus(str, enum.Enum):
    """Integration connection status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    SYNCING = "syncing"


# Workflow Execution Status
class WorkflowExecutionStatus(str, enum.Enum):
    """Workflow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


# Interaction Status
class InteractionStatus(str, enum.Enum):
    """Agent interaction status"""

    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


# Change Types for History Tables
class ChangeType(str, enum.Enum):
    """Types of changes for history tracking"""

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
