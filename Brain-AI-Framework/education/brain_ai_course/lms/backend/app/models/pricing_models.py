"""
Pricing and Revenue Models for Brain AI LMS
Handles course pricing, subscriptions, and revenue optimization
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class CourseTier(enum.Enum):
    FOUNDATION = "foundation"
    IMPLEMENTATION = "implementation" 
    MASTERY = "mastery"
    CORPORATE = "corporate"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"

class CoursePricing(Base):
    __tablename__ = "course_pricing"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    tier = Column(Enum(CourseTier), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    duration_hours = Column(Integer, nullable=False)
    description = Column(Text)
    features = Column(Text)  # JSON string of features
    max_students = Column(Integer, default=50)
    early_bird_discount = Column(Float, default=0.0)  # Percentage discount
    corporate_discount = Column(Float, default=0.0)   # Percentage discount
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    course = relationship("Course", back_populates="pricing")
    payments = relationship("Payment", back_populates="course_pricing")
    enrollments = relationship("Enrollment", back_populates="pricing")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_pricing_id = Column(Integer, ForeignKey("course_pricing.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    stripe_payment_intent_id = Column(String(255), unique=True)
    stripe_customer_id = Column(String(255))
    discount_applied = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    payment_method = Column(String(50))
    billing_address = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="payments")
    course_pricing = relationship("CoursePricing", back_populates="payments")
    refund_requests = relationship("RefundRequest", back_populates="payment")

class RefundRequest(Base):
    __tablename__ = "refund_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    admin_notes = Column(Text)
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    payment = relationship("Payment", back_populates="refund_requests")
    user = relationship("User")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True)
    plan_name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="subscriptions")

class RevenueAnalytics(Base):
    __tablename__ = "revenue_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    total_revenue = Column(Float, default=0.0)
    course_revenue = Column(Float, default=0.0)
    subscription_revenue = Column(Float, default=0.0)
    new_customers = Column(Integer, default=0)
    churned_customers = Column(Integer, default=0)
    average_order_value = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)  # Percentage
    refunds_processed = Column(Integer, default=0)
    refunds_amount = Column(Float, default=0.0)

class CorporatePackage(Base):
    __tablename__ = "corporate_packages"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    package_type = Column(String(50), nullable=False)  # "custom", "premium", "enterprise"
    number_of_seats = Column(Integer, nullable=False)
    base_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    final_price = Column(Float, nullable=False)
    custom_curriculum = Column(Text)  # JSON string
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    status = Column(String(20), default="pending")
    contract_details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(Text)  # JSON string of requirements
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    validity_period_months = Column(Integer, default=24)
    badge_image_url = Column(String(500))
    certificate_template_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    certifications = relationship("UserCertification", back_populates="certification")

class UserCertification(Base):
    __tablename__ = "user_certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    status = Column(String(20), default="pending")  # "pending", "approved", "rejected"
    score = Column(Float)
    submitted_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    certificate_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="certifications")
    certification = relationship("Certification", back_populates="certifications")