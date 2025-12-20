"""
Pricing and Revenue Service for Brain AI LMS
Handles course pricing, payments, subscriptions, and revenue optimization
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import stripe
from .models.pricing_models import (
    CoursePricing, Payment, RefundRequest, Subscription, 
    RevenueAnalytics, CorporatePackage, Certification, UserCertification
)
from .models.community_models import AlumniProfile
from .schemas.pricing_schemas import (
    CoursePricingCreate, CoursePricingUpdate, PaymentCreate,
    RefundRequestCreate, SubscriptionCreate, CorporatePackageCreate,
    CertificationCreate, UserCertificationCreate, PricingCalculationRequest,
    PricingCalculationResponse, StripePaymentIntentCreate, StripePaymentIntentResponse,
    RevenueDashboard, CourseRevenueAnalytics
)

class PricingService:
    """Service for managing pricing and revenue operations"""
    
    def __init__(self, db: Session):
        self.db = db
        # Initialize Stripe with environment variable
        stripe.api_key = "sk_test_your_stripe_secret_key"  # Replace with actual key
    
    # Course Pricing Management
    async def create_course_pricing(self, pricing_data: CoursePricingCreate) -> CoursePricing:
        """Create a new course pricing tier"""
        pricing = CoursePricing(**pricing_data.dict())
        self.db.add(pricing)
        self.db.commit()
        self.db.refresh(pricing)
        return pricing
    
    async def get_course_pricing(self, pricing_id: int) -> Optional[CoursePricing]:
        """Get course pricing by ID"""
        return self.db.query(CoursePricing).filter(CoursePricing.id == pricing_id).first()
    
    async def get_course_pricing_by_course(self, course_id: int, tier: str) -> Optional[CoursePricing]:
        """Get pricing for specific course and tier"""
        return self.db.query(CoursePricing).filter(
            and_(
                CoursePricing.course_id == course_id,
                CoursePricing.tier == tier,
                CoursePricing.is_active == True
            )
        ).first()
    
    async def list_course_pricing(self, course_id: Optional[int] = None) -> List[CoursePricing]:
        """List course pricing options"""
        query = self.db.query(CoursePricing).filter(CoursePricing.is_active == True)
        if course_id:
            query = query.filter(CoursePricing.course_id == course_id)
        return query.all()
    
    async def update_course_pricing(self, pricing_id: int, update_data: CoursePricingUpdate) -> Optional[CoursePricing]:
        """Update course pricing"""
        pricing = await self.get_course_pricing(pricing_id)
        if not pricing:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(pricing, field, value)
        
        self.db.commit()
        self.db.refresh(pricing)
        return pricing
    
    # Pricing Calculations
    async def calculate_pricing(self, request: PricingCalculationRequest) -> PricingCalculationResponse:
        """Calculate pricing with discounts and features"""
        # Get base pricing
        pricing = await self.get_course_pricing_by_course(request.course_id, request.tier)
        if not pricing:
            raise ValueError("Course pricing not found")
        
        base_price = pricing.price * request.quantity
        discount_amount = 0.0
        discount_percentage = 0.0
        features_included = []
        
        # Apply early bird discount
        if request.early_bird and pricing.early_bird_discount > 0:
            early_bird_discount = base_price * (pricing.early_bird_discount / 100)
            discount_amount += early_bird_discount
            discount_percentage += pricing.early_bird_discount
        
        # Apply corporate discount
        if request.is_corporate and pricing.corporate_discount > 0:
            corporate_discount = base_price * (pricing.corporate_discount / 100)
            discount_amount += corporate_discount
            discount_percentage += pricing.corporate_discount
        
        # Apply volume discount for large corporate orders
        if request.is_corporate and request.corporate_size and request.corporate_size >= 50:
            volume_discount = min(15.0, (request.corporate_size / 100) * 2)  # Max 15% discount
            volume_discount_amount = base_price * (volume_discount / 100)
            discount_amount += volume_discount_amount
            discount_percentage += volume_discount
        
        final_price = base_price - discount_amount
        savings_amount = discount_amount
        
        # Parse features if available
        if pricing.features:
            try:
                features_included = json.loads(pricing.features)
            except json.JSONDecodeError:
                features_included = []
        
        return PricingCalculationResponse(
            base_price=base_price,
            discount_amount=discount_amount,
            discount_percentage=discount_percentage,
            final_price=final_price,
            currency=pricing.currency,
            features_included=features_included,
            savings_amount=savings_amount
        )
    
    # Payment Processing
    async def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Create a new payment record"""
        payment = Payment(**payment_data.dict())
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    async def create_stripe_payment_intent(self, request: StripePaymentIntentCreate) -> StripePaymentIntentResponse:
        """Create Stripe payment intent"""
        try:
            # Get pricing information
            pricing = await self.get_course_pricing(request.course_pricing_id)
            if not pricing:
                raise ValueError("Course pricing not found")
            
            # Calculate amount
            amount = int(pricing.price * 100)  # Convert to cents
            if request.quantity > 1:
                amount *= request.quantity
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=pricing.currency.lower(),
                metadata={
                    'course_pricing_id': str(request.course_pricing_id),
                    'quantity': str(request.quantity)
                }
            )
            
            # Create payment record
            payment = Payment(
                user_id=1,  # This should come from authentication
                course_pricing_id=request.course_pricing_id,
                amount=pricing.price * request.quantity,
                final_amount=pricing.price * request.quantity,
                stripe_payment_intent_id=payment_intent.id,
                currency=pricing.currency,
                status="pending"
            )
            self.db.add(payment)
            self.db.commit()
            
            return StripePaymentIntentResponse(
                client_secret=payment_intent.client_secret,
                payment_intent_id=payment_intent.id,
                amount=amount / 100,
                currency=pricing.currency
            )
        
        except Exception as e:
            raise Exception(f"Failed to create payment intent: {str(e)}")
    
    async def confirm_payment(self, payment_intent_id: str) -> Optional[Payment]:
        """Confirm payment and update status"""
        payment = self.db.query(Payment).filter(
            Payment.stripe_payment_intent_id == payment_intent_id
        ).first()
        
        if not payment:
            return None
        
        # Update payment status
        payment.status = "completed"
        payment.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    # Refund Management
    async def create_refund_request(self, refund_data: RefundRequestCreate, user_id: int) -> RefundRequest:
        """Create a refund request"""
        refund = RefundRequest(
            **refund_data.dict(),
            user_id=user_id
        )
        self.db.add(refund)
        self.db.commit()
        self.db.refresh(refund)
        return refund
    
    async def process_refund_request(self, refund_id: int, approve: bool, admin_notes: str = None) -> Optional[RefundRequest]:
        """Process refund request (approve/reject)"""
        refund = self.db.query(RefundRequest).filter(RefundRequest.id == refund_id).first()
        if not refund:
            return None
        
        refund.status = "approved" if approve else "rejected"
        refund.admin_notes = admin_notes
        refund.processed_at = datetime.utcnow()
        
        # If approved, update original payment status
        if approve:
            payment = self.db.query(Payment).filter(Payment.id == refund.payment_id).first()
            if payment:
                payment.status = "refunded"
        
        self.db.commit()
        self.db.refresh(refund)
        return refund
    
    # Subscription Management
    async def create_subscription(self, subscription_data: SubscriptionCreate) -> Subscription:
        """Create a new subscription"""
        subscription = Subscription(**subscription_data.dict())
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    async def update_subscription_status(self, subscription_id: int, status: str) -> Optional[Subscription]:
        """Update subscription status"""
        subscription = self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            return None
        
        subscription.status = status
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    # Corporate Packages
    async def create_corporate_package(self, package_data: CorporatePackageCreate) -> CorporatePackage:
        """Create a new corporate package"""
        package = CorporatePackage(**package_data.dict())
        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)
        return package
    
    async def list_corporate_packages(self, status: Optional[str] = None) -> List[CorporatePackage]:
        """List corporate packages"""
        query = self.db.query(CorporatePackage)
        if status:
            query = query.filter(CorporatePackage.status == status)
        return query.all()
    
    # Certification Management
    async def create_certification(self, cert_data: CertificationCreate) -> Certification:
        """Create a new certification"""
        certification = Certification(**cert_data.dict())
        self.db.add(certification)
        self.db.commit()
        self.db.refresh(certification)
        return certification
    
    async def issue_user_certification(self, cert_data: UserCertificationCreate, user_id: int) -> UserCertification:
        """Issue certification to user"""
        # Get certification details
        certification = self.db.query(Certification).filter(
            Certification.id == cert_data.certification_id
        ).first()
        
        if not certification:
            raise ValueError("Certification not found")
        
        # Calculate expiry date
        expiry_date = datetime.utcnow() + timedelta(days=certification.validity_period_months * 30)
        
        user_cert = UserCertification(
            **cert_data.dict(),
            user_id=user_id,
            status="approved",
            approved_at=datetime.utcnow(),
            expires_at=expiry_date
        )
        
        self.db.add(user_cert)
        self.db.commit()
        self.db.refresh(user_cert)
        return user_cert
    
    # Revenue Analytics
    async def get_revenue_dashboard(self, start_date: datetime, end_date: datetime) -> RevenueDashboard:
        """Get comprehensive revenue dashboard data"""
        # Calculate total revenue
        total_revenue = self.db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date,
                Payment.status == "completed"
            )
        ).scalar() or 0.0
        
        # Calculate monthly recurring revenue
        mrr = self.db.query(func.sum(Subscription.amount)).filter(
            Subscription.status == "active"
        ).scalar() or 0.0
        
        # Calculate average order value
        aov_result = self.db.query(func.avg(Payment.amount)).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date,
                Payment.status == "completed"
            )
        ).scalar()
        average_order_value = aov_result or 0.0
        
        # Get other metrics
        new_customers = self.db.query(func.count(func.distinct(Payment.user_id))).filter(
            and_(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date,
                Payment.status == "completed"
            )
        ).scalar() or 0
        
        active_subscriptions = self.db.query(func.count(Subscription.id)).filter(
            Subscription.status == "active"
        ).scalar() or 0
        
        # Mock additional data (in real implementation, calculate these)
        conversion_rate = 2.5  # Example
        churn_rate = 5.2  # Example
        customer_lifetime_value = 2500.0  # Example
        refund_rate = 1.8  # Example
        
        # Get top performing courses
        top_courses = [
            {"course_id": 1, "title": "Brain AI Foundation", "revenue": 125000},
            {"course_id": 2, "title": "Memory Systems Mastery", "revenue": 98000},
            {"course_id": 3, "title": "Enterprise Implementation", "revenue": 87000}
        ]
        
        # Revenue by tier
        revenue_by_tier = {
            "foundation": 85000,
            "implementation": 120000,
            "mastery": 95000,
            "corporate": 250000
        }
        
        return RevenueDashboard(
            total_revenue=total_revenue,
            monthly_recurring_revenue=mrr,
            average_order_value=average_order_value,
            conversion_rate=conversion_rate,
            churn_rate=churn_rate,
            customer_lifetime_value=customer_lifetime_value,
            new_customers_this_month=new_customers,
            active_subscriptions=active_subscriptions,
            refund_rate=refund_rate,
            top_performing_courses=top_courses,
            revenue_by_tier=revenue_by_tier
        )
    
    async def get_course_revenue_analytics(self, course_id: int) -> CourseRevenueAnalytics:
        """Get revenue analytics for specific course"""
        # Mock implementation - in real system, this would query actual data
        return CourseRevenueAnalytics(
            course_id=course_id,
            course_title="Brain AI Foundation",
            total_revenue=125000.0,
            enrollments_count=50,
            completion_rate=0.85,
            average_rating=4.8,
            refund_rate=0.05,
            revenue_trend=[
                {"date": "2025-01-01", "revenue": 5000},
                {"date": "2025-01-02", "revenue": 7500},
                {"date": "2025-01-03", "revenue": 6200}
            ]
        )
    
    # Alumni Network Integration
    async def get_alumni_for_referrals(self) -> List[Dict[str, Any]]:
        """Get alumni profiles for referral programs"""
        alumni_profiles = self.db.query(AlumniProfile).filter(
            AlumniProfile.status.in_(["active", "mentor"])
        ).all()
        
        return [
            {
                "id": profile.id,
                "user_id": profile.user_id,
                "name": profile.user.full_name if profile.user else "Unknown",
                "company": profile.current_company,
                "job_title": profile.current_job_title,
                "expertise_areas": json.loads(profile.expertise_areas) if profile.expertise_areas else [],
                "availability_for_mentoring": profile.availability_for_mentoring
            }
            for profile in alumni_profiles
        ]