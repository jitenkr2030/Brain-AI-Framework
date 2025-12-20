"""
Pricing and Revenue API Router for Brain AI LMS
Handles course pricing, payments, subscriptions, and revenue optimization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..services.pricing_service import PricingService
from ..schemas.pricing_schemas import (
    CoursePricingCreate, CoursePricingUpdate, CoursePricing as CoursePricingSchema,
    PaymentCreate, Payment as PaymentSchema,
    RefundRequestCreate, RefundRequest as RefundRequestSchema,
    SubscriptionCreate, Subscription as SubscriptionSchema,
    CorporatePackageCreate, CorporatePackage as CorporatePackageSchema,
    CertificationCreate, Certification as CertificationSchema,
    UserCertificationCreate, UserCertification as UserCertificationSchema,
    PricingCalculationRequest, PricingCalculationResponse,
    StripePaymentIntentCreate, StripePaymentIntentResponse,
    RevenueDashboard, CourseRevenueAnalytics
)

router = APIRouter(prefix="/pricing", tags=["pricing"])
logger = logging.getLogger(__name__)

# Dependency to get pricing service
def get_pricing_service(db: Session = Depends(get_db)) -> PricingService:
    return PricingService(db)

# Course Pricing Endpoints
@router.post("/course-pricing", response_model=CoursePricingSchema, status_code=status.HTTP_201_CREATED)
async def create_course_pricing(
    pricing_data: CoursePricingCreate,
    service: PricingService = Depends(get_pricing_service)
):
    """Create a new course pricing tier"""
    try:
        return await service.create_course_pricing(pricing_data)
    except Exception as e:
        logger.error(f"Error creating course pricing: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/course-pricing/{pricing_id}", response_model=CoursePricingSchema)
async def get_course_pricing(
    pricing_id: int,
    service: PricingService = Depends(get_pricing_service)
):
    """Get course pricing by ID"""
    pricing = await service.get_course_pricing(pricing_id)
    if not pricing:
        raise HTTPException(status_code=404, detail="Course pricing not found")
    return pricing

@router.get("/course-pricing", response_model=List[CoursePricingSchema])
async def list_course_pricing(
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    service: PricingService = Depends(get_pricing_service)
):
    """List course pricing options"""
    return await service.list_course_pricing(course_id)

@router.put("/course-pricing/{pricing_id}", response_model=CoursePricingSchema)
async def update_course_pricing(
    pricing_id: int,
    update_data: CoursePricingUpdate,
    service: PricingService = Depends(get_pricing_service)
):
    """Update course pricing"""
    pricing = await service.update_course_pricing(pricing_id, update_data)
    if not pricing:
        raise HTTPException(status_code=404, detail="Course pricing not found")
    return pricing

# Pricing Calculation Endpoints
@router.post("/calculate", response_model=PricingCalculationResponse)
async def calculate_pricing(
    request: PricingCalculationRequest,
    service: PricingService = Depends(get_pricing_service)
):
    """Calculate pricing with discounts"""
    try:
        return await service.calculate_pricing(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating pricing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Payment Processing Endpoints
@router.post("/payments/stripe-intent", response_model=StripePaymentIntentResponse)
async def create_stripe_payment_intent(
    request: StripePaymentIntentCreate,
    service: PricingService = Depends(get_pricing_service)
):
    """Create Stripe payment intent"""
    try:
        return await service.create_stripe_payment_intent(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

@router.post("/payments/confirm/{payment_intent_id}", response_model=PaymentSchema)
async def confirm_payment(
    payment_intent_id: str,
    service: PricingService = Depends(get_pricing_service)
):
    """Confirm payment completion"""
    payment = await service.confirm_payment(payment_intent_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/payments", response_model=List[PaymentSchema])
async def list_payments(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    limit: int = Query(50, ge=1, le=100, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """List payments with filters"""
    from ..models.pricing_models import Payment
    query = db.query(Payment)
    
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    if status:
        query = query.filter(Payment.status == status)
    
    return query.offset(offset).limit(limit).all()

# Refund Management Endpoints
@router.post("/refunds", response_model=RefundRequestSchema, status_code=status.HTTP_201_CREATED)
async def create_refund_request(
    refund_data: RefundRequestCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: PricingService = Depends(get_pricing_service)
):
    """Create refund request"""
    try:
        return await service.create_refund_request(refund_data, current_user_id)
    except Exception as e:
        logger.error(f"Error creating refund request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refunds/{refund_id}/process")
async def process_refund_request(
    refund_id: int,
    approve: bool = Query(..., description="Approve or reject refund"),
    admin_notes: Optional[str] = Query(None, description="Admin notes"),
    service: PricingService = Depends(get_pricing_service)
):
    """Process refund request (admin only)"""
    refund = await service.process_refund_request(refund_id, approve, admin_notes)
    if not refund:
        raise HTTPException(status_code=404, detail="Refund request not found")
    return {"message": "Refund request processed successfully", "status": refund.status}

# Subscription Management Endpoints
@router.post("/subscriptions", response_model=SubscriptionSchema, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    service: PricingService = Depends(get_pricing_service)
):
    """Create subscription"""
    try:
        return await service.create_subscription(subscription_data)
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/subscriptions/{subscription_id}/status")
async def update_subscription_status(
    subscription_id: int,
    status: str = Query(..., description="New subscription status"),
    service: PricingService = Depends(get_pricing_service)
):
    """Update subscription status"""
    subscription = await service.update_subscription_status(subscription_id, status)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription status updated successfully", "status": subscription.status}

# Corporate Packages Endpoints
@router.post("/corporate-packages", response_model=CorporatePackageSchema, status_code=status.HTTP_201_CREATED)
async def create_corporate_package(
    package_data: CorporatePackageCreate,
    service: PricingService = Depends(get_pricing_service)
):
    """Create corporate package"""
    try:
        return await service.create_corporate_package(package_data)
    except Exception as e:
        logger.error(f"Error creating corporate package: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/corporate-packages", response_model=List[CorporatePackageSchema])
async def list_corporate_packages(
    status: Optional[str] = Query(None, description="Filter by status"),
    service: PricingService = Depends(get_pricing_service)
):
    """List corporate packages"""
    return await service.list_corporate_packages(status)

# Certification Management Endpoints
@router.post("/certifications", response_model=CertificationSchema, status_code=status.HTTP_201_CREATED)
async def create_certification(
    cert_data: CertificationCreate,
    service: PricingService = Depends(get_pricing_service)
):
    """Create certification"""
    try:
        return await service.create_certification(cert_data)
    except Exception as e:
        logger.error(f"Error creating certification: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/certifications/issue", response_model=UserCertificationSchema, status_code=status.HTTP_201_CREATED)
async def issue_user_certification(
    cert_data: UserCertificationCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: PricingService = Depends(get_pricing_service)
):
    """Issue certification to user"""
    try:
        return await service.issue_user_certification(cert_data, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error issuing certification: {str(e)}")
        raise HTTPException(status_code=500, detail="Certification issuance failed")

@router.get("/certifications/user/{user_id}", response_model=List[UserCertificationSchema])
async def list_user_certifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    """List user certifications"""
    from ..models.pricing_models import UserCertification
    return db.query(UserCertification).filter(UserCertification.user_id == user_id).all()

# Revenue Analytics Endpoints
@router.get("/analytics/dashboard", response_model=RevenueDashboard)
async def get_revenue_dashboard(
    start_date: datetime = Query(..., description="Start date for analytics"),
    end_date: datetime = Query(..., description="End date for analytics"),
    service: PricingService = Depends(get_pricing_service)
):
    """Get revenue dashboard"""
    try:
        return await service.get_revenue_dashboard(start_date, end_date)
    except Exception as e:
        logger.error(f"Error getting revenue dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve revenue data")

@router.get("/analytics/course/{course_id}", response_model=CourseRevenueAnalytics)
async def get_course_revenue_analytics(
    course_id: int,
    service: PricingService = Depends(get_pricing_service)
):
    """Get revenue analytics for specific course"""
    try:
        return await service.get_course_revenue_analytics(course_id)
    except Exception as e:
        logger.error(f"Error getting course analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve course analytics")

# Alumni Integration Endpoints
@router.get("/alumni/referrals")
async def get_alumni_for_referrals(
    service: PricingService = Depends(get_pricing_service)
):
    """Get alumni profiles for referral programs"""
    try:
        return await service.get_alumni_for_referrals()
    except Exception as e:
        logger.error(f"Error getting alumni referrals: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alumni data")

# Health Check Endpoint
@router.get("/health")
async def pricing_health_check():
    """Health check for pricing service"""
    return {
        "status": "healthy",
        "service": "pricing",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "course_pricing",
            "payment_processing",
            "subscription_management",
            "corporate_packages",
            "certifications",
            "revenue_analytics",
            "refund_management"
        ]
    }