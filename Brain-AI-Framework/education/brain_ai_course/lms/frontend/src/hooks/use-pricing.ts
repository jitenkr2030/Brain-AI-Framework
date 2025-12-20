"""
Frontend React hooks for Brain AI LMS Pricing and Revenue Features
Phase 3: Revenue Optimization
"""

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  CourseTier,
  Payment,
  Subscription,
  CorporatePackage,
  Certification,
  UserCertification,
  PricingCalculationRequest,
  PricingCalculationResponse,
  StripePaymentIntentRequest,
  StripePaymentIntentResponse,
  RevenueDashboard,
  CourseRevenueAnalytics,
  PricingFormData,
  CheckoutSession,
  RevenueReport
} from '@/types/pricing';

// Base API configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Pricing Hook
export function usePricing() {
  const [coursePricing, setCoursePricing] = useState<CourseTier[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCoursePricing = useCallback(async (courseId?: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const url = courseId 
        ? `${API_BASE}/pricing/course-pricing?course_id=${courseId}`
        : `${API_BASE}/pricing/course-pricing`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch pricing');
      
      const data = await response.json();
      setCoursePricing(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createCoursePricing = useCallback(async (pricingData: Partial<CourseTier>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/course-pricing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pricingData),
      });
      
      if (!response.ok) throw new Error('Failed to create pricing');
      
      const data = await response.json();
      setCoursePricing(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateCoursePricing = useCallback(async (pricingId: number, updateData: Partial<CourseTier>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/course-pricing/${pricingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData),
      });
      
      if (!response.ok) throw new Error('Failed to update pricing');
      
      const data = await response.json();
      setCoursePricing(prev => prev.map(p => p.id === pricingId ? data : p));
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    coursePricing,
    isLoading,
    error,
    fetchCoursePricing,
    createCoursePricing,
    updateCoursePricing,
  };
}

// Pricing Calculator Hook
export function usePricingCalculator() {
  const [calculation, setCalculation] = useState<PricingCalculationResponse | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculatePrice = useCallback(async (request: PricingCalculationRequest) => {
    setIsCalculating(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) throw new Error('Failed to calculate price');
      
      const data = await response.json();
      setCalculation(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsCalculating(false);
    }
  }, []);

  const clearCalculation = useCallback(() => {
    setCalculation(null);
    setError(null);
  }, []);

  return {
    calculation,
    isCalculating,
    error,
    calculatePrice,
    clearCalculation,
  };
}

// Payment Processing Hook
export function usePayments() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPayments = useCallback(async (userId?: number, status?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId.toString());
      if (status) params.append('status', status);
      
      const response = await fetch(`${API_BASE}/pricing/payments?${params}`);
      if (!response.ok) throw new Error('Failed to fetch payments');
      
      const data = await response.json();
      setPayments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createPaymentIntent = useCallback(async (request: StripePaymentIntentRequest): Promise<StripePaymentIntentResponse> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/payments/stripe-intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      
      if (!response.ok) throw new Error('Failed to create payment intent');
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const confirmPayment = useCallback(async (paymentIntentId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/payments/confirm/${paymentIntentId}`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to confirm payment');
      
      const data = await response.json();
      // Refresh payments list
      await fetchPayments();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [fetchPayments]);

  return {
    payments,
    isLoading,
    error,
    fetchPayments,
    createPaymentIntent,
    confirmPayment,
  };
}

// Subscription Management Hook
export function useSubscriptions() {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscriptions = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/subscriptions?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch subscriptions');
      
      const data = await response.json();
      setSubscriptions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createSubscription = useCallback(async (subscriptionData: Partial<Subscription>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/subscriptions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscriptionData),
      });
      
      if (!response.ok) throw new Error('Failed to create subscription');
      
      const data = await response.json();
      setSubscriptions(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateSubscriptionStatus = useCallback(async (subscriptionId: number, status: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/subscriptions/${subscriptionId}/status?status=${status}`, {
        method: 'PUT',
      });
      
      if (!response.ok) throw new Error('Failed to update subscription');
      
      const data = await response.json();
      setSubscriptions(prev => prev.map(s => s.id === subscriptionId ? { ...s, status } : s));
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    subscriptions,
    isLoading,
    error,
    fetchSubscriptions,
    createSubscription,
    updateSubscriptionStatus,
  };
}

// Corporate Packages Hook
export function useCorporatePackages() {
  const [packages, setPackages] = useState<CorporatePackage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPackages = useCallback(async (status?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = status ? `?status=${status}` : '';
      const response = await fetch(`${API_BASE}/pricing/corporate-packages${params}`);
      if (!response.ok) throw new Error('Failed to fetch corporate packages');
      
      const data = await response.json();
      setPackages(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createPackage = useCallback(async (packageData: Partial<CorporatePackage>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/corporate-packages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(packageData),
      });
      
      if (!response.ok) throw new Error('Failed to create corporate package');
      
      const data = await response.json();
      setPackages(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    packages,
    isLoading,
    error,
    fetchPackages,
    createPackage,
  };
}

// Certifications Hook
export function useCertifications() {
  const [certifications, setCertifications] = useState<Certification[]>([]);
  const [userCertifications, setUserCertifications] = useState<UserCertification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCertifications = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/certifications`);
      if (!response.ok) throw new Error('Failed to fetch certifications');
      
      const data = await response.json();
      setCertifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchUserCertifications = useCallback(async (userId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/certifications/user/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch user certifications');
      
      const data = await response.json();
      setUserCertifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const issueCertification = useCallback(async (certData: Partial<UserCertification>) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/certifications/issue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(certData),
      });
      
      if (!response.ok) throw new Error('Failed to issue certification');
      
      const data = await response.json();
      setUserCertifications(prev => [...prev, data]);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    certifications,
    userCertifications,
    isLoading,
    error,
    fetchCertifications,
    fetchUserCertifications,
    issueCertification,
  };
}

// Revenue Analytics Hook
export function useRevenueAnalytics() {
  const [dashboard, setDashboard] = useState<RevenueDashboard | null>(null);
  const [courseAnalytics, setCourseAnalytics] = useState<CourseRevenueAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async (startDate: string, endDate: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      });
      
      const response = await fetch(`${API_BASE}/pricing/analytics/dashboard?${params}`);
      if (!response.ok) throw new Error('Failed to fetch revenue dashboard');
      
      const data = await response.json();
      setDashboard(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchCourseAnalytics = useCallback(async (courseId: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/analytics/course/${courseId}`);
      if (!response.ok) throw new Error('Failed to fetch course analytics');
      
      const data = await response.json();
      setCourseAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getRevenueReport = useCallback(async (
    startDate: string,
    endDate: string,
    period: 'daily' | 'weekly' | 'monthly' | 'yearly' = 'monthly'
  ): Promise<RevenueReport> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        period,
      });
      
      const response = await fetch(`${API_BASE}/pricing/analytics/report?${params}`);
      if (!response.ok) throw new Error('Failed to fetch revenue report');
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    dashboard,
    courseAnalytics,
    isLoading,
    error,
    fetchDashboard,
    fetchCourseAnalytics,
    getRevenueReport,
  };
}

// Checkout Process Hook
export function useCheckout() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [checkoutSession, setCheckoutSession] = useState<CheckoutSession | null>(null);

  const processCheckout = useCallback(async (formData: PricingFormData) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      // Step 1: Calculate pricing
      const pricingRequest: PricingCalculationRequest = {
        course_id: formData.courseId,
        tier: formData.tier,
        quantity: formData.quantity,
        is_corporate: formData.isCorporate,
        corporate_size: formData.corporateSize,
        promo_code: formData.promoCode,
        early_bird: formData.earlyBird,
      };

      const pricing = await fetch(`${API_BASE}/pricing/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pricingRequest),
      }).then(res => res.json());

      // Step 2: Create payment intent
      const paymentRequest: StripePaymentIntentRequest = {
        course_pricing_id: formData.courseId, // This should be the pricing tier ID
        quantity: formData.quantity,
        promo_code: formData.promoCode,
        billing_address: formData.billingAddress,
      };

      const paymentIntent = await fetch(`${API_BASE}/pricing/payments/stripe-intent`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paymentRequest),
      }).then(res => res.json());

      return {
        pricing,
        paymentIntent,
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Checkout failed');
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const createCheckoutSession = useCallback(async (sessionData: Partial<CheckoutSession>) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/pricing/checkout/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData),
      });
      
      if (!response.ok) throw new Error('Failed to create checkout session');
      
      const data = await response.json();
      setCheckoutSession(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create checkout session');
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const redirectToCheckout = useCallback((sessionId: string) => {
    // In a real implementation, this would redirect to Stripe's hosted checkout
    window.location.href = `${API_BASE}/pricing/checkout/session/${sessionId}`;
  }, []);

  return {
    isProcessing,
    error,
    checkoutSession,
    processCheckout,
    createCheckoutSession,
    redirectToCheckout,
  };
}