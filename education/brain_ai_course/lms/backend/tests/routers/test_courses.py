"""
Tests for course endpoints
Brain AI LMS - Backend Test Suite
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCoursesAPI:
    """Test cases for courses API endpoints"""
    
    def test_get_courses_returns_list(self, client):
        """Test that GET /courses returns a list of courses"""
        response = client.get("/api/v1/courses")
        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
        assert isinstance(data["courses"], list)
    
    def test_get_courses_with_pagination(self, client):
        """Test that courses endpoint supports pagination"""
        response = client.get("/api/v1/courses?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
    
    def test_get_course_by_id_success(self, client, mock_course):
        """Test retrieving a specific course by ID"""
        with patch('app.services.course_service.get_course_by_id') as mock_get:
            mock_get.return_value = mock_course
            response = client.get("/api/v1/courses/1")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == mock_course["id"]
    
    def test_get_course_by_id_not_found(self, client):
        """Test retrieving a non-existent course"""
        with patch('app.services.course_service.get_course_by_id') as mock_get:
            mock_get.return_value = None
            response = client.get("/api/v1/courses/999")
            assert response.status_code == 404
    
    def test_get_featured_courses(self, client, mock_course):
        """Test retrieving featured courses"""
        with patch('app.services.course_service.get_featured_courses') as mock_get:
            mock_get.return_value = [mock_course]
            response = client.get("/api/v1/courses/featured")
            assert response.status_code == 200
            data = response.json()
            assert "courses" in data
            assert len(data["courses"]) >= 1
    
    def test_course_filter_by_level(self, client):
        """Test filtering courses by level"""
        response = client.get("/api/v1/courses?level=foundation")
        assert response.status_code == 200
        data = response.json()
        # All returned courses should be foundation level
        for course in data["courses"]:
            assert course.get("level") == "foundation"
    
    def test_course_search(self, client):
        """Test searching for courses"""
        response = client.get("/api/v1/courses?search=brain")
        assert response.status_code == 200
        data = response.json()
        assert "courses" in data


class TestCourseValidation:
    """Test cases for course data validation"""
    
    def test_course_requires_title(self, client):
        """Test that course creation requires a title"""
        with patch('app.services.course_service.create_course') as mock_create:
            mock_create.return_value = None
            response = client.post("/api/v1/courses", json={})
            assert response.status_code == 422  # Validation error
    
    def test_course_requires_valid_level(self, client):
        """Test that course level must be valid"""
        with patch('app.services.course_service.create_course') as mock_create:
            mock_create.return_value = None
            response = client.post("/api/v1/courses", json={
                "title": "Test Course",
                "level": "invalid_level"
            })
            assert response.status_code == 422
    
    def test_course_requires_price(self, client):
        """Test that course requires a valid price"""
        with patch('app.services.course_service.create_course') as mock_create:
            mock_create.return_value = None
            response = client.post("/api/v1/courses", json={
                "title": "Test Course",
                "level": "foundation",
                "price_usd": -100  # Invalid price
            })
            assert response.status_code == 422


class TestCourseEnrollment:
    """Test cases for course enrollment"""
    
    def test_enroll_in_course(self, client, mock_user, mock_course):
        """Test enrolling in a course"""
        with patch('app.services.course_service.enroll_user') as mock_enroll:
            mock_enroll.return_value = {
                "id": 1,
                "user_id": mock_user["id"],
                "course_id": mock_course["id"],
                "status": "active"
            }
            with patch('app.services.course_service.get_current_user') as mock_user:
                mock_user.return_value = mock_user
                
                response = client.post(
                    f"/api/v1/courses/{mock_course['id']}/enroll",
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 200
    
    def test_enroll_requires_authentication(self, client):
        """Test that enrollment requires authentication"""
        response = client.post("/api/v1/courses/1/enroll")
        assert response.status_code == 401
    
    def test_double_enrollment_prevented(self, client, mock_user, mock_course):
        """Test that users cannot enroll twice"""
        with patch('app.services.course_service.enroll_user') as mock_enroll:
            mock_enroll.side_effect = Exception("Already enrolled")
            with patch('app.services.course_service.get_current_user') as mock_user:
                mock_user.return_value = mock_user
                
                response = client.post(
                    f"/api/v1/courses/{mock_course['id']}/enroll",
                    headers={"Authorization": "Bearer test-token"}
                )
                assert response.status_code == 400
