/**
 * Unit Tests for use-pricing.ts
 * Brain AI LMS - Pricing Hook Tests
 */

import { renderHook, waitFor } from '@testing-library/react';
import { usePricing, usePricingCalculator, usePayments, useSubscriptions, useCorporatePackages, useCertifications, useRevenueAnalytics, useCheckout } from '../use-pricing';

// Mock fetch globally
global.fetch = jest.fn();

describe('usePricing', () => {
  const mockPricingTiers = [
    { id: 1, name: 'Basic', price: 29.99, features: ['Access to 3 courses'] },
    { id: 2, name: 'Pro', price: 59.99, features: ['Access to all courses', 'Certificate'] },
    { id: 3, name: 'Enterprise', price: 199.99, features: ['All features', 'Priority support'] },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockPricingTiers,
    });
  });

  it('should initialize with empty pricing data', () => {
    const { result } = renderHook(() => usePricing());

    expect(result.current.coursePricing).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should fetch pricing on demand', async () => {
    const { result } = renderHook(() => usePricing());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.coursePricing).toEqual(mockPricingTiers);
    expect(result.current.error).toBeNull();
  });

  it('should fetch pricing for specific course', async () => {
    const { result } = renderHook(() => usePricing());

    result.current.fetchCoursePricing(123);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('course_id=123'),
        expect.any(Object)
      );
    });
  });

  it('should create new pricing tier', async () => {
    const newPricing = { name: 'Premium', price: 99.99, features: ['All courses', 'Mentor support'] };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 4, ...newPricing }),
    });

    const { result } = renderHook(() => usePricing());
    await result.current.fetchCoursePricing();

    const created = await result.current.createCoursePricing(newPricing);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/pricing/course-pricing'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created).toEqual({ id: 4, ...newPricing });
  });

  it('should update existing pricing tier', async () => {
    const updateData = { price: 69.99, features: ['Updated features'] };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 2, ...updateData }),
    });

    const { result } = renderHook(() => usePricing());
    await result.current.fetchCoursePricing();

    await result.current.updateCoursePricing(2, updateData);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/pricing/course-pricing/2'),
      expect.objectContaining({ method: 'PUT' })
    );
  });

  it('should handle fetch error', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 500,
    });

    const { result } = renderHook(() => usePricing());

    result.current.fetchCoursePricing();

    await waitFor(() => {
      expect(result.current.error).toBe('Failed to fetch pricing');
    });
  });

  it('should handle network error', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => usePricing());

    result.current.fetchCoursePricing();

    await waitFor(() => {
      expect(result.current.error).toBe('Network error');
    });
  });
});

describe('usePricingCalculator', () => {
  const mockCalculation = {
    basePrice: 59.99,
    discount: 10.00,
    tax: 4.50,
    total: 54.49,
    breakdown: {
      subtotal: 59.99,
      discountPercentage: 16.67,
      taxRate: 8.25,
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockCalculation,
    });
  });

  it('should initialize with null calculation', () => {
    const { result } = renderHook(() => usePricingCalculator());

    expect(result.current.calculation).toBeNull();
    expect(result.current.isCalculating).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should calculate price', async () => {
    const { result } = renderHook(() => usePricingCalculator());

    const request = {
      course_id: 1,
      tier: 'pro',
      quantity: 2,
    };

    const calculated = await result.current.calculatePrice(request);

    await waitFor(() => {
      expect(result.current.isCalculating).toBe(false);
    });

    expect(result.current.calculation).toEqual(mockCalculation);
    expect(calculated).toEqual(mockCalculation);
  });

  it('should clear calculation', async () => {
    const { result } = renderHook(() => usePricingCalculator());

    const request = {
      course_id: 1,
      tier: 'pro',
      quantity: 2,
    };

    await result.current.calculatePrice(request);

    await waitFor(() => {
      expect(result.current.calculation).not.toBeNull();
    });

    result.current.clearCalculation();

    expect(result.current.calculation).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should handle calculation error', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 400,
    });

    const { result } = renderHook(() => usePricingCalculator());

    try {
      await result.current.calculatePrice({ course_id: 1, tier: 'basic' });
    } catch (e) {
      // Expected to throw
    }

    await waitFor(() => {
      expect(result.current.error).toBe('Failed to calculate price');
    });
  });
});

