"""
Billing and subscription-related schemas
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import Field, field_validator, computed_field
from pydantic.types import PositiveInt, NonNegativeInt

from .base import BaseSchema, TimestampMixin, UUIDMixin
from ..models.enums import (
    BillingCycle,
    OrganizationStatus,
    TransactionType,
    CreditPurchaseStatus,
)


class SubscriptionPlanBase(BaseSchema):
    """Base subscription plan fields"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    monthly_price: Decimal = Field(..., ge=0, decimal_places=2)
    annual_price: Decimal = Field(..., ge=0, decimal_places=2)
    included_credits: NonNegativeInt = 0
    credit_overage_rate: Decimal = Field(0.01, ge=0, decimal_places=4)
    features: Dict[str, Any] = Field(default_factory=dict)
    limits: Dict[str, Any] = Field(default_factory=dict)
    trial_days: PositiveInt = 14
    trial_credits: NonNegativeInt = 100


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating subscription plans"""

    pass


class SubscriptionPlanUpdate(BaseSchema):
    """Schema for updating subscription plans"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    monthly_price: Optional[Decimal] = Field(None, ge=0)
    annual_price: Optional[Decimal] = Field(None, ge=0)
    included_credits: Optional[NonNegativeInt] = None
    credit_overage_rate: Optional[Decimal] = Field(None, ge=0)
    features: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(SubscriptionPlanBase, UUIDMixin, TimestampMixin):
    """Subscription plan response schema"""

    is_active: bool


class CreditPackageBase(BaseSchema):
    """Base credit package fields"""

    name: str = Field(..., min_length=1, max_length=100)
    credit_amount: PositiveInt
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stripe_price_id: Optional[str] = Field(None, max_length=100)

    @computed_field
    @property
    def cost_per_credit(self) -> Decimal:
        """Calculate cost per credit"""
        return self.price / self.credit_amount


class CreditPackageCreate(CreditPackageBase):
    """Schema for creating credit packages"""

    pass


class CreditPackageUpdate(BaseSchema):
    """Schema for updating credit packages"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    credit_amount: Optional[PositiveInt] = None
    price: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None
    stripe_price_id: Optional[str] = Field(None, max_length=100)


class CreditPackageResponse(CreditPackageBase, UUIDMixin, TimestampMixin):
    """Credit package response schema"""

    cost_per_credit: Decimal
    is_active: bool


class ServicePricingBase(BaseSchema):
    """Base service pricing fields"""

    service_type: str = Field(..., max_length=100)
    provider: str = Field(..., max_length=100)
    model_name: str = Field(..., max_length=100)
    input_cost_per_unit: Decimal = Field(..., ge=0, decimal_places=8)
    output_cost_per_unit: Decimal = Field(..., ge=0, decimal_places=8)
    unit_type: str = Field(..., max_length=50)  # token, second, minute, message
    credits_per_unit: Decimal = Field(..., ge=0, decimal_places=4)
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None


class ServicePricingCreate(ServicePricingBase):
    """Schema for creating service pricing"""

    pass


class ServicePricingUpdate(BaseSchema):
    """Schema for updating service pricing"""

    input_cost_per_unit: Optional[Decimal] = Field(None, ge=0)
    output_cost_per_unit: Optional[Decimal] = Field(None, ge=0)
    credits_per_unit: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    effective_until: Optional[datetime] = None


class ServicePricingResponse(ServicePricingBase, UUIDMixin, TimestampMixin):
    """Service pricing response schema"""

    is_active: bool


class OrganizationBase(BaseSchema):
    """Base organization fields"""

    name: str = Field(..., min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    slug: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="Slug should only contain lowercase letters, numbers, and hyphens",
    )
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    monthly_credit_limit: NonNegativeInt = 1000
    auto_recharge_enabled: bool = False
    auto_recharge_threshold: NonNegativeInt = 100
    tax_id: Optional[str] = Field(None, max_length=100)
    billing_address: Optional[Dict[str, Any]] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format"""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Slug must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v.lower()


class OrganizationCreate(OrganizationBase):
    """Schema for creating organizations"""

    subscription_plan_id: UUID
    auto_recharge_package_id: Optional[UUID] = None


class OrganizationUpdate(BaseSchema):
    """Schema for updating organizations"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    billing_cycle: Optional[BillingCycle] = None
    monthly_credit_limit: Optional[NonNegativeInt] = None
    auto_recharge_enabled: Optional[bool] = None
    auto_recharge_threshold: Optional[NonNegativeInt] = None
    auto_recharge_package_id: Optional[UUID] = None
    tax_id: Optional[str] = Field(None, max_length=100)
    billing_address: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(OrganizationBase, UUIDMixin, TimestampMixin):
    """Organization response schema"""

    subscription_plan_id: UUID
    status: OrganizationStatus
    current_credits: NonNegativeInt
    credit_balance: Decimal
    auto_recharge_package_id: Optional[UUID] = None
    trial_ends_at: Optional[datetime] = None
    billing_date: Optional[date] = None
    stripe_customer_id: Optional[str] = None


class CreditTransactionResponse(UUIDMixin, TimestampMixin):
    """Credit transaction response schema"""

    org_id: UUID
    transaction_type: TransactionType
    credits_amount: int  # Can be negative for consumption
    cost_usd: Optional[Decimal] = Field(None, decimal_places=2)
    service_type: Optional[str] = Field(None, max_length=100)
    provider: Optional[str] = Field(None, max_length=100)
    model_used: Optional[str] = Field(None, max_length=100)
    usage_details: Optional[Dict[str, Any]] = None
    reference_id: Optional[str] = Field(None, max_length=100)
    related_entity_id: Optional[UUID] = None
    balance_after: int
    created_by: Optional[UUID] = None


class CreditPurchaseBase(BaseSchema):
    """Base credit purchase fields"""

    credit_package_id: UUID
    credits_purchased: PositiveInt
    amount_paid: Decimal = Field(..., gt=0, decimal_places=2)


class CreditPurchaseCreate(CreditPurchaseBase):
    """Schema for creating credit purchases"""

    org_id: UUID


class CreditPurchaseResponse(CreditPurchaseBase, UUIDMixin, TimestampMixin):
    """Credit purchase response schema"""

    org_id: UUID
    stripe_payment_intent_id: Optional[str] = None
    status: CreditPurchaseStatus
    purchased_by: Optional[UUID] = None
    completed_at: Optional[datetime] = None


class ServiceConsumptionBase(BaseSchema):
    """Base service consumption fields"""

    service_type: str = Field(..., max_length=100)
    provider: str = Field(..., max_length=100)
    model_used: str = Field(..., max_length=100)
    input_units: NonNegativeInt = 0
    output_units: NonNegativeInt = 0
    input_cost_usd: Decimal = Field(0, ge=0, decimal_places=8)
    output_cost_usd: Decimal = Field(0, ge=0, decimal_places=8)
    credits_consumed: NonNegativeInt

    @computed_field
    @property
    def total_cost_usd(self) -> Decimal:
        """Calculate total cost"""
        return self.input_cost_usd + self.output_cost_usd


class ServiceConsumptionResponse(ServiceConsumptionBase, UUIDMixin, TimestampMixin):
    """Service consumption response schema"""

    org_id: UUID
    interaction_id: Optional[UUID] = None
    total_cost_usd: Decimal
    raw_provider_response: Optional[Dict[str, Any]] = None
    consumed_at: datetime
