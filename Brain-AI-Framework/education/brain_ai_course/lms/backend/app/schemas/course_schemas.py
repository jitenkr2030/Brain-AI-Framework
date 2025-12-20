"""
Pydantic Schemas for Course Management
Defines request/response models for course-related API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.course import CourseLevel, CourseCategory
from app.models.lms_models import LessonType, EnrollmentStatus

# Enums for schemas
class CourseLevelEnum(str, Enum):
    FOUNDATION = "foundation"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CourseCategoryEnum(str, Enum):
    BRAIN_AI_FUNDAMENTALS = "brain_ai_fundamentals"
    MEMORY_SYSTEMS = "memory_systems"
    LEARNING_ENGINES = "learning_engines"
    INDUSTRY_APPLICATIONS = "industry_applications"
    ENTERPRISE_DEPLOYMENT = "enterprise_deployment"
    RESEARCH_ADVANCED = "research_advanced"

class LessonTypeEnum(str, Enum):
    VIDEO = "video"
    INTERACTIVE_LAB = "interactive_lab"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    LIVE_SESSION = "live_session"
    READING = "reading"

# Base Schemas
class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Course title")
    description: str = Field(..., min_length=10, description="Detailed course description")
    short_description: Optional[str] = Field(None, max_length=500, description="Brief course summary")
    level: CourseLevelEnum = Field(..., description="Course difficulty level")
    category: CourseCategoryEnum = Field(..., description="Course category")
    duration_hours: int = Field(..., ge=1, le=1000, description="Total course duration in hours")
    difficulty_rating: float = Field(1.0, ge=1.0, le=5.0, description="Difficulty rating from 1-5")
    price_usd: float = Field(..., ge=0, description="Course price in USD")
    currency: str = Field("USD", description="Currency code")
    learning_outcomes: List[str] = Field(default_factory=list, description="What students will learn")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite knowledge")
    syllabus: Dict[str, Any] = Field(default_factory=dict, description="Course syllabus structure")
    
    # LMS features
    has_interactive_labs: bool = Field(True, description="Course includes interactive coding labs")
    has_certification: bool = Field(True, description="Course offers certificate")
    has_live_sessions: bool = Field(False, description="Course includes live sessions")
    has_community_access: bool = Field(True, description="Course includes community access")

class CourseCreate(CourseBase):
    """Schema for creating a new course"""
    slug: Optional[str] = Field(None, description="URL-friendly course identifier")
    thumbnail_url: Optional[str] = Field(None, description="Course thumbnail image URL")
    preview_video_url: Optional[str] = Field(None, description="Course preview video URL")
    instructor_ids: Optional[List[int]] = Field(default_factory=list, description="Additional instructor user IDs")
    
    @validator('slug')
    def validate_slug(cls, v):
        if v:
            # Convert to URL-friendly format
            import re
            v = re.sub(r'[^a-zA-Z0-9-]', '-', v.lower())
            v = re.sub(r'-+', '-', v).strip('-')
        return v

class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    level: Optional[CourseLevelEnum] = None
    category: Optional[CourseCategoryEnum] = None
    duration_hours: Optional[int] = Field(None, ge=1, le=1000)
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    price_usd: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    learning_outcomes: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    syllabus: Optional[Dict[str, Any]] = None
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    has_interactive_labs: Optional[bool] = None
    has_certification: Optional[bool] = None
    has_live_sessions: Optional[bool] = None
    has_community_access: Optional[bool] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_enterprise_only: Optional[bool] = None

# Module and Lesson Schemas
class ModuleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: int = Field(..., ge=0, description="Module order in course")
    estimated_duration_minutes: int = Field(0, ge=0, le=10000)
    is_prerequisite: bool = Field(False, description="Must complete before next modules")

class ModuleCreate(ModuleBase):
    """Schema for creating a module"""
    pass

class ModuleUpdate(BaseModel):
    """Schema for updating a module"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: Optional[int] = Field(None, ge=0)
    estimated_duration_minutes: Optional[int] = Field(None, ge=0, le=10000)
    is_prerequisite: Optional[bool] = None
    is_published: Optional[bool] = None

class LessonBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    lesson_type: LessonTypeEnum = Field(..., description="Type of lesson content")
    order_index: int = Field(..., ge=0, description="Lesson order in module")
    duration_minutes: int = Field(0, ge=0, le=1000)
    is_prerequisite: bool = Field(False, description="Must complete before next lessons")