describe('usePayments', () => {
  const mockPayments = [
    { id: 1, amount: 59.99, status: 'completed', date: '2024-01-15' },
    { id: 2, amount: 29.99, status: 'pending', date: '2024-01-20' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockPayments,
    });
  });

  it('should initialize with empty payments', () => {
    const { result } = renderHook(() => usePayments());

    expect(result.current.payments).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it('should fetch payments', async () => {
    const { result } = renderHook(() => usePayments());

    result.current.fetchPayments();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.payments).toEqual(mockPayments);
  });

  it('should fetch payments by user', async () => {
    const { result } = renderHook(() => usePayments());

    result.current.fetchPayments(123);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('user_id=123'),
        expect.any(Object)
      );
    });
  });

  it('should fetch payments by status', async () => {
    const { result } = renderHook(() => usePayments());

    result.current.fetchPayments(undefined, 'completed');

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('status=completed'),
        expect.any(Object)
      );
    });
  });

  it('should create payment intent', async () => {
    const mockIntent = {
      clientSecret: 'pi_123_secret_456',
      paymentIntentId: 'pi_123',
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockIntent,
    });

    const { result } = renderHook(() => usePayments());

    const intent = await result.current.createPaymentIntent({
      course_pricing_id: 1,
      quantity: 1,
    });

    expect(intent).toEqual(mockIntent);
  });

  it('should confirm payment', async () => {
    const mockConfirmation = { status: 'succeeded', id: 'pi_123' };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockConfirmation,
    });

    const { result } = renderHook(() => usePayments());
    await result.current.fetchPayments();

    const confirmation = await result.current.confirmPayment('pi_123');

    expect(confirmation).toEqual(mockConfirmation);
    expect(global.fetch).toHaveBeenCalledTimes(2); // fetch + confirm
  });
});

describe('useSubscriptions', () => {
  const mockSubscriptions = [
    { id: 1, plan: 'Pro', status: 'active', startDate: '2024-01-01', endDate: '2025-01-01' },
    { id: 2, plan: 'Enterprise', status: 'cancelled', startDate: '2023-06-01', endDate: '2023-12-01' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockSubscriptions,
    });
  });

  it('should fetch subscriptions for user', async () => {
    const { result } = renderHook(() => useSubscriptions());

    result.current.fetchSubscriptions(123);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.subscriptions).toEqual(mockSubscriptions);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('user_id=123'),
      expect.any(Object)
    );
  });

  it('should create subscription', async () => {
    const newSubscription = { plan: 'Pro', userId: 123 };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 3, ...newSubscription }),
    });

    const { result } = renderHook(() => useSubscriptions());

    const created = await result.current.createSubscription(newSubscription);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/pricing/subscriptions'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(3);
  });

  it('should update subscription status', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, status: 'paused' }),
    });

    const { result } = renderHook(() => useSubscriptions());
    await result.current.fetchSubscriptions(123);

    await result.current.updateSubscriptionStatus(1, 'paused');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/subscriptions/1/status'),
      expect.objectContaining({ method: 'PUT' })
    );
  });
});

describe('useCorporatePackages', () => {
  const mockPackages = [
    { id: 1, name: 'Startup', seats: 10, pricePerSeat: 49.99, features: ['All courses', 'Support'] },
    { id: 2, name: 'Enterprise', seats: 100, pricePerSeat: 39.99, features: ['All courses', 'Priority support', 'Custom integration'] },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockPackages,
    });
  });

  it('should fetch corporate packages', async () => {
    const { result } = renderHook(() => useCorporatePackages());

    result.current.fetchPackages();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.packages).toEqual(mockPackages);
  });

  it('should filter packages by status', async () => {
    const { result } = renderHook(() => useCorporatePackages());

    result.current.fetchPackages('active');

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('status=active'),
        expect.any(Object)
      );
    });
  });

  it('should create corporate package', async () => {
    const newPackage = { name: 'Custom', seats: 50, pricePerSeat: 44.99 };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 3, ...newPackage }),
    });

    const { result } = renderHook(() => useCorporatePackages());

    const created = await result.current.createPackage(newPackage);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/corporate-packages'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(created.id).toBe(3);
  });
});

