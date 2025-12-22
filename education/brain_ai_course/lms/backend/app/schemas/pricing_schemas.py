"""
Pricing and Revenue Schemas for Brain AI LMS API
Handles course pricing, payments, subscriptions, and revenue analytics
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CourseTier(str, Enum):
    FOUNDATION = "foundation"
    IMPLEMENTATION = "implementation" 
    MASTERY = "mastery"
    CORPORATE = "corporate"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"

# Course Pricing Schemas
class CoursePricingBase(BaseModel):
    course_id: int = Field(..., description="Course ID")
    tier: CourseTier = Field(..., description="Course tier level")
    price: float = Field(..., ge=0, description="Course price in USD")
    currency: str = Field(default="USD", description="Currency code")
    duration_hours: int = Field(..., gt=0, description="Course duration in hours")
    description: Optional[str] = Field(None, description="Pricing tier description")
    features: Optional[str] = Field(None, description="JSON string of features")
    max_students: int = Field(default=50, ge=1, description="Maximum students allowed")
    early_bird_discount: float = Field(default=0.0, ge=0, le=100, description="Early bird discount percentage")
    corporate_discount: float = Field(default=0.0, ge=0, le=100, description="Corporate discount percentage")
    is_active: bool = Field(default=True, description="Whether this pricing tier is active")

class CoursePricingCreate(CoursePricingBase):
    pass

class CoursePricingUpdate(BaseModel):
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    features: Optional[str] = None
    max_students: Optional[int] = Field(None, ge=1)
    early_bird_discount: Optional[float] = Field(None, ge=0, le=100)
    corporate_discount: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None

class CoursePricing(CoursePricingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Payment Schemas
class PaymentBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    course_pricing_id: int = Field(..., description="Course pricing ID")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    discount_applied: float = Field(default=0.0, ge=0, le=100, description="Discount percentage applied")
    final_amount: float = Field(..., gt=0, description="Final amount after discount")
    payment_method: Optional[str] = Field(None, description="Payment method used")
    billing_address: Optional[str] = Field(None, description="Billing PaymentCreate(Payment address JSON")

classBase):
    pass

class Payment(PaymentBase):
    id: int
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str]
    stripe_customer_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Refund Request Schemas
class RefundRequestBase(BaseModel):
    payment_id: int = Field(..., description="Payment ID to refund")
    amount: float = Field(..., gt=0, description="Refund amount")
    reason: str = Field(..., min_length=10, max_length=1000, description="Refund reason")

class RefundRequestCreate(RefundRequestBase):
    pass

class RefundRequest(RefundRequestBase):
    id: int
    user_id: int
    status: str
    admin_notes: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    plan_name: str = Field(..., min_length=1, max_length=100, description="Subscription plan name")
    amount: float = Field(..., gt=0, description="Subscription amount")
    currency: str = Field(default="USD", description="Currency code")
    current_period_start: Optional[datetime] = Field(None, description="Current period start")
    current_period_end: Optional[datetime] = Field(None, description="Current period end")
    cancel_at_period_end: bool = Field(default=False, description="Cancel at period end")

class SubscriptionCreate(SubscriptionBase):
    stripe_subscription_id: str = Field(..., description="Stripe subscription ID")

class Subscription(SubscriptionBase):
    id: int
    status: SubscriptionStatus
    stripe_subscription_id: str
    started_at: datetime
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Revenue Analytics Schemas
class RevenueAnalytics(BaseModel):
    date: datetime
    total_revenue: float = Field(default=0.0)
    course_revenue: float = Field(default=0.0)
    subscription_revenue: float = Field(default=0.0)
    new_customers: int = Field(default=0)
    churned_customers: int = Field(default=0)
    average_order_value: float = Field(default=0.0)
    conversion_rate: float = Field(default=0.0)
    refunds_processed: int = Field(default=0)
    refunds_amount: float = Field(default=0.0)

class RevenueAnalyticsRequest(BaseModel):
    start_date: datetime = Field(..., description="Start date for analytics")
    end_date: datetime = Field(..., description="End date for analytics")
    group_by: str = Field(default="day", description="Group by: day, week, month")

# Corporate Package Schemas
class CorporatePackageBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    contact_email: str = Field(..., description="Contact email")
    contact_name: str = Field(..., min_length=1, max_length=255, description="Contact person name")
    package_type: str = Field(..., min_length=1, max_length=50, description="Package type")
    number_of_seats: int = Field(..., gt=0, description="Number of seats")
    base_price: float = Field(..., gt=0, description="Base price")
    discount_percentage: float = Field(default=0.0, ge=0, le=100, description="Discount percentage")
    final_price: float = Field(..., gt=0, description="Final price")
    custom_curriculum: Optional[str] = Field(None, description="Custom curriculum JSON")
    start_date: Optional[datetime] = Field(None, description="Contract start date")
    end_date: Optional[datetime] = Field(None, description="Contract end date")
    contract_details: Optional[str] = Field(None, description="Contract details")

class CorporatePackageCreate(CorporatePackageBase):
    pass

class CorporatePackage(CorporatePackageBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Certification Schemas
class CertificationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Certification name")
    description: Optional[str] = Field(None, description="Certification description")
    requirements: Optional[str] = Field(None, description="Requirements JSON")
    price: float = Field(..., gt=0, description="Certification price")
    currency: str = Field(default="USD", description="Currency code")
    validity_period_months: int = Field(default=24, gt=0, description="Validity period in months")
    badge_image_url: Optional[str] = Field(None, description="Badge image URL")
    certificate_template_url: Optional[str] = Field(None, description="Certificate template URL")
    is_active: bool = Field(default=True, description="Whether certification is active")

class CertificationCreate(CertificationBase):
    pass

class Certification(CertificationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserCertificationBase(BaseModel):
    certification_id: int = Field(..., description="Certification ID")
    score: Optional[float] = Field(None, ge=0, le=100, description="Certification score")

class UserCertificationCreate(UserCertificationBase):
    pass

class UserCertification(UserCertificationBase):
    id: int
    user_id: int
    status: str
    submitted_at: datetime
    approved_at: Optional[datetime]
    expires_at: Optional[datetime]
    certificate_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Pricing Calculator Schemas
class PricingCalculationRequest(BaseModel):
    course_id: int = Field(..., description="Course ID")
    tier: CourseTier = Field(..., description="Course tier")
    quantity: int = Field(default=1, gt=0, description="Number of seats/courses")
    is_corporate: bool = Field(default=False, description="Is this a corporate purchase")
    corporate_size: Optional[int] = Field(None, ge=1, description="Corporate size for discount")
    promo_code: Optional[str] = Field(None, description="Promotional code")
    early_bird: bool = Field(default=False, description="Apply early bird discount")

class PricingCalculationResponse(BaseModel):
    base_price: float
    discount_amount: float
    discount_percentage: float
    final_price: float
    currency: str = "USD"
    features_included: List[str]
    savings_amount: float

# Payment Processing Schemas
class StripePaymentIntentCreate(BaseModel):
    course_pricing_id: int = Field(..., description="Course pricing ID")
    quantity: int = Field(default=1, gt=0, description="Quantity to purchase")
    promo_code: Optional[str] = Field(None, description="Promotional code")
    billing_address: Optional[Dict[str, Any]] = Field(None, description="Billing address")

class StripePaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str

# Revenue Dashboard Schemas
class RevenueDashboard(BaseModel):
    total_revenue: float
    monthly_recurring_revenue: float
    average_order_value: float
    conversion_rate: float
    churn_rate: float
    customer_lifetime_value: float
    new_customers_this_month: int
    active_subscriptions: int
    refund_rate: float
    top_performing_courses: List[Dict[str, Any]]
    revenue_by_tier: Dict[str, float]

class CourseRevenueAnalytics(BaseModel):
    course_id: int
    course_title: str
    total_revenue: float
    enrollments_count: int
    completion_rate: float
    average_rating: float
    refund_rate: float
    revenue_trend: List[Dict[str, Any]]  # Daily/weekly/monthly revenue data