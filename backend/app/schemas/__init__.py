"""
Healthcare SaaS Platform - Schemas Package
Pydantic v2 schemas for request/response validation
"""

from .base import BaseSchema, TimestampMixin, UUIDMixin, PaginatedResponse
from .platform import *
from .billing import *
from .users import *
from .healthcare import *
from .agents import *
from .communication import *
from .analytics import *
from .common import *

# Export all schemas
__all__ = [
    # Base
    "BaseSchema",
    "TimestampMixin",
    "UUIDMixin",
    "PaginatedResponse",
    # Platform
    "PlatformUserBase",
    "PlatformUserCreate",
    "PlatformUserUpdate",
    "PlatformUserResponse",
    # Billing
    "SubscriptionPlanBase",
    "SubscriptionPlanCreate",
    "SubscriptionPlanUpdate",
    "SubscriptionPlanResponse",
    "CreditPackageBase",
    "CreditPackageCreate",
    "CreditPackageUpdate",
    "CreditPackageResponse",
    "ServicePricingBase",
    "ServicePricingCreate",
    "ServicePricingUpdate",
    "ServicePricingResponse",
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationUpdate",
    "OrganizationResponse",
    "CreditTransactionResponse",
    "CreditPurchaseCreate",
    "CreditPurchaseResponse",
    "ServiceConsumptionResponse",
    # Users
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInvitationCreate",
    "UserInvitationResponse",
    # Healthcare
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "ProviderBase",
    "ProviderCreate",
    "ProviderUpdate",
    "ProviderResponse",
    "AppointmentBase",
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "FacilityTypeResponse",
    "LocationBase",
    "LocationCreate",
    "LocationUpdate",
    "LocationResponse",
    "AppointmentTypeBase",
    "AppointmentTypeCreate",
    "AppointmentTypeUpdate",
    "AppointmentTypeResponse",
    # Agents
    "AgentBase",
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "AgentInteractionBase",
    "AgentInteractionCreate",
    "AgentInteractionResponse",
    # Communication
    "CommunicationBase",
    "CommunicationCreate",
    "CommunicationUpdate",
    "CommunicationResponse",
    # Analytics
    "UsageStatsResponse",
    "CreditBalanceResponse",
    "TopConsumingAgentsResponse",
    # Common
    "ErrorResponse",
    "ValidationErrorResponse",
    "HealthCheckResponse",
    "BulkDeleteRequest",
    "BulkDeleteResponse",
    "BulkUpdateRequest",
    "BulkUpdateResponse",
]
