"""
Billing, subscription, and credit management models
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    Integer,
    Numeric,
    Text,
    ForeignKey,
    Enum,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import (
    BillingCycle,
    OrganizationStatus,
    SubscriptionStatus,
    InvoiceStatus,
    PaymentMethodType,
    TransactionType,
    CreditPurchaseStatus,
    AlertType,
)


class SubscriptionPlan(BaseModel):
    """Subscription plans with features and pricing"""

    __tablename__ = "subscription_plans"

    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    monthly_price = Column(Numeric(10, 2), nullable=False)
    annual_price = Column(Numeric(10, 2), nullable=False)
    included_credits = Column(Integer, default=0, nullable=False)
    credit_overage_rate = Column(Numeric(10, 4), nullable=False)
    features = Column(JSONB, default=dict)
    limits = Column(JSONB, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    trial_days = Column(Integer, default=0)
    trial_credits = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_plan_active", "is_active"),
        Index("idx_plan_name", "name"),
    )

    # Relationships
    organizations = relationship("Organization", back_populates="subscription_plan")
    subscriptions = relationship("Subscription", back_populates="plan")

    @property
    def monthly_savings(self):
        """Calculate monthly savings when paying annually"""
        if self.annual_price and self.monthly_price:
            annual_monthly_equivalent = self.annual_price / 12
            return self.monthly_price - annual_monthly_equivalent
        return 0

    @property
    def annual_savings_percentage(self):
        """Calculate annual savings percentage"""
        if self.monthly_price > 0:
            annual_equivalent = self.monthly_price * 12
            return ((annual_equivalent - self.annual_price) / annual_equivalent) * 100
        return 0


class CreditPackage(BaseModel):
    """Credit packages available for purchase"""

    __tablename__ = "credit_packages"

    name = Column(String(255), unique=True, nullable=False)
    credit_amount = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost_per_credit = Column(Numeric(10, 4), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    stripe_price_id = Column(String(255))

    __table_args__ = (
        Index("idx_credit_package_active", "is_active"),
        Index("idx_credit_package_amount", "credit_amount"),
    )

    # Relationships
    purchases = relationship("CreditPurchase", back_populates="credit_package")
    auto_recharge_orgs = relationship(
        "Organization",
        foreign_keys="Organization.auto_recharge_package_id",
        back_populates="auto_recharge_package",
    )

    @property
    def value_per_dollar(self):
        """Calculate credits per dollar"""
        return self.credit_amount / self.price if self.price > 0 else 0


class ServicePricing(BaseModel):
    """Pricing for different AI services and models"""

    __tablename__ = "service_pricing"

    service_type = Column(String(100), unique=True, nullable=False)
    provider = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    input_cost_per_unit = Column(Numeric(12, 8), nullable=False)
    output_cost_per_unit = Column(Numeric(12, 8), nullable=False)
    unit_type = Column(String(50), nullable=False)  # tokens, characters, minutes
    credits_per_unit = Column(Numeric(10, 4), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    effective_from = Column(DateTime(timezone=True), server_default=func.now())
    effective_until = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_service_pricing_active", "is_active"),
        Index("idx_service_pricing_type", "service_type"),
        Index("idx_service_pricing_effective", "effective_from", "effective_until"),
    )

    # Relationships
    service_consumptions = relationship(
        "ServiceConsumption", back_populates="service_pricing"
    )


class Organization(BaseModel):
    """Organizations (tenants) in the platform"""

    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    domain = Column(String(255))
    slug = Column(String(100), unique=True, nullable=False)
    subscription_plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id")
    )
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.MONTHLY)
    status = Column(Enum(OrganizationStatus), default=OrganizationStatus.TRIAL)
    current_credits = Column(Integer, default=0)
    monthly_credit_limit = Column(Integer, default=0)
    credit_balance = Column(Numeric(10, 2), default=0)
    auto_recharge_enabled = Column(Boolean, default=False)
    auto_recharge_threshold = Column(Integer, default=1000)
    auto_recharge_package_id = Column(
        UUID(as_uuid=True), ForeignKey("credit_packages.id")
    )
    trial_ends_at = Column(DateTime(timezone=True))
    billing_date = Column(Date)
    stripe_customer_id = Column(String(255), unique=True)
    tax_id = Column(String(100))
    billing_address = Column(JSONB)
    settings = Column(JSONB, default=dict)

    __table_args__ = (
        Index("idx_org_slug", "slug"),
        Index("idx_org_status", "status"),
        Index("idx_org_stripe_customer", "stripe_customer_id"),
        Index("idx_org_trial_ends", "trial_ends_at"),
    )

    # Relationships
    subscription_plan = relationship("SubscriptionPlan", back_populates="organizations")
    auto_recharge_package = relationship(
        "CreditPackage",
        foreign_keys=[auto_recharge_package_id],
        back_populates="auto_recharge_orgs",
    )
    creator = relationship(
        "PlatformUser",
        foreign_keys=[BaseModel.created_by],
        back_populates="created_organizations",
    )
    subscriptions = relationship("Subscription", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")
    users = relationship("User", back_populates="organization")
    credit_transactions = relationship(
        "CreditTransaction", back_populates="organization"
    )
    credit_purchases = relationship("CreditPurchase", back_populates="organization")
    service_consumptions = relationship(
        "ServiceConsumption", back_populates="organization"
    )
    payment_methods = relationship("PaymentMethod", back_populates="organization")
    credit_alerts = relationship("CreditAlert", back_populates="organization")
    usage_quotas = relationship("UsageQuota", back_populates="organization")

    @property
    def is_trial(self):
        """Check if organization is on trial"""
        return self.status == OrganizationStatus.TRIAL

    @property
    def is_active(self):
        """Check if organization is active"""
        return self.status == OrganizationStatus.ACTIVE

    @property
    def trial_days_remaining(self):
        """Calculate remaining trial days"""
        if self.trial_ends_at and self.is_trial:
            remaining = self.trial_ends_at - datetime.utcnow()
            return max(0, remaining.days)
        return 0

    @property
    def credit_usage_percentage(self):
        """Calculate credit usage as percentage of limit"""
        if self.monthly_credit_limit > 0:
            return (self.current_credits / self.monthly_credit_limit) * 100
        return 0


class Subscription(BaseModel):
    """Active subscriptions for organizations"""

    __tablename__ = "subscriptions"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False
    )
    status = Column(Enum(SubscriptionStatus), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True)
    amount = Column(Numeric(10, 2), nullable=False)
    billing_cycle = Column(Enum(BillingCycle), nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    trial_end = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_subscription_org", "org_id"),
        Index("idx_subscription_status", "status"),
        Index("idx_subscription_stripe", "stripe_subscription_id"),
        Index("idx_subscription_period", "current_period_start", "current_period_end"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription")

    @property
    def is_active(self):
        """Check if subscription is active"""
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def is_cancelled(self):
        """Check if subscription is cancelled"""
        return self.status == SubscriptionStatus.CANCELLED

    @property
    def days_until_renewal(self):
        """Calculate days until next billing period"""
        remaining = self.current_period_end - datetime.utcnow()
        return max(0, remaining.days)


class Invoice(BaseModel):
    """Billing invoices"""

    __tablename__ = "invoices"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"))
    stripe_invoice_id = Column(String(255), unique=True)
    number = Column(String(100), unique=True, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(InvoiceStatus), nullable=False)
    line_items = Column(JSONB, default=list)
    due_date = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    payment_method = Column(String(100))

    __table_args__ = (
        Index("idx_invoice_org", "org_id"),
        Index("idx_invoice_status", "status"),
        Index("idx_invoice_number", "number"),
        Index("idx_invoice_due_date", "due_date"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")

    @property
    def is_paid(self):
        """Check if invoice is paid"""
        return self.status == InvoiceStatus.PAID

    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return (
            self.due_date
            and self.due_date < datetime.utcnow()
            and self.status != InvoiceStatus.PAID
        )


class PaymentMethod(BaseModel):
    """Organization payment methods"""

    __tablename__ = "payment_methods"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    stripe_payment_method_id = Column(String(255), unique=True, nullable=False)
    type = Column(Enum(PaymentMethodType), nullable=False)
    details = Column(JSONB, default=dict)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("idx_payment_method_org", "org_id"),
        Index("idx_payment_method_stripe", "stripe_payment_method_id"),
        Index("idx_payment_method_default", "org_id", "is_default"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="payment_methods")


class CreditTransaction(BaseModel):
    """Credit usage and purchase transactions"""

    __tablename__ = "credit_transactions"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    credits_amount = Column(Integer, nullable=False)
    cost_usd = Column(Numeric(10, 4))
    service_type = Column(String(100))
    provider = Column(String(100))
    model_used = Column(String(100))
    related_entity_id = Column(UUID(as_uuid=True))
    usage_details = Column(JSONB)
    reference_id = Column(String(255))
    balance_after = Column(Integer, nullable=False)

    __table_args__ = (
        Index("idx_credit_transaction_org", "org_id"),
        Index("idx_credit_transaction_type", "transaction_type"),
        Index("idx_credit_transaction_created", "created_at"),
        Index("idx_credit_transaction_service", "service_type"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="credit_transactions")


class CreditPurchase(BaseModel):
    """Credit package purchases"""

    __tablename__ = "credit_purchases"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    credit_package_id = Column(
        UUID(as_uuid=True), ForeignKey("credit_packages.id"), nullable=False
    )
    credits_purchased = Column(Integer, nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    stripe_payment_intent_id = Column(String(255), unique=True)
    status = Column(Enum(CreditPurchaseStatus), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    purchased_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        Index("idx_credit_purchase_org", "org_id"),
        Index("idx_credit_purchase_status", "status"),
        Index("idx_credit_purchase_stripe", "stripe_payment_intent_id"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="credit_purchases")
    credit_package = relationship("CreditPackage", back_populates="purchases")


class ServiceConsumption(BaseModel):
    """Detailed service usage tracking"""

    __tablename__ = "service_consumption"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("agent_interactions.id"))
    service_type = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=False)
    model_used = Column(String(100), nullable=False)
    input_units = Column(Integer, default=0)
    output_units = Column(Integer, default=0)
    input_cost_usd = Column(Numeric(10, 6), default=0)
    output_cost_usd = Column(Numeric(10, 6), default=0)
    total_cost_usd = Column(Numeric(10, 6), nullable=False)
    credits_consumed = Column(Integer, nullable=False)
    raw_provider_response = Column(JSONB)
    consumed_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_service_consumption_org", "org_id"),
        Index("idx_service_consumption_interaction", "interaction_id"),
        Index("idx_service_consumption_service", "service_type"),
        Index("idx_service_consumption_consumed", "consumed_at"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="service_consumptions")
    service_pricing = relationship(
        "ServicePricing", back_populates="service_consumptions"
    )


class CreditAlert(BaseModel):
    """Credit usage alerts and notifications"""

    __tablename__ = "credit_alerts"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    threshold_percentage = Column(Integer, nullable=False)
    is_enabled = Column(Boolean, default=True)
    notification_settings = Column(JSONB, default=dict)
    last_triggered = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_credit_alert_org", "org_id"),
        Index("idx_credit_alert_type", "alert_type"),
        Index("idx_credit_alert_enabled", "is_enabled"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="credit_alerts")


class UsageQuota(BaseModel):
    """Service usage quotas and limits"""

    __tablename__ = "usage_quotas"

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    service_type = Column(String(100), nullable=False)
    daily_limit = Column(Integer, default=0)
    monthly_limit = Column(Integer, default=0)
    current_daily_usage = Column(Integer, default=0)
    current_monthly_usage = Column(Integer, default=0)
    current_period_start = Column(Date, server_default=func.current_date())
    enforce_limits = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("org_id", "service_type", name="uq_usage_quota_org_service"),
        Index("idx_usage_quota_org", "org_id"),
        Index("idx_usage_quota_service", "service_type"),
        Index("idx_usage_quota_period", "current_period_start"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="usage_quotas")

    @property
    def daily_usage_percentage(self):
        """Calculate daily usage percentage"""
        if self.daily_limit > 0:
            return (self.current_daily_usage / self.daily_limit) * 100
        return 0

    @property
    def monthly_usage_percentage(self):
        """Calculate monthly usage percentage"""
        if self.monthly_limit > 0:
            return (self.current_monthly_usage / self.monthly_limit) * 100
        return 0

    @property
    def is_daily_limit_exceeded(self):
        """Check if daily limit is exceeded"""
        return self.enforce_limits and self.current_daily_usage >= self.daily_limit

    @property
    def is_monthly_limit_exceeded(self):
        """Check if monthly limit is exceeded"""
        return self.enforce_limits and self.current_monthly_usage >= self.monthly_limit
