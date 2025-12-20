"""
Course Management Router for Brain AI LMS
Handles course operations, enrollment, and catalog management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.models.course import Course, CourseLevel, CourseCategory
from app.models.lms_models import CourseEnrollment, EnrollmentStatus, Progress
from app.services.course_service import CourseService
from app.schemas.course_schemas import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse,
    CourseEnrollmentRequest, CourseEnrollmentResponse,
    CourseFilterParams, CourseReviewRequest, CourseReviewResponse
)
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=CourseListResponse)
async def get_courses(
    skip: int = Query(0, ge=0, description="Number of courses to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of courses to return"),
    level: Optional[CourseLevel] = Query(None, description="Filter by course level"),
    category: Optional[CourseCategory] = Query(None, description="Filter by course category"),
    price_min: Optional[float] = Query(None, description="Minimum price filter"),
    price_max: Optional[float] = Query(None, description="Maximum price filter"),
    featured_only: bool = Query(False, description="Show only featured courses"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: str = Query("created_at", description="Sort field: created_at, price, rating, enrollment_count"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    db: Session = Depends(get_db)
):
    """Get courses with filtering and pagination"""
    course_service = CourseService(db)
    
    filters = CourseFilterParams(
        level=level,
        category=category,
        price_min=price_min,
        price_max=price_max,
        featured_only=featured_only,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    courses, total = await course_service.get_courses(skip=skip, limit=limit, filters=filters)
    
    return CourseListResponse(
        courses=courses,
        total=total,
        skip=skip,
        limit=limit,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

@router.get("/featured", response_model=List[CourseResponse])
async def get_featured_courses(
    limit: int = Query(6, ge=1, le=20, description="Number of featured courses to return"),
    db: Session = Depends(get_db)
):
    """Get featured courses for homepage"""
    course_service = CourseService(db)
    courses = await course_service.get_featured_courses(limit=limit)
    return courses

@router.get("/learning-paths", response_model=List[dict])
async def get_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized learning paths for the current user"""
    course_service = CourseService(db)
    paths = await course_service.get_personalized_paths(current_user)
    return paths

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    include_content: bool = Query(True, description="Include course content (modules and lessons)"),
    include_enrollment: bool = Query(False, description="Include enrollment status for current user"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed course information"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    course_service = CourseService(db)
    course_data = await course_service.get_course_details(
        course, 
        include_content=include_content,
        include_enrollment=include_enrollment and current_user is not None,
        current_user=current_user
    )
    
    return course_data

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new course (instructors and admins only)"""
    if current_user.role not in [UserRole.INSTRUCTOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors and admins can create courses"
        )
    
    course_service = CourseService(db)
    course = await course_service.create_course(course_data, current_user.id)
    return course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update course information"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check permissions
    if (current_user.role != UserRole.ADMIN and 
        course.creator_id != current_user.id and
        current_user.id not in [instructor.id for instructor in course.instructors]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    
    course_service = CourseService(db)
    updated_course = await course_service.update_course(course, course_data)
    return updated_course

@router.post("/{course_id}/enroll", response_model=CourseEnrollmentResponse)
async def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.user_id == current_user.id,
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE
        )
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    course_service = CourseService(db)
    enrollment = await course_service.enroll_course(current_user.id, course_id)
    return enrollment

@router.get("/{course_id}/enrollment", response_model=Optional[CourseEnrollmentResponse])
async def get_enrollment_status(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enrollment status for current user"""
    enrollment = db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.user_id == current_user.id,
            CourseEnrollment.course_id == course_id
        )
    ).first()
    
    if not enrollment:
        return None
    
    return CourseEnrollmentResponse(
        id=enrollment.id,
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at,
        completed_at=enrollment.completed_at,
        progress_percentage=enrollment.progress_percentage
    )

@router.get("/{course_id}/progress")
async def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a course"""
    # Check enrollment
    enrollment = db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.user_id == current_user.id,
            CourseEnrollment.course_id == course_id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    course_service = CourseService(db)
    progress_data = await course_service.get_course_progress(current_user.id, course_id)
    return progress_data

@router.post("/{course_id}/progress/update")
async def update_lesson_progress(
    course_id: int,
    lesson_id: int,
    status: str,
    progress_percentage: float,
    time_spent_minutes: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress for a specific lesson"""
    # Verify enrollment
    enrollment = db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.user_id == current_user.id,
            CourseEnrollment.course_id == course_id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    course_service = CourseService(db)
    updated_progress = await course_service.update_lesson_progress(
        current_user.id, course_id, lesson_id, status, progress_percentage, time_spent_minutes
    )
    
    return {"message": "Progress updated successfully", "progress": updated_progress}

@router.post("/{course_id}/review", response_model=CourseReviewResponse)
async def create_course_review(
    course_id: int,
    review_data: CourseReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a course review"""
    # Check if enrolled and completed
    enrollment = db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.user_id == current_user.id,
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.status == EnrollmentStatus.COMPLETED
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must complete the course to leave a review"
        )
    
    course_service = CourseService(db)
    review = await course_service.create_review(
        current_user.id, course_id, review_data
    )
    return review

@router.get("/{course_id}/reviews")
async def get_course_reviews(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get reviews for a course"""
    course_service = CourseService(db)
    reviews, total = await course_service.get_course_reviews(
        course_id, skip=skip, limit=limit
    )
    
    return {
        "reviews": reviews,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/my-courses")
async def get_my_courses(
    current_user: User = Depends(get_current_user),
    status: Optional[EnrollmentStatus] = Query(None, description="Filter by enrollment status"),
    db: Session = Depends(get_db)
):
    """Get courses for current user"""
    course_service = CourseService(db)
    courses = await course_service.get_user_courses(current_user.id, status)
    return courses

@router.get("/recommendations")
async def get_course_recommendations(
    current_user: User = Depends(get_current_user),
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get personalized course recommendations"""
    course_service = CourseService(db)
    recommendations = await course_service.get_recommendations(current_user.id, limit)
    return recommendations

@router.get("/stats/overview")
async def get_course_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get course statistics for dashboard"""
    course_service = CourseService(db)
    stats = await course_service.get_user_stats(current_user.id)
    return stats

# Brain AI specific endpoints
@router.get("/brain-ai/examples")
async def get_brain_ai_examples(
    course_id: Optional[int] = Query(None, description="Filter by course"),
    lesson_id: Optional[int] = Query(None, description="Filter by lesson"),
    category: Optional[str] = Query(None, description="Filter by example category"),
    db: Session = Depends(get_db)
):
    """Get Brain AI examples integrated with courses"""
    course_service = CourseService(db)
    examples = await course_service.get_brain_ai_examples(course_id, lesson_id, category)
    return examples

@router.post("/{course_id}/brain-ai/lab-setup")
async def setup_brain_ai_lab(
    course_id: int,
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Setup Brain AI lab environment for a lesson"""
    # Verify enrollment
    enrollment = db.query(CourseEnrollment).filter(
        and_(
            CourseEnrollment.user_id == current_user.id,
            CourseEnrollment.course_id == course_id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enrolled in this course"
        )
    
    course_service = CourseService(db)
    lab_config = await course_service.setup_brain_ai_lab(current_user.id, course_id, lesson_id)
    return lab_config

@router.get("/{course_id}/certificate/{certificate_id}/verify")
async def verify_certificate(
    course_id: int,
    certificate_id: str,
    db: Session = Depends(get_db)
):
    """Verify course certificate"""
    course_service = CourseService(db)
    certificate_info = await course_service.verify_certificate(certificate_id)
    return certificate_info