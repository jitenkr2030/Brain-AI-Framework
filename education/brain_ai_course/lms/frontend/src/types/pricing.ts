"""
Frontend TypeScript types for Brain AI LMS Pricing and Revenue Features
Phase 3: Revenue Optimization
"""

export interface CourseTier {
  id: number;
  course_id: number;
  tier: 'foundation' | 'implementation' | 'mastery' | 'corporate';
  price: number;
  currency: string;
  duration_hours: number;
  description?: string;
  features?: string; // JSON string
  max_students: number;
  early_bird_discount: number;
  corporate_discount: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Payment {
  id: number;
  user_id: number;
  course_pricing_id: number;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded' | 'cancelled';
  stripe_payment_intent_id?: string;
  stripe_customer_id?: string;
  discount_applied: number;
  final_amount: number;
  payment_method?: string;
  billing_address?: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
}

export interface RefundRequest {
  id: number;
  payment_id: number;
  user_id: number;
  amount: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  admin_notes?: string;
  processed_at?: string;
  created_at: string;
}

export interface Subscription {
  id: number;
  user_id: number;
  stripe_subscription_id: string;
  plan_name: string;
  amount: number;
  currency: string;
  status: 'active' | 'cancelled' | 'expired' | 'past_due';
  current_period_start?: string;
  current_period_end?: string;
  cancel_at_period_end: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CorporatePackage {
  id: number;
  company_name: string;
  contact_email: string;
  contact_name: string;
  package_type: 'custom' | 'premium' | 'enterprise';
  number_of_seats: number;
  base_price: number;
  discount_percentage: number;
  final_price: number;
  custom_curriculum?: string; // JSON string
  start_date?: string;
  end_date?: string;
  status: 'pending' | 'approved' | 'rejected' | 'active' | 'expired';
  contract_details?: string;
  created_at: string;
  updated_at?: string;
}

export interface Certification {
  id: number;
  name: string;
  description?: string;
  requirements?: string; // JSON string
  price: number;
  currency: string;
  validity_period_months: number;
  badge_image_url?: string;
  certificate_template_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserCertification {
  id: number;
  user_id: number;
  certification_id: number;
  status: 'pending' | 'approved' | 'rejected';
  score?: number;
  submitted_at: string;
  approved_at?: string;
  expires_at?: string;
  certificate_url?: string;
  created_at: string;
}

export interface PricingCalculationRequest {
  course_id: number;
  tier: CourseTier['tier'];
  quantity: number;
  is_corporate: boolean;
  corporate_size?: number;
  promo_code?: string;
  early_bird: boolean;
}

export interface PricingCalculationResponse {
  base_price: number;
  discount_amount: number;
  discount_percentage: number;
  final_price: number;
  currency: string;
  features_included: string[];
  savings_amount: number;
}

export interface StripePaymentIntentRequest {
  course_pricing_id: number;
  quantity: number;
  promo_code?: string;
  billing_address?: Record<string, any>;
}

export interface StripePaymentIntentResponse {
  client_secret: string;
  payment_intent_id: string;
  amount: number;
  currency: string;
}

export interface RevenueDashboard {
  total_revenue: number;
  monthly_recurring_revenue: number;
  average_order_value: number;
  conversion_rate: number;
  churn_rate: number;
  customer_lifetime_value: number;
  new_customers_this_month: number;
  active_subscriptions: number;
  refund_rate: number;
  top_performing_courses: Array<{
    course_id: number;
    title: string;
    revenue: number;
  }>;
  revenue_by_tier: Record<string, number>;
}

export interface CourseRevenueAnalytics {
  course_id: number;
  course_title: string;
  total_revenue: number;
  enrollments_count: number;
  completion_rate: number;
  average_rating: number;
  refund_rate: number;
  revenue_trend: Array<{
    date: string;
    revenue: number;
  }>;
}

export interface RevenueMetrics {
  totalRevenue: number;
  monthlyRecurringRevenue: number;
  averageOrderValue: number;
  conversionRate: number;
  churnRate: number;
  customerLifetimeValue: number;
  newCustomers: number;
  activeSubscriptions: number;
  refundRate: number;
}

export interface CourseTierOption {
  id: number;
  tier: CourseTier['tier'];
  name: string;
  price: number;
  originalPrice: number;
  duration: string;
  features: string[];
  savings?: number;
  savingsPercentage?: number;
  isPopular?: boolean;
  isEarlyBird?: boolean;
  maxStudents: number;
}

export interface PaymentMethod {
  id: string;
  type: 'card' | 'bank_account' | 'digital_wallet';
  last4?: string;
  brand?: string;
  expiryMonth?: number;
  expiryYear?: number;
  isDefault: boolean;
}

export interface Invoice {
  id: number;
  payment_id: number;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'overdue' | 'cancelled';
  due_date: string;
  paid_date?: string;
  invoice_url?: string;
  created_at: string;
}

export interface PromoCode {
  code: string;
  type: 'percentage' | 'fixed_amount';
  value: number;
  valid_from: string;
  valid_until: string;
  usage_limit?: number;
  used_count: number;
  min_purchase_amount?: number;
  applicable_tiers?: CourseTier['tier'][];
  is_active: boolean;
}

export interface RevenueAlert {
  id: number;
  type: 'low_revenue' | 'high_churn' | 'payment_failed' | 'refund_request';
  severity: 'low' | 'medium' | 'high';
  message: string;
  amount?: number;
  threshold?: number;
  is_read: boolean;
  created_at: string;
}

export interface PricingFormData {
  courseId: number;
  tier: CourseTier['tier'];
  quantity: number;
  isCorporate: boolean;
  corporateSize?: number;
  promoCode?: string;
  earlyBird: boolean;
  billingAddress?: {
    line1: string;
    line2?: string;
    city: string;
    state: string;
    postal_code: string;
    country: string;
  };
}

export interface CheckoutSession {
  id: string;
  url: string;
  expires_at: string;
  amount_total: number;
  currency: string;
  customer_email?: string;
  metadata?: Record<string, string>;
}

export interface RevenueReport {
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  start_date: string;
  end_date: string;
  total_revenue: number;
  total_orders: number;
  average_order_value: number;
  refunds_total: number;
  refunds_count: number;
  net_revenue: number;
  growth_rate: number;
  top_courses: Array<{
    course_id: number;
    title: string;
    revenue: number;
    orders: number;
  }>;
  revenue_by_tier: Record<string, number>;
  daily_breakdown: Array<{
    date: string;
    revenue: number;
    orders: number;
  }>;
}