describe('useCertifications', () => {
  const mockCertifications = [
    { id: 1, name: 'Python Developer', price: 99.99, validity: '2 years' },
    { id: 2, name: 'Machine Learning Expert', price: 149.99, validity: '3 years' },
  ];

  const mockUserCertifications = [
    { id: 101, certificationId: 1, userId: 123, issueDate: '2024-01-15', expiryDate: '2026-01-15' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockCertifications,
    });
  });

  it('should fetch all certifications', async () => {
    const { result } = renderHook(() => useCertifications());

    result.current.fetchCertifications();

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.certifications).toEqual(mockCertifications);
  });

  it('should fetch user certifications', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockUserCertifications,
    });

    const { result } = renderHook(() => useCertifications());

    result.current.fetchUserCertifications(123);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/certifications/user/123'),
        expect.any(Object)
      );
    });
  });

  it('should issue certification', async () => {
    const newCert = { certificationId: 2, userId: 123 };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 102, ...newCert }),
    });

    const { result } = renderHook(() => useCertifications());

    const issued = await result.current.issueCertification(newCert);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/certifications/issue'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(issued.id).toBe(102);
  });
});

describe('useRevenueAnalytics', () => {
  const mockDashboard = {
    totalRevenue: 125000,
    activeSubscriptions: 150,
    avgRevenuePerUser: 83.33,
    churnRate: 2.5,
    revenueGrowth: 15.2,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockDashboard,
    });
  });

  it('should fetch revenue dashboard', async () => {
    const { result } = renderHook(() => useRevenueAnalytics());

    result.current.fetchDashboard('2024-01-01', '2024-12-31');

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.dashboard).toEqual(mockDashboard);
  });

  it('should fetch course-specific analytics', async () => {
    const mockCourseAnalytics = {
      courseId: 1,
      courseName: 'Python Basics',
      totalRevenue: 5000,
      enrollments: 150,
      completionRate: 78.5,
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockCourseAnalytics,
    });

    const { result } = renderHook(() => useRevenueAnalytics());

    result.current.fetchCourseAnalytics(1);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/analytics/course/1'),
        expect.any(Object)
      );
    });
  });

  it('should get revenue report', async () => {
    const mockReport = {
      period: 'monthly',
      totalRevenue: 15000,
      data: [
        { month: 'Jan', revenue: 5000 },
        { month: 'Feb', revenue: 5500 },
        { month: 'Mar', revenue: 4500 },
      ],
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockReport,
    });

    const { result } = renderHook(() => useRevenueAnalytics());

    const report = await result.current.getRevenueReport('2024-01-01', '2024-03-31', 'monthly');

    expect(report).toEqual(mockReport);
  });
});

describe('useCheckout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with empty checkout session', () => {
    const { result } = renderHook(() => useCheckout());

    expect(result.current.isProcessing).toBe(false);
    expect(result.current.checkoutSession).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should process checkout', async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ total: 54.99 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ clientSecret: 'pi_123_secret' }),
      });

    const { result } = renderHook(() => useCheckout());

    const formData = {
      courseId: 1,
      tier: 'pro',
      quantity: 1,
      isCorporate: false,
      promoCode: 'SAVE10',
    };

    const resultData = await result.current.processCheckout(formData);

    expect(resultData.pricing.total).toBe(54.99);
    expect(resultData.paymentIntent.clientSecret).toBe('pi_123_secret');
  });

  it('should create checkout session', async () => {
    const mockSession = {
      id: 'cs_test_123',
      url: 'https://checkout.stripe.com/pay/cs_test_123',
    };
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockSession,
    });

    const { result } = renderHook(() => useCheckout());

    const session = await result.current.createCheckoutSession({
      courseId: 1,
      quantity: 1,
    });

    expect(session).toEqual(mockSession);
    expect(result.current.checkoutSession).toEqual(mockSession);
  });

  it('should redirect to checkout', () => {
    const { result } = renderHook(() => useCheckout());

    const originalLocation = window.location;
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true,
    });

    result.current.redirectToCheckout('cs_test_123');

    expect(window.location.href).toContain('/checkout/session/cs_test_123');

    Object.defineProperty(window, 'location', { value: originalLocation });
  });

  it('should handle checkout error', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Checkout failed'));

    const { result } = renderHook(() => useCheckout());

    try {
      await result.current.processCheckout({
        courseId: 1,
        tier: 'basic',
        quantity: 1,
      });
    } catch (e) {
      // Expected
    }

    await waitFor(() => {
      expect(result.current.error).toBe('Checkout failed');
    });
  });
});
