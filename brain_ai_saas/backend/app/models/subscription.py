"""
Subscription models for billing and plan management
Manage tenant subscriptions and billing information
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class SubscriptionBase(BaseModel):
    """Base subscription model"""
    plan: str = Field(..., pattern="^(free|starter|professional|enterprise)$", description="Subscription plan")
    status: str = Field(..., pattern="^(active|cancelled|past_due|incomplete|incomplete_expired|trialing|unpaid)$", description="Subscription status")


class SubscriptionCreate(SubscriptionBase):
    """Model for creating a subscription"""
    tenant_id: uuid.UUID = Field(..., description="Tenant ID")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")


class SubscriptionUpdate(BaseModel):
    """Model for updating a subscription"""
    plan: Optional[str] = Field(None, pattern="^(free|starter|professional|enterprise)$")
    status: Optional[str] = Field(None, pattern="^(active|cancelled|past_due|incomplete|incomplete_expired|trialing|unpaid)$")
    stripe_subscription_id: Optional[str] = None


class Subscription(SubscriptionBase):
    """Complete subscription model"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    stripe_subscription_id: Optional[str]
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    """Subscription response model"""
    id: uuid.UUID
    plan: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlanLimits(BaseModel):
    """Plan limits and features"""
    plan_name: str
    monthly_price: float
    max_projects: int
    max_memories: int
    max_api_calls_per_month: int
    max_storage_gb: float
    max_bandwidth_gb_per_month: float
    rate_limit_per_minute: int
    priority_support: bool
    custom_integrations: bool
    white_label: bool
    sla_guarantee: Optional[str] = None
    features: list[str]


class BillingUsage(BaseModel):
    """Billing usage for current period"""
    period_start: datetime
    period_end: datetime
    projects_used: int
    projects_limit: Optional[int]
    memories_used: int
    memories_limit: Optional[int]
    api_calls_used: int
    api_calls_limit: Optional[int]
    storage_used_gb: float
    storage_limit_gb: Optional[float]
    bandwidth_used_gb: float
    bandwidth_limit_gb: Optional[float]
    overage_cost: Optional[float] = None


class Invoice(BaseModel):
    """Invoice information"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    stripe_invoice_id: str
    amount_due: float
    amount_paid: float
    currency: str
    status: str
    due_date: datetime
    period_start: datetime
    period_end: datetime
    created_at: datetime


class PaymentMethod(BaseModel):
    """Payment method information"""
    id: str
    type: str
    brand: Optional[str] = None
    last4: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False
    created_at: datetime


class BillingPortalSession(BaseModel):
    """Billing portal session for customer self-service"""
    url: str
    expires_at: datetime


# Plan definitions
PLANS = {
    "free": PlanLimits(
        plan_name="Free",
        monthly_price=0.0,
        max_projects=1,
        max_memories=1000,
        max_api_calls_per_month=10000,
        max_storage_gb=0.1,
        max_bandwidth_gb_per_month=1.0,
        rate_limit_per_minute=10,
        priority_support=False,
        custom_integrations=False,
        white_label=False,
        features=[
            "Basic memory management",
            "Simple reasoning",
            "Community support",
            "1 project",
            "1,000 memories"
        ]
    ),
    "starter": PlanLimits(
        plan_name="Starter",
        monthly_price=99.0,
        max_projects=5,
        max_memories=10000,
        max_api_calls_per_month=100000,
        max_storage_gb=1.0,
        max_bandwidth_gb_per_month=10.0,
        rate_limit_per_minute=100,
        priority_support=False,
        custom_integrations=False,
        white_label=False,
        features=[
            "All memory types",
            "Learning system",
            "Basic analytics",
            "Email support",
            "5 projects",
            "10,000 memories"
        ]
    ),
    "professional": PlanLimits(
        plan_name="Professional",
        monthly_price=499.0,
        max_projects=25,
        max_memories=100000,
        max_api_calls_per_month=1000000,
        max_storage_gb=10.0,
        max_bandwidth_gb_per_month=100.0,
        rate_limit_per_minute=500,
        priority_support=True,
        custom_integrations=True,
        white_label=False,
        features=[
            "Advanced analytics",
            "Priority support",
            "Custom integrations",
            "API access",
            "25 projects",
            "100,000 memories"
        ]
    ),
    "enterprise": PlanLimits(
        plan_name="Enterprise",
        monthly_price=2499.0,
        max_projects=-1,  # Unlimited
        max_memories=-1,  # Unlimited
        max_api_calls_per_month=-1,  # Unlimited
        max_storage_gb=100.0,
        max_bandwidth_gb_per_month=1000.0,
        rate_limit_per_minute=2000,
        priority_support=True,
        custom_integrations=True,
        white_label=True,
        sla_guarantee="99.9% uptime",
        features=[
            "White-label solution",
            "Dedicated support",
            "Custom development",
            "SLA guarantee",
            "Unlimited projects",
            "Unlimited memories",
            "Priority processing"
        ]
    )
}