class LessonCreate(LessonBase):
    """Schema for creating a lesson"""
    content: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Lesson content")
    video_url: Optional[str] = None
    interactive_lab_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Coding lab configuration")
    assignment_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Assignment configuration")
    quiz_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Quiz configuration")
    brain_ai_example_id: Optional[str] = Field(None, description="Associated Brain AI example")
    requires_brain_ai_setup: bool = Field(False, description="Requires Brain AI environment setup")

class LessonUpdate(BaseModel):
    """Schema for updating a lesson"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    lesson_type: Optional[LessonTypeEnum] = None
    order_index: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, ge=0, le=1000)
    content: Optional[Dict[str, Any]] = None
    video_url: Optional[str] = None
    interactive_lab_config: Optional[Dict[str, Any]] = None
    assignment_config: Optional[Dict[str, Any]] = None
    quiz_config: Optional[Dict[str, Any]] = None
    brain_ai_example_id: Optional[str] = None
    requires_brain_ai_setup: Optional[bool] = None
    is_published: Optional[bool] = None
    is_prerequisite: Optional[bool] = None

# Response Schemas
class InstructorInfo(BaseModel):
    """Basic instructor information"""
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None

class LessonInfo(BaseModel):
    """Lesson information for course response"""
    id: int
    title: str
    description: Optional[str]
    lesson_type: LessonTypeEnum
    order_index: int
    duration_minutes: int
    is_published: bool
    brain_ai_example_id: Optional[str] = None
    requires_brain_ai_setup: bool = False

class ModuleInfo(BaseModel):
    """Module information for course response"""
    id: int
    title: str
    description: Optional[str]
    order_index: int
    estimated_duration_minutes: int
    is_prerequisite: bool
    is_published: bool
    lessons: List[LessonInfo]

class CourseInfo(BaseModel):
    """Basic course information"""
    id: int
    title: str
    slug: str
    short_description: Optional[str]
    level: CourseLevelEnum
    category: CourseCategoryEnum
    duration_hours: int
    difficulty_rating: float
    price_usd: float
    currency: str
    thumbnail_url: Optional[str]
    preview_video_url: Optional[str]
    learning_outcomes: List[str]
    prerequisites: List[str]
    has_interactive_labs: bool
    has_certification: bool
    has_live_sessions: bool
    has_community_access: bool
    is_published: bool
    is_featured: bool
    is_enterprise_only: bool
    enrollment_count: int
    completion_rate: float
    average_rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime

class CourseResponse(CourseInfo):
    """Full course response with detailed information"""
    description: str
    syllabus: Dict[str, Any]
    instructors: List[InstructorInfo]
    creator: InstructorInfo
    modules: List[ModuleInfo] = Field(default_factory=list)
    
    class Config:
        orm_mode = True

class CourseListResponse(BaseModel):
    """Response for course list endpoint"""
    courses: List[CourseInfo]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool

# Enrollment Schemas
class CourseEnrollmentRequest(BaseModel):
    """Request for course enrollment"""
    payment_method_id: Optional[str] = Field(None, description="Stripe payment method ID")

class CourseEnrollmentResponse(BaseModel):
    """Course enrollment response"""
    id: int
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: Optional[datetime]
    progress_percentage: float
    course: CourseInfo

# Progress Schemas
class ProgressUpdateRequest(BaseModel):
    """Request to update lesson progress"""
    lesson_id: int
    status: str = Field(..., description="not_started, in_progress, completed")
    progress_percentage: float = Field(..., ge=0, le=100)
    time_spent_minutes: int = Field(0, ge=0)
    quiz_score: Optional[float] = Field(None, ge=0, le=100)
    assignment_submission: Optional[Dict[str, Any]] = None

class ProgressResponse(BaseModel):
    """Progress response"""
    lesson_id: int
    status: str
    progress_percentage: float
    time_spent_minutes: int
    quiz_score: Optional[float]
    last_accessed: datetime
    completion_date: Optional[datetime]

class CourseProgressResponse(BaseModel):
    """Overall course progress"""
    course_id: int
    overall_progress: float
    completed_lessons: int
    total_lessons: int
    total_time_spent_minutes: int
    estimated_time_remaining_minutes: int
    lesson_progress: List[ProgressResponse]

# Review Schemas
class CourseReviewRequest(BaseModel):
    """Request for creating a course review"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    title: Optional[str] = Field(None, max_length=255, description="Review title")
    content: str = Field(..., min_length=10, max_length=2000, description="Review content")

