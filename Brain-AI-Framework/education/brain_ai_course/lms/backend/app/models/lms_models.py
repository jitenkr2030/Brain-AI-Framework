"""
Database Models for Brain AI LMS
Extends Brain AI framework with Learning Management System functionality
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Float, 
    ForeignKey, Enum, JSON, ARRAY, Table, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from typing import Optional, Dict, Any

Base = declarative_base()

# Association tables for many-to-many relationships
course_instructors = Table(
    'course_instructors',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id')),
    Column('instructor_id', Integer, ForeignKey('users.id'))
)

class UserRole(enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    ENTERPRISE_ADMIN = "enterprise_admin"

class CourseLevel(enum.Enum):
    FOUNDATION = "foundation"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CourseCategory(enum.Enum):
    BRAIN_AI_FUNDAMENTALS = "brain_ai_fundamentals"
    MEMORY_SYSTEMS = "memory_systems"
    LEARNING_ENGINES = "learning_engines"
    INDUSTRY_APPLICATIONS = "industry_applications"
    ENTERPRISE_DEPLOYMENT = "enterprise_deployment"
    RESEARCH_ADVANCED = "research_advanced"

class LessonType(enum.Enum):
    VIDEO = "video"
    INTERACTIVE_LAB = "interactive_lab"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    LIVE_SESSION = "live_session"
    READING = "reading"

class EnrollmentStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    PAUSED = "paused"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class User(Base):
    """Extended User model for LMS"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # LMS-specific fields
    bio = Column(Text)
    avatar_url = Column(String(500))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    company = Column(String(100))
    job_title = Column(String(100))
    experience_level = Column(String(20), default="beginner")
    
    # Learning preferences
    learning_style = Column(String(50))  # visual, auditory, kinesthetic, reading
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Business fields
    enterprise_id = Column(Integer, ForeignKey("enterprise_profiles.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    enrollments = relationship("CourseEnrollment", back_populates="user")
    created_courses = relationship("Course", back_populates="creator")
    progress_records = relationship("Progress", back_populates="user")
    quiz_results = relationship("QuizResult", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    forum_posts = relationship("ForumPost", back_populates="author")
    forum_comments = relationship("ForumComment", back_populates="author")
    reviews = relationship("CourseReview", back_populates="user")

class Course(Base):
    """Course model"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(500))
    
    # Course metadata
    level = Column(Enum(CourseLevel), nullable=False)
    category = Column(Enum(CourseCategory), nullable=False)
    duration_hours = Column(Integer, default=0)
    difficulty_rating = Column(Float, default=1.0)  # 1.0 to 5.0
    
    # Pricing
    price_usd = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Content
    thumbnail_url = Column(String(500))
    preview_video_url = Column(String(500))
    syllabus = Column(JSON)  # Array of module summaries
    prerequisites = Column(ARRAY(String))  # Array of prerequisite course IDs
    learning_outcomes = Column(ARRAY(String))  # Array of what students will learn
    
    # LMS features
    has_interactive_labs = Column(Boolean, default=False)
    has_certification = Column(Boolean, default=False)
    has_live_sessions = Column(Boolean, default=False)
    has_community_access = Column(Boolean, default=True)
    
    # Status and visibility
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_enterprise_only = Column(Boolean, default=False)
    
    # Analytics
    enrollment_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="created_courses")
    instructors = relationship("User", secondary=course_instructors, backref="instructor_courses")
    
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course")
    reviews = relationship("CourseReview", back_populates="course")
    learning_paths = relationship("LearningPath", back_populates="course")

class Module(Base):
    """Course Module model"""
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    
    # Content
    estimated_duration_minutes = Column(Integer, default=0)
    is_prerequisite = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")
    progress_records = relationship("Progress", back_populates="module")

class Lesson(Base):
    """Lesson model"""
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    lesson_type = Column(Enum(LessonType), nullable=False)
    
    # Content
    content = Column(JSON)  # Flexible content structure
    video_url = Column(String(500))
    interactive_lab_config = Column(JSON)  # Configuration for coding exercises
    assignment_config = Column(JSON)  # Configuration for assignments
    quiz_config = Column(JSON)  # Configuration for quizzes
    
    # Meta
    order_index = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    is_prerequisite = Column(Boolean, default=False)
    
    # Brain AI integration
    brain_ai_example_id = Column(String(100))  # Links to Brain AI framework examples
    requires_brain_ai_setup = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
    progress_records = relationship("Progress", back_populates="lesson")
    quiz_results = relationship("QuizResult", back_populates="lesson")

class CourseEnrollment(Base):
    """Course enrollment model"""
    __tablename__ = "course_enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Enrollment details
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    progress_percentage = Column(Float, default=0.0)
    
    # Payment
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    payment = relationship("Payment", back_populates="enrollments")

class Progress(Base):
    """Student progress tracking"""
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    
    # Progress tracking
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed
    progress_percentage = Column(Float, default=0.0)
    time_spent_minutes = Column(Integer, default=0)
    
    # Content-specific data
    video_watch_time = Column(Integer, default=0)  # Seconds watched
    quiz_score = Column(Float, default=0.0)
    assignment_submission = Column(JSON)
    
    # Learning analytics
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    completion_date = Column(DateTime(timezone=True))
    
    # Brain AI specific
    brain_ai_activity_log = Column(JSON)  # Track Brain AI interactions
    memory_consolidation_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    course = relationship("Course")
    module = relationship("Module", back_populates="progress_records")
    lesson = relationship("Lesson", back_populates="progress_records")

class QuizResult(Base):
    """Quiz results model"""
    __tablename__ = "quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    
    # Quiz data
    quiz_config = Column(JSON, nullable=False)  # Quiz configuration
    answers = Column(JSON, nullable=False)  # User answers
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    
    # Timing
    time_taken_seconds = Column(Integer)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Feedback
    feedback = Column(JSON)  # Detailed feedback per question
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="quiz_results")
    lesson = relationship("Lesson", back_populates="quiz_results")

class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment details
    stripe_payment_intent_id = Column(String(255), unique=True)
    amount_usd = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment metadata
    description = Column(Text)
    payment_method = Column(String(50))  # card, bank_transfer, etc.
    
    # Billing
    billing_address = Column(JSON)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="payments")
    enrollments = relationship("CourseEnrollment", back_populates="payment")
    subscriptions = relationship("Subscription", back_populates="payment")

class Subscription(Base):
    """Subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    
    # Subscription details
    plan_type = Column(String(50), nullable=False)  # monthly, annual, enterprise
    price_usd = Column(Float, nullable=False)
    
    # Status and dates
    status = Column(String(20), default="active")  # active, cancelled, expired
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    cancelled_at = Column(DateTime(timezone=True))
    
    # Stripe integration
    stripe_subscription_id = Column(String(255), unique=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payment = relationship("Payment", back_populates="subscriptions")

class CourseReview(Base):
    """Course review model"""
    __tablename__ = "course_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1 to 5
    title = Column(String(255))
    content = Column(Text)
    
    # Review metadata
    is_verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class LearningPath(Base):
    """Learning path model"""
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    
    # Path details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    
    # Path structure
    path_courses = Column(JSON)  # Array of course IDs in sequence
    estimated_duration_hours = Column(Integer)
    
    # Targeting
    target_audience = Column(ARRAY(String))  # Array of target user types
    prerequisites = Column(ARRAY(String))  # Array of prerequisite paths
    
    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="learning_paths")

class EnterpriseProfile(Base):
    """Enterprise client profile"""
    __tablename__ = "enterprise_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    industry = Column(String(100))
    company_size = Column(String(20))  # small, medium, large, enterprise
    
    # Contact information
    primary_contact_name = Column(String(100))
    primary_contact_email = Column(String(255))
    primary_contact_phone = Column(String(50))
    
    # Business details
    billing_address = Column(JSON)
    tax_id = Column(String(100))
    
    # Training preferences
    preferred_training_format = Column(String(50))  # online, onsite, hybrid
    custom_curriculum_requirements = Column(Text)
    
    # Contract details
    contract_start_date = Column(DateTime(timezone=True))
    contract_end_date = Column(DateTime(timezone=True))
    total_licenses = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="active")  # active, suspended, terminated
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Community features
class ForumCategory(Base):
    """Forum category model"""
    __tablename__ = "forum_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    slug = Column(String(255), unique=True, index=True)
    icon = Column(String(100))
    
    # Permissions
    is_public = Column(Boolean, default=True)
    required_course_id = Column(Integer, ForeignKey("courses.id"))
    
    # Moderation
    is_moderated = Column(Boolean, default=True)
    moderator_ids = Column(ARRAY(Integer))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ForumPost(Base):
    """Forum post model"""
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("forum_categories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    title = Column(String(255), content = Column(Text nullable=False)
   , nullable=False)
    tags = Column(ARRAY(String))
    
    # Threading
    parent_post_id = Column(Integer, ForeignKey("forum_posts.id"))  # For replies
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    # Engagement
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="forum_posts")
    comments = relationship("ForumComment", back_populates="post")

class ForumComment(Base):
    """Forum comment model"""
    __tablename__ = "forum_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Engagement
    like_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("ForumPost", back_populates="comments")
    author = relationship("User", back_populates="forum_comments")

# Database indexes for performance
Index('idx_user_email', User.email)
Index('idx_course_slug', Course.slug)
Index('idx_course_level', Course.level)
Index('idx_course_category', Course.category)
Index('idx_enrollment_user_course', CourseEnrollment.user_id, CourseEnrollment.course_id)
Index('idx_progress_user_course', Progress.user_id, Progress.course_id)
Index('idx_payment_stripe_intent', Payment.stripe_payment_intent_id)
Index('idx_forum_post_category', ForumPost.category_id)
Index('idx_forum_comment_post', ForumComment.post_id)