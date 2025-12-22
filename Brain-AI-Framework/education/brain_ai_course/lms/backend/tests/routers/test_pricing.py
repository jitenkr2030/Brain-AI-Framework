"""
Tests for pricing and payment endpoints
Brain AI LMS - Backend Test Suite
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestPricingAPI:
    """Test cases for pricing API endpoints"""
    
    def test_get_pricing_tiers(self, client):
        """Test retrieving pricing tiers"""
        response = client.get("/api/v1/pricing/tiers")
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        assert len(data["tiers"]) >= 3  # Foundation, Implementation, Mastery
    
    def test_get_tier_details(self, client):
        """Test retrieving specific tier details"""
        response = client.get("/api/v1/pricing/tiers/foundation")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "foundation"
        assert "price" in data
        assert "features" in data
    
    def test_calculate_price_with_discount(self, client):
        """Test price calculation with discount"""
        response = client.post("/api/v1/pricing/calculate", json={
            "tier_id": "foundation",
            "discount_code": "EARLY_BIRD",
            "quantity": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "original_price" in data
        assert "discounted_price" in data
        assert "savings" in data
    
    def test_calculate_price_no_discount(self, client):
        """Test price calculation without discount"""
        response = client.post("/api/v1/pricing/calculate", json={
            "tier_id": "implementation",
            "quantity": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert data["original_price"] == data["discounted_price"]
        assert data["savings"] == 0


class TestPaymentsAPI:
    """Test cases for payment processing endpoints"""
    
    def test_create_payment_intent(self, client, mock_user):
        """Test creating a payment intent"""
        with patch('app.services.pricing_service.create_payment_intent') as mock_create:
            mock_create.return_value = {
                "client_secret": "pi_test123_secret",
                "payment_intent_id": "pi_test123"
            }
            with patch('app.services.pricing_service.get_current_user') as mock_user:
                mock_user.return_value = mock_user
                
                response = client.post(
                    "/api/v1/pricing/payments/create",
                    json={
                        "tier_id": "foundation",
                        "success_url": "http://localhost:3000/success"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
                data = response.json()
                assert "client_secret" in data
                assert "payment_intent_id" in data
    
    def test_payment_requires_authentication(self, client):
        """Test that payment creation requires authentication"""
        response = client.post("/api/v1/pricing/payments/create", json={
            "tier_id": "foundation"
        })
        assert response.status_code == 401
    
    def test_get_payment_history(self, client, mock_user):
        """Test retrieving payment history"""
        with patch('app.services.pricing_service.get_payment_history') as mock_get:
            mock_get.return_value = [
                {
                    "id": 1,
                    "amount": 2500.00,
                    "status": "succeeded",
                    "created_at": "2024-01-15T10:00:00Z"
                }
            ]
            with patch('app.services.pricing_service.get_current_user') as mock_user:
                mock_user.return_value = mock_user
                
                response = client.get(
                    "/api/v1/pricing/payments/history",
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
                data = response.json()
                assert "payments" in data
                assert len(data["payments"]) >= 1


class TestDiscountCodes:
    """Test cases for discount code functionality"""
    
    def test_validate_discount_code_valid(self, client):
        """Test validating a valid discount code"""
        with patch('app.services.pricing_service.validate_discount_code') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "code": "EARLY_BIRD",
                "discount_type": "percentage",
                "discount_value": 15,
                "min_purchase": 0
            }
            
            response = client.post("/api/v1/pricing/discounts/validate", json={
                "code": "EARLY_BIRD",
                "tier_id": "foundation"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
    
    def test_validate_discount_code_invalid(self, client):
        """Test validating an invalid discount code"""
        with patch('app.services.pricing_service.validate_discount_code') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "error": "Invalid or expired discount code"
            }
            
            response = client.post("/api/v1/pricing/discounts/validate", json={
                "code": "INVALID_CODE",
                "tier_id": "foundation"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False


class TestSubscriptions:
    """Test cases for subscription management"""
    
    def test_get_subscription_plans(self, client):
        """Test retrieving available subscription plans"""
        response = client.get("/api/v1/pricing/subscriptions/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
    
    def test_create_subscription(self, client, mock_user):
        """Test creating a new subscription"""
        with patch('app.services.pricing_service.create_subscription') as mock_create:
            mock_create.return_value = {
                "id": 1,
                "status": "active",
                "plan_type": "monthly"
            }
            with patch('app.services.pricing_service.get_current_user') as mock_user:
                mock_user.return_value = mock_user
                
                response = client.post(
                    "/api/v1/pricing/subscriptions/create",
                    json={
                        "plan_type": "monthly",
                        "payment_method_id": "pm_test123"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
    
    def test_cancel_subscription(self, client, mock_user):
        """Test canceling a subscription"""
        with patch('app.services.pricing_service.cancel_subscription') as mock_cancel:
            mock_cancel.return_value = {
                "id": 1,
                "status": "cancelled",
                "cancel_at_period_end": True
            }
            with patch('app.services.pricing_service.get_current_user') as mock_user:
                mock_user.return_value = mock_user
                
                response = client.post(
                    "/api/v1/pricing/subscriptions/1/cancel",
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