class ReviewerInfo(BaseModel):
    """Reviewer information"""
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    verified_purchase: bool = False

class CourseReviewResponse(BaseModel):
    """Course review response"""
    id: int
    rating: int
    title: Optional[str]
    content: str
    is_verified_purchase: bool
    helpful_count: int
    created_at: datetime
    reviewer: ReviewerInfo

class CourseReviewsResponse(BaseModel):
    """Response for course reviews"""
    reviews: List[CourseReviewResponse]
    total: int
    average_rating: float
    rating_distribution: Dict[str, int]  # {"5": 10, "4": 5, ...}

# Filter Schemas
class CourseFilterParams(BaseModel):
    """Parameters for filtering courses"""
    level: Optional[CourseLevelEnum] = None
    category: Optional[CourseCategoryEnum] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    featured_only: bool = False
    search: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"

# Learning Path Schemas
class LearningPathItem(BaseModel):
    """Individual course in a learning path"""
    course_id: int
    course_title: str
    course_level: CourseLevelEnum
    order_index: int
    is_required: bool
    estimated_hours: int

class LearningPath(BaseModel):
    """Learning path structure"""
    id: int
    title: str
    description: str
    difficulty_level: str
    target_audience: List[str]
    estimated_duration_hours: int
    courses: List[LearningPathItem]
    prerequisites: List[str]

# Brain AI Integration Schemas
class BrainAIExample(BaseModel):
    """Brain AI example integration"""
    id: str
    name: str
    description: str
    category: str
    languages: List[str]
    difficulty_level: CourseLevelEnum
    course_id: Optional[int] = None
    lesson_id: Optional[int] = None
    demo_url: Optional[str] = None
    source_code_url: Optional[str] = None

class BrainAILabConfig(BaseModel):
    """Brain AI lab environment configuration"""
    lab_id: str
    environment_ready: bool
    dependencies: List[str]
    setup_instructions: List[str]
    example_code: Optional[str] = None
    interactive_url: Optional[str] = None

class CertificateInfo(BaseModel):
    """Course certificate information"""
    certificate_id: str
    course_title: str
    student_name: str
    completion_date: datetime
    instructor_name: str
    certificate_url: str
    verification_url: str

# Course Statistics Schemas
class CourseStats(BaseModel):
    """Course statistics for dashboard"""
    total_courses: int
    active_enrollments: int
    completed_courses: int
    total_learning_time_minutes: int
    average_completion_rate: float
    current_streak_days: int
    certificates_earned: int
    total_spent: float

# Advanced Schemas
class CourseSearchRequest(BaseModel):
    """Advanced course search request"""
    query: Optional[str] = Field(None, description="Text search query")
    filters: Optional[CourseFilterParams] = None
    ai_recommendations: bool = Field(False, description="Use AI for personalized recommendations")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class CourseRecommendation(BaseModel):
    """AI-powered course recommendation"""
    course: CourseInfo
    relevance_score: float
    reason: str
    personalized_factors: List[str]

class CourseRecommendationsResponse(BaseModel):
    """Response for course recommendations"""
    recommendations: List[CourseRecommendation]
    total: int
    algorithm_version: str

# Analytics Schemas
class CourseAnalytics(BaseModel):
    """Course analytics data"""
    enrollment_trends: List[Dict[str, Any]]
    completion_rates: Dict[str, float]
    average_ratings: Dict[str, float]
    revenue_data: Dict[str, float]
    engagement_metrics: Dict[str, Any]

# Export Schemas
class CourseExportRequest(BaseModel):
    """Request for course data export"""
    format: str = Field(..., description="Export format: json, csv, pdf")
    include_content: bool = Field(True, description="Include lesson content")
    include_progress: bool = Field(False, description="Include student progress")
    include_analytics: bool = Field(False, description="Include analytics data")

class CourseExportResponse(BaseModel):
    """Response for course export"""
    export_id: str
    download_url: str
    expires_at: datetime
    format: str
    file_size_mb: float