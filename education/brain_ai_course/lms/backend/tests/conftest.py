"""
Pytest configuration and fixtures for Brain AI LMS Backend Tests
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    session = MagicMock()
    return session


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "role": "student",
        "is_active": True,
        "is_verified": True
    }


@pytest.fixture
def mock_course():
    """Create a mock course for testing"""
    return {
        "id": 1,
        "title": "Brain AI Fundamentals",
        "slug": "brain-ai-fundamentals",
        "description": "Test course description",
        "level": "foundation",
        "category": "brain_ai_fundamentals",
        "duration_hours": 40,
        "price_usd": 2500.00,
        "is_published": True,
        "is_featured": True
    }


@pytest.fixture
def auth_headers(mock_user):
    """Create authentication headers for testing"""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def client():
    """Create a test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_pricing_service():
    """Create a mock pricing service"""
    service = MagicMock()
    service.calculate_price.return_value = {
        "original_price": 2500.00,
        "discounted_price": 2250.00,
        "discount_percentage": 10.0
    }
    service.create_payment_intent.return_value = {
        "client_secret": "test-client-secret",
        "payment_intent_id": "pi_test123"
    }
    return service


# Sample test data
SAMPLE_USERS = [
    {
        "id": 1,
        "email": "admin@brainai.com",
        "username": "admin",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "is_verified": True
    },
    {
        "id": 2,
        "email": "instructor@brainai.com",
        "username": "instructor",
        "full_name": "Instructor User",
        "role": "instructor",
        "is_active": True,
        "is_verified": True
    },
    {
        "id": 3,
        "email": "student@brainai.com",
        "username": "student",
        "full_name": "Student User",
        "role": "student",
        "is_active": True,
        "is_verified": True
    }
]

SAMPLE_COURSES = [
    {
        "id": 1,
        "title": "Brain AI Fundamentals",
        "slug": "brain-ai-fundamentals",
        "description": "Foundation course for brain-inspired AI",
        "level": "foundation",
        "category": "brain_ai_fundamentals",
        "duration_hours": 40,
        "price_usd": 2500.00,
        "is_published": True,
        "is_featured": True
    },
    {
        "id": 2,
        "title": "Advanced Memory Systems",
        "slug": "advanced-memory-systems",
        "description": "Advanced course on memory architectures",
        "level": "advanced",
        "category": "memory_systems",
        "duration_hours": 60,
        "price_usd": 3500.00,
        "is_published": True,
        "is_featured": True
    }
]


def create_test_token(user_id: int = 1, role: str = "student") -> str:
    """Create a test JWT token"""
    from jose import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    return jwt.encode(
        payload,
        "test-secret-key-for-testing-only",
        algorithm="HS256"
    )
