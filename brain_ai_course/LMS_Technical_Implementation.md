# 🛠️ Brain AI LMS Technical Implementation Guide

## 📋 Platform Architecture Overview

This guide provides detailed technical specifications for building a world-class Learning Management System for Brain AI education. The platform leverages modern web technologies to deliver an exceptional learning experience with interactive coding environments, progress tracking, and community features.

## 🏗️ System Architecture

### **High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Student     │ │ Instructor  │ │ Admin       │          │
│  │ App         │ │ Dashboard   │ │ Panel       │          │
│  │ (Next.js)   │ │ (Next.js)   │ │ (Next.js)   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    API Gateway                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Auth        │ │ Rate        │ │ Load        │          │
│  │ Middleware  │ │ Limiting    │ │ Balancer    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    Microservices Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Course      │ │ User        │ │ Progress    │          │
│  │ Service     │ │ Service     │ │ Service     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Payment     │ │ Content     │ │ Community   │          │
│  │ Service     │ │ Service     │ │ Service     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    Brain AI Integration                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Code        │ │ Example     │ │ Assessment  │          │
│  │ Sandbox     │ │ Runner      │ │ Engine      │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ PostgreSQL  │ │ Redis       │ │ S3/Cloud    │          │
│  │ (Primary)   │ │ (Cache)     │ │ Storage     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ Database Schema Design

### **Core Tables**

#### **Users and Authentication**
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    website_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles (extended information)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    occupation VARCHAR(255),
    company VARCHAR(255),
    experience_level VARCHAR(50) CHECK (experience_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    programming_languages TEXT[],
    interests TEXT[],
    learning_goals TEXT,
    preferred_learning_style VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- OAuth accounts (for social login)
CREATE TABLE oauth_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider, provider_id)
);
```

#### **Courses and Content**
```sql
-- Courses
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    long_description TEXT,
    thumbnail_url TEXT,
    trailer_video_url TEXT,
    level VARCHAR(50) CHECK (level IN ('beginner', 'intermediate', 'advanced')) NOT NULL,
    duration_hours INTEGER NOT NULL,
    price DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    language VARCHAR(10) DEFAULT 'en',
    is_published BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    enrollment_count INTEGER DEFAULT 0,
    completion_rate DECIMAL(5, 2) DEFAULT 0,
    average_rating DECIMAL(3, 2) DEFAULT 0,
    total_ratings INTEGER DEFAULT 0,
    prerequisites TEXT[],
    learning_objectives TEXT[],
    tags TEXT[],
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Course categories
CREATE TABLE course_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon_url TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Course-category relationships
CREATE TABLE course_category_mappings (
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    category_id UUID REFERENCES course_categories(id) ON DELETE CASCADE,
    PRIMARY KEY (course_id, category_id)
);

-- Modules (course sections)
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    sort_order INTEGER NOT NULL,
    duration_minutes INTEGER,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lessons
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT,
    content_type VARCHAR(50) CHECK (content_type IN ('video', 'text', 'quiz', 'lab', 'assignment')) NOT NULL,
    sort_order INTEGER NOT NULL,
    duration_minutes INTEGER,
    video_url TEXT,
    video_duration INTEGER,
    thumbnail_url TEXT,
    resources JSONB DEFAULT '[]',
    prerequisites UUID[],
    learning_objectives TEXT[],
    is_free BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lesson content (for different content types)
CREATE TABLE lesson_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,
    content_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quizzes
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    time_limit_minutes INTEGER,
    passing_score DECIMAL(5, 2) DEFAULT 70,
    max_attempts INTEGER DEFAULT 3,
    shuffle_questions BOOLEAN DEFAULT TRUE,
    show_correct_answers BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quiz questions
CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) CHECK (question_type IN ('multiple_choice', 'true_false', 'fill_blank', 'essay')) NOT NULL,
    options JSONB, -- For multiple choice questions
    correct_answer TEXT,
    explanation TEXT,
    points INTEGER DEFAULT 1,
    sort_order INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Coding labs
CREATE TABLE coding_labs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    starter_code TEXT,
    solution_code TEXT,
    test_cases JSONB DEFAULT '[]',
    language VARCHAR(50) NOT NULL,
    time_limit_minutes INTEGER,
    memory_limit_mb INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Enrollment and Progress**
```sql
-- Course enrollments
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    enrollment_type VARCHAR(50) CHECK (enrollment_type IN ('free', 'paid', 'subscription', 'corporate')) NOT NULL,
    payment_status VARCHAR(50) CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')) DEFAULT 'pending',
    amount_paid DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    stripe_payment_intent_id VARCHAR(255),
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    certificate_issued_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, course_id)
);

-- Lesson progress
CREATE TABLE lesson_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    status VARCHAR(50) CHECK (status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
    progress_percentage DECIMAL(5, 2) DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    last_position_seconds INTEGER DEFAULT 0, -- For video lessons
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, lesson_id)
);

-- Quiz attempts
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quiz_id UUID REFERENCES quizzes(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    score DECIMAL(5, 2),
    max_score INTEGER,
    percentage DECIMAL(5, 2),
    passed BOOLEAN DEFAULT FALSE,
    answers JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    time_taken_minutes INTEGER,
    UNIQUE(user_id, quiz_id, attempt_number)
);

-- Quiz answers
CREATE TABLE quiz_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id UUID REFERENCES quiz_questions(id) ON DELETE CASCADE,
    user_answer TEXT,
    is_correct BOOLEAN,
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Coding lab submissions
CREATE TABLE lab_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lab_id UUID REFERENCES coding_labs(id) ON DELETE CASCADE,
    submission_number INTEGER NOT NULL,
    code TEXT NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'running', 'passed', 'failed', 'error')) DEFAULT 'pending',
    test_results JSONB,
    score DECIMAL(5, 2),
    feedback TEXT,
    execution_time_ms INTEGER,
    memory_used_mb INTEGER,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    graded_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, lab_id, submission_number)
);

-- User achievements and badges
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) NOT NULL,
    achievement_data JSONB,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, achievement_type)
);
```

#### **Community Features**
```sql
-- Discussion forums
CREATE TABLE forums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Forum posts
CREATE TABLE forum_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forum_id UUID REFERENCES forums(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT NOT NULL,
    parent_post_id UUID REFERENCES forum_posts(id),
    is_pinned BOOLEAN DEFAULT FALSE,
    is_solved BOOLEAN DEFAULT FALSE,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Post votes
CREATE TABLE post_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES forum_posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vote_type VARCHAR(10) CHECK (vote_type IN ('upvote', 'downvote')) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(post_id, user_id)
);

-- Comments
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES forum_posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_comment_id UUID REFERENCES comments(id),
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Payments and Subscriptions**
```sql
-- Payment plans
CREATE TABLE payment_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_interval VARCHAR(50) CHECK (billing_interval IN ('one_time', 'monthly', 'quarterly', 'yearly')),
    stripe_price_id VARCHAR(255),
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES payment_plans(id),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) CHECK (status IN ('active', 'cancelled', 'past_due', 'unpaid')) NOT NULL,
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment transactions
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id),
    subscription_id UUID REFERENCES subscriptions(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) CHECK (status IN ('pending', 'succeeded', 'failed', 'cancelled', 'refunded')) NOT NULL,
    payment_method VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Indexes and Performance Optimization**
```sql
-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_courses_published ON courses(is_published, level);
CREATE INDEX idx_courses_featured ON courses(is_featured) WHERE is_featured = true;
CREATE INDEX idx_modules_course ON modules(course_id, sort_order);
CREATE INDEX idx_lessons_module ON lessons(module_id, sort_order);
CREATE INDEX idx_enrollments_user ON enrollments(user_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_lesson_progress_user ON lesson_progress(user_id);
CREATE INDEX idx_lesson_progress_lesson ON lesson_progress(lesson_id);
CREATE INDEX idx_forum_posts_forum ON forum_posts(forum_id, created_at);
CREATE INDEX idx_forum_posts_user ON forum_posts(user_id);

-- Full-text search indexes
CREATE INDEX idx_courses_search ON courses USING gin(to_tsvector('english', title || ' ' || description));
CREATE INDEX idx_lessons_search ON lessons USING gin(to_tsvector('english', title || ' ' || coalesce(description, '')));

-- Composite indexes for common queries
CREATE INDEX idx_lesson_progress_composite ON lesson_progress(user_id, lesson_id, status);
CREATE INDEX idx_enrollment_composite ON enrollments(user_id, course_id, payment_status);
```

## 🚀 Backend Implementation (FastAPI)

### **Main Application**
```python
# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

from app.database import init_db
from app.routers import auth, courses, users, progress, payments, community
from app.dependencies import get_current_user, get_current_admin
from app.config import settings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("🚀 Brain AI LMS API Started")
    yield
    # Shutdown
    print("🛑 Brain AI LMS API Stopped")

app = FastAPI(
    title="Brain AI LMS API",
    description="Learning Management System for Brain AI Education",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(courses.router, prefix="/api/v1/courses", tags=["Courses"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["Progress"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(community.router, prefix="/api/v1/community", tags=["Community"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {
        "message": "Brain AI LMS API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### **Database Connection**
```python
# backend/app/database.py
import asyncpg
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME", "brain_ai_lms"),
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': 'brain-ai-lms'
                }
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args):
        """Execute a query and return the result"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def fetch(self, query: str, *args):
        """Fetch all rows from a query"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row from a query"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute_query(self, query: str, *args):
        """Execute a query and return affected rows"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)

db = Database()

async def init_db():
    """Initialize database tables"""
    try:
        # Read and execute schema SQL
        with open("app/schema.sql", "r") as f:
            schema_sql = f.read()
        
        async with db.get_connection() as conn:
            await conn.execute(schema_sql)
        
        logger.info("Database schema initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
```

### **Course Management API**
```python
# backend/app/routers/courses.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
import json
from datetime import datetime

from app.database import db
from app.dependencies import get_current_user, get_current_admin
from app.models.course import CourseCreate, CourseUpdate, CourseResponse, ModuleCreate, ModuleResponse
from app.models.user import UserResponse

router = APIRouter()

class CourseListResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    thumbnail_url: Optional[str]
    level: str
    duration_hours: int
    price: float
    average_rating: float
    total_ratings: int
    enrollment_count: int
    is_published: bool
    created_at: datetime

@router.get("/", response_model=List[CourseListResponse])
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    level: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|popularity|rating|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """Get paginated list of courses with filters"""
    try:
        # Build dynamic query
        query = """
        SELECT c.*, 
               COUNT(DISTINCT e.id) as enrollment_count,
               AVG(r.rating) as avg_rating,
               COUNT(r.id) as total_ratings
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id AND e.payment_status = 'completed'
        LEFT JOIN course_ratings r ON c.id = r.course_id
        WHERE c.is_published = true
        """
        params = []
        param_count = 0
        
        # Add filters
        if level:
            param_count += 1
            query += f" AND c.level = ${param_count}"
            params.append(level)
        
        if search:
            param_count += 1
            query += f" AND to_tsvector('english', c.title || ' ' || c.description) @@ plainto_tsquery(${param_count})"
            params.append(search)
        
        # Add grouping and sorting
        query += """
        GROUP BY c.id
        ORDER BY 
        """
        
        if sort_by == "popularity":
            query += "enrollment_count"
        elif sort_by == "rating":
            query += "avg_rating"
        elif sort_by == "title":
            query += "c.title"
        else:
            query += "c.created_at"
        
        if sort_order == "asc":
            query += " ASC"
        else:
            query += " DESC"
        
        # Add pagination
        param_count += 1
        param_count += 1
        query += f" LIMIT ${param_count} OFFSET ${param_count - 1}"
        params.extend([limit, skip])
        
        results = await db.fetch(query, *params)
        
        return [
            CourseListResponse(
                id=row["id"],
                title=row["title"],
                slug=row["slug"],
                description=row["description"],
                thumbnail_url=row["thumbnail_url"],
                level=row["level"],
                duration_hours=row["duration_hours"],
                price=float(row["price"]),
                average_rating=float(row["avg_rating"]) if row["avg_rating"] else 0.0,
                total_ratings=row["total_ratings"] or 0,
                enrollment_count=row["enrollment_count"] or 0,
                is_published=row["is_published"],
                created_at=row["created_at"]
            )
            for row in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get detailed course information"""
    try:
        # Get course details
        course_query = """
        SELECT c.*, 
               u.first_name || ' ' || u.last_name as instructor_name,
               u.avatar_url as instructor_avatar,
               COUNT(DISTINCT e.id) as enrollment_count,
               AVG(r.rating) as average_rating,
               COUNT(r.id) as total_ratings
        FROM courses c
        LEFT JOIN users u ON c.created_by = u.id
        LEFT JOIN enrollments e ON c.id = e.course_id AND e.payment_status = 'completed'
        LEFT JOIN course_ratings r ON c.id = r.course_id
        WHERE c.id = $1 AND c.is_published = true
        GROUP BY c.id, u.first_name, u.last_name, u.avatar_url
        """
        
        course_result = await db.fetchrow(course_query, course_id)
        
        if not course_result:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get modules
        modules_query = """
        SELECT m.*, 
               COUNT(l.id) as lesson_count,
               SUM(l.duration_minutes) as total_duration
        FROM modules m
        LEFT JOIN lessons l ON m.id = l.module_id AND l.is_published = true
        WHERE m.course_id = $1
        GROUP BY m.id
        ORDER BY m.sort_order
        """
        modules_result = await db.fetch(modules_query, course_id)
        
        # Get user enrollment status
        enrollment = None
        progress_data = None
        
        if current_user:
            enrollment_query = """
            SELECT * FROM enrollments 
            WHERE user_id = $1 AND course_id = $2
            """
            enrollment = await db.fetchrow(enrollment_query, current_user["id"], course_id)
            
            if enrollment:
                # Get progress data
                progress_query = """
                SELECT 
                    COUNT(*) as total_lessons,
                    COUNT(CASE WHEN lp.status = 'completed' THEN 1 END) as completed_lessons,
                    AVG(lp.progress_percentage) as avg_progress
                FROM lessons l
                LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.user_id = $1
                WHERE l.module_id IN (
                    SELECT id FROM modules WHERE course_id = $2
                )
                """
                progress_result = await db.fetchrow(progress_query, current_user["id"], course_id)
                progress_data = {
                    "total_lessons": progress_result["total_lessons"] or 0,
                    "completed_lessons": progress_result["completed_lessons"] or 0,
                    "avg_progress": float(progress_result["avg_progress"]) if progress_result["avg_progress"] else 0.0
                }
        
        # Build response
        modules = [
            {
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "sort_order": row["sort_order"],
                "duration_minutes": row["duration_minutes"],
                "lesson_count": row["lesson_count"] or 0,
                "total_duration": row["total_duration"] or 0,
                "is_published": row["is_published"]
            }
            for row in modules_result
        ]
        
        return CourseResponse(
            id=course_result["id"],
            title=course_result["title"],
            slug=course_result["slug"],
            description=course_result["description"],
            long_description=course_result["long_description"],
            thumbnail_url=course_result["thumbnail_url"],
            trailer_video_url=course_result["trailer_video_url"],
            level=course_result["level"],
            duration_hours=course_result["duration_hours"],
            price=float(course_result["price"]),
            language=course_result["language"],
            prerequisites=course_result["prerequisites"] or [],
            learning_objectives=course_result["learning_objectives"] or [],
            tags=course_result["tags"] or [],
            instructor={
                "name": course_result["instructor_name"],
                "avatar": course_result["instructor_avatar"]
            },
            stats={
                "enrollment_count": course_result["enrollment_count"] or 0,
                "average_rating": float(course_result["average_rating"]) if course_result["average_rating"] else 0.0,
                "total_ratings": course_result["total_ratings"] or 0
            },
            modules=modules,
            enrollment=enrollment,
            progress=progress_data,
            created_at=course_result["created_at"],
            updated_at=course_result["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Create a new course (admin only)"""
    try:
        course_id = str(uuid.uuid4())
        
        # Insert course
        query = """
        INSERT INTO courses (
            id, title, slug, description, long_description, thumbnail_url,
            trailer_video_url, level, duration_hours, price, language,
            prerequisites, learning_objectives, tags, created_by
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
        RETURNING *
        """
        
        result = await db.fetchrow(
            query,
            course_id,
            course_data.title,
            course_data.slug,
            course_data.description,
            course_data.long_description,
            course_data.thumbnail_url,
            course_data.trailer_video_url,
            course_data.level,
            course_data.duration_hours,
            course_data.price,
            course_data.language,
            json.dumps(course_data.prerequisites),
            json.dumps(course_data.learning_objectives),
            json.dumps(course_data.tags),
            current_admin["id"]
        )
        
        return CourseResponse(
            id=result["id"],
            title=result["title"],
            slug=result["slug"],
            description=result["description"],
            long_description=result["long_description"],
            thumbnail_url=result["thumbnail_url"],
            trailer_video_url=result["trailer_video_url"],
            level=result["level"],
            duration_hours=result["duration_hours"],
            price=float(result["price"]),
            language=result["language"],
            prerequisites=result["prerequisites"] or [],
            learning_objectives=result["learning_objectives"] or [],
            tags=result["tags"] or [],
            instructor={"name": "", "avatar": None},
            stats={"enrollment_count": 0, "average_rating": 0.0, "total_ratings": 0},
            modules=[],
            enrollment=None,
            progress=None,
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )
        
    except Exception as e:
        if "duplicate key value" in str(e):
            raise HTTPException(status_code=400, detail="Course with this slug already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{course_id}/enroll")
async def enroll_in_course(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Enroll user in a course"""
    try:
        # Check if course exists and is published
        course = await db.fetchrow(
            "SELECT * FROM courses WHERE id = $1 AND is_published = true",
            course_id
        )
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if already enrolled
        existing_enrollment = await db.fetchrow(
            "SELECT * FROM enrollments WHERE user_id = $1 AND course_id = $2",
            current_user["id"], course_id
        )
        
        if existing_enrollment:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
        # Create enrollment
        enrollment_id = str(uuid.uuid4())
        enrollment_query = """
        INSERT INTO enrollments (id, user_id, course_id, enrollment_type, payment_status)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """
        
        # Free enrollment or paid enrollment based on course price
        enrollment_type = "free" if course["price"] == 0 else "paid"
        payment_status = "completed" if course["price"] == 0 else "pending"
        
        result = await db.fetchrow(
            enrollment_query,
            enrollment_id,
            current_user["id"],
            course_id,
            enrollment_type,
            payment_status
        )
        
        # Update course enrollment count
        await db.execute(
            "UPDATE courses SET enrollment_count = enrollment_count + 1 WHERE id = $1",
            course_id
        )
        
        return {
            "message": "Successfully enrolled in course",
            "enrollment": {
                "id": result["id"],
                "course_id": result["course_id"],
                "enrollment_type": result["enrollment_type"],
                "payment_status": result["payment_status"],
                "enrolled_at": result["enrolled_at"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **Progress Tracking API**
```python
# backend/app/routers/progress.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import datetime

from app.database import db
from app.dependencies import get_current_user

router = APIRouter()

class ProgressUpdate(BaseModel):
    lesson_id: str
    progress_percentage: float = 0.0
    time_spent_minutes: int = 0
    last_position_seconds: int = 0
    completed: bool = False

class ProgressResponse(BaseModel):
    id: str
    lesson_id: str
    status: str
    progress_percentage: float
    time_spent_minutes: int
    last_position_seconds: int
    completed_at: Optional[datetime]
    updated_at: datetime

@router.get("/course/{course_id}")
async def get_course_progress(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get progress for all lessons in a course"""
    try:
        # Get all lessons in the course with progress
        query = """
        SELECT l.id, l.title, l.content_type, l.duration_minutes, l.sort_order,
               lp.status, lp.progress_percentage, lp.time_spent_minutes,
               lp.last_position_seconds, lp.completed_at, lp.updated_at
        FROM lessons l
        JOIN modules m ON l.module_id = m.id
        LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.user_id = $1
        WHERE m.course_id = $2 AND l.is_published = true
        ORDER BY m.sort_order, l.sort_order
        """
        
        results = await db.fetch(query, current_user["id"], course_id)
        
        # Calculate course-level statistics
        total_lessons = len(results)
        completed_lessons = sum(1 for row in results if row["status"] == "completed")
        in_progress_lessons = sum(1 for row in results if row["status"] == "in_progress")
        not_started_lessons = sum(1 for row in results if row["status"] in [None, "not_started"])
        
        total_time_spent = sum(row["time_spent_minutes"] or 0 for row in results)
        avg_progress = sum(row["progress_percentage"] or 0 for row in results) / total_lessons if total_lessons > 0 else 0
        
        lessons_progress = [
            {
                "lesson_id": row["id"],
                "title": row["title"],
                "content_type": row["content_type"],
                "duration_minutes": row["duration_minutes"],
                "status": row["status"] or "not_started",
                "progress_percentage": row["progress_percentage"] or 0.0,
                "time_spent_minutes": row["time_spent_minutes"] or 0,
                "last_position_seconds": row["last_position_seconds"] or 0,
                "completed_at": row["completed_at"]
            }
            for row in results
        ]
        
        return {
            "course_id": course_id,
            "summary": {
                "total_lessons": total_lessons,
                "completed_lessons": completed_lessons,
                "in_progress_lessons": in_progress_lessons,
                "not_started_lessons": not_started_lessons,
                "completion_percentage": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
                "total_time_spent_minutes": total_time_spent,
                "average_progress": avg_progress
            },
            "lessons": lessons_progress
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lesson")
async def update_lesson_progress(
    progress_data: ProgressUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update progress for a specific lesson"""
    try:
        # Check if progress record exists
        existing_progress = await db.fetchrow(
            "SELECT * FROM lesson_progress WHERE user_id = $1 AND lesson_id = $2",
            current_user["id"], progress_data.lesson_id
        )
        
        # Determine status
        if progress_data.completed or progress_data.progress_percentage >= 100:
            status = "completed"
            completed_at = datetime.now()
        elif progress_data.progress_percentage > 0:
            status = "in_progress"
            completed_at = None
        else:
            status = "not_started"
            completed_at = None
        
        if existing_progress:
            # Update existing progress
            query = """
            UPDATE lesson_progress 
            SET progress_percentage = $1, 
                time_spent_minutes = time_spent_minutes + $2,
                last_position_seconds = $3,
                status = $4,
                completed_at = $5,
                updated_at = NOW()
            WHERE user_id = $6 AND lesson_id = $7
            RETURNING *
            """
            
            result = await db.fetchrow(
                query,
                min(100.0, progress_data.progress_percentage),
                progress_data.time_spent_minutes,
                progress_data.last_position_seconds,
                status,
                completed_at,
                current_user["id"],
                progress_data.lesson_id
            )
        else:
            # Create new progress record
            progress_id = str(uuid.uuid4())
            query = """
            INSERT INTO lesson_progress (
                id, user_id, lesson_id, progress_percentage, time_spent_minutes,
                last_position_seconds, status, completed_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """
            
            result = await db.fetchrow(
                query,
                progress_id,
                current_user["id"],
                progress_data.lesson_id,
                min(100.0, progress_data.progress_percentage),
                progress_data.time_spent_minutes,
                progress_data.last_position_seconds,
                status,
                completed_at
            )
        
        return {
            "message": "Progress updated successfully",
            "progress": {
                "id": result["id"],
                "lesson_id": result["lesson_id"],
                "status": result["status"],
                "progress_percentage": float(result["progress_percentage"]),
                "time_spent_minutes": result["time_spent_minutes"],
                "last_position_seconds": result["last_position_seconds"],
                "completed_at": result["completed_at"],
                "updated_at": result["updated_at"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lesson/{lesson_id}")
async def get_lesson_progress(
    lesson_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get progress for a specific lesson"""
    try:
        query = """
        SELECT lp.*, l.title as lesson_title, l.content_type
        FROM lesson_progress lp
        JOIN lessons l ON lp.lesson_id = l.id
        WHERE lp.user_id = $1 AND lp.lesson_id = $2
        """
        
        result = await db.fetchrow(query, current_user["id"], lesson_id)
        
        if not result:
            return {
                "lesson_id": lesson_id,
                "status": "not_started",
                "progress_percentage": 0.0,
                "time_spent_minutes": 0,
                "last_position_seconds": 0,
                "completed_at": None
            }
        
        return {
            "lesson_id": result["lesson_id"],
            "lesson_title": result["lesson_title"],
            "content_type": result["content_type"],
            "status": result["status"],
            "progress_percentage": float(result["progress_percentage"]),
            "time_spent_minutes": result["time_spent_minutes"],
            "last_position_seconds": result["last_position_seconds"],
            "completed_at": result["completed_at"],
            "created_at": result["created_at"],
            "updated_at": result["updated_at"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/achievements")
async def get_user_achievements(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user achievements and badges"""
    try:
        query = """
        SELECT achievement_type, achievement_data, earned_at
        FROM user_achievements
        WHERE user_id = $1
        ORDER BY earned_at DESC
        """
        
        results = await db.fetch(query, current_user["id"])
        
        achievements = [
            {
                "type": row["achievement_type"],
                "data": row["achievement_data"],
                "earned_at": row["earned_at"]
            }
            for row in results
        ]
        
        # Calculate progress towards next achievements
        progress_query = """
        SELECT 
            COUNT(DISTINCT c.id) as courses_completed,
            COUNT(DISTINCT lp.lesson_id) as lessons_completed,
            SUM(lp.time_spent_minutes) as total_time_spent,
            COUNT(DISTINCT qa.attempt_id) as quiz_attempts
        FROM users u
        LEFT JOIN enrollments e ON u.id = e.user_id
        LEFT JOIN courses c ON e.course_id = c.id
        LEFT JOIN modules m ON c.id = m.course_id
        LEFT JOIN lessons l ON m.id = l.module_id
        LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.user_id = u.id AND lp.status = 'completed'
        LEFT JOIN quizzes q ON l.id = q.lesson_id
        LEFT JOIN quiz_attempts qa ON q.id = qa.quiz_id AND qa.user_id = u.id
        WHERE u.id = $1
        """
        
        stats = await db.fetchrow(progress_query, current_user["id"])
        
        return {
            "achievements": achievements,
            "stats": {
                "courses_completed": stats["courses_completed"] or 0,
                "lessons_completed": stats["lessons_completed"] or 0,
                "total_time_spent_minutes": stats["total_time_spent"] or 0,
                "quiz_attempts": stats["quiz_attempts"] or 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🎨 Frontend Implementation (Next.js)

### **Next.js Application Structure**
```
brain-ai-lms/
├── app/                          # App Router (Next.js 14)
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   ├── (auth)/                  # Auth routes
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/             # Protected dashboard routes
│   │   ├── dashboard/
│   │   ├── courses/
│   │   ├── progress/
│   │   └── profile/
│   ├── courses/                 # Public course pages
│   │   ├── [slug]/
│   │   └── [slug]/lesson/[id]/
│   └── api/                     # API routes
├── components/                  # Reusable components
│   ├── ui/                      # UI components
│   ├── forms/                   # Form components
│   ├── course/                  # Course-specific components
│   └── layout/                  # Layout components
├── lib/                         # Utilities and configurations
│   ├── api.ts                   # API client
│   ├── auth.ts                  # Authentication logic
│   ├── db.ts                    # Database utilities
│   └── utils.ts                 # General utilities
├── hooks/                       # Custom React hooks
├── types/                       # TypeScript type definitions
└── styles/                      # CSS and styling
```

### **Main Application Setup**
```typescript
// app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/components/providers/AuthProvider';
import { QueryProvider } from '@/components/providers/QueryProvider';
import { Toaster } from '@/components/ui/toaster';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Brain AI Course Platform',
  description: 'Learn Brain-Inspired AI with hands-on examples and expert guidance',
  keywords: 'AI, Machine Learning, Brain AI, Education, Online Courses',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
```

### **Course Listing Page**
```typescript
// app/courses/page.tsx
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Filter, Star, Clock, Users, BookOpen } from 'lucide-react';
import { api } from '@/lib/api';
import { Course } from '@/types';

export default function CoursesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');

  const { data: courses = [], isLoading, error } = useQuery({
    queryKey: ['courses', searchTerm, levelFilter, sortBy, sortOrder],
    queryFn: () => api.courses.getCourses({
      search: searchTerm || undefined,
      level: levelFilter || undefined,
      sortBy,
      sortOrder,
      limit: 20,
    }),
  });

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-red-600">
          Error loading courses. Please try again.
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Brain AI Courses</h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Master brain-inspired AI with our comprehensive courses and hands-on examples
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Level Filter */}
          <Select value={levelFilter} onValueChange={setLevelFilter}>
            <SelectTrigger>
              <SelectValue placeholder="All levels" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All levels</SelectItem>
              <SelectItem value="beginner">Beginner</SelectItem>
              <SelectItem value="intermediate">Intermediate</SelectItem>
              <SelectItem value="advanced">Advanced</SelectItem>
            </SelectContent>
          </Select>

          {/* Sort By */}
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger>
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="created_at">Latest</SelectItem>
              <SelectItem value="popularity">Most Popular</SelectItem>
              <SelectItem value="rating">Highest Rated</SelectItem>
              <SelectItem value="title">Title A-Z</SelectItem>
            </SelectContent>
          </Select>

          {/* Sort Order */}
          <Select value={sortOrder} onValueChange={setSortOrder}>
            <SelectTrigger>
              <SelectValue placeholder="Order" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="desc">Descending</SelectItem>
              <SelectItem value="asc">Ascending</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Courses Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <div className="h-48 bg-gray-200 rounded-t-lg"></div>
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </CardHeader>
              <CardContent>
                <div className="h-3 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}

      {/* No Results */}
      {!isLoading && courses.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No courses found</h3>
          <p className="text-gray-500">
            Try adjusting your search criteria or browse all courses.
          </p>
        </div>
      )}
    </div>
  );
}

function CourseCard({ course }: { course: Course }) {
  const { data: enrollment } = useQuery({
    queryKey: ['enrollment', course.id],
    queryFn: () => api.enrollments.getEnrollment(course.id),
    enabled: false, // Only fetch if user is logged in
  });

  const handleEnroll = async () => {
    try {
      await api.enrollments.enrollInCourse(course.id);
      // Refresh the page or update UI
      window.location.reload();
    } catch (error) {
      console.error('Enrollment failed:', error);
    }
  };

  return (
    <Card className="group hover:shadow-lg transition-shadow duration-200">
      <div className="relative">
        <img
          src={course.thumbnail_url || '/placeholder-course.jpg'}
          alt={course.title}
          className="w-full h-48 object-cover rounded-t-lg"
        />
        <div className="absolute top-2 right-2">
          <Badge variant={course.level === 'beginner' ? 'secondary' : 
                         course.level === 'intermediate' ? 'default' : 'destructive'}>
            {course.level}
          </Badge>
        </div>
      </div>

      <CardHeader>
        <CardTitle className="line-clamp-2">{course.title}</CardTitle>
        <CardDescription className="line-clamp-3">
          {course.description}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Course Stats */}
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {course.duration_hours}h
              </div>
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                {course.enrollment_count}
              </div>
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                {course.average_rating.toFixed(1)}
              </div>
            </div>
          </div>

          {/* Tags */}
          {course.tags && course.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {course.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {course.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{course.tags.length - 3}
                </Badge>
              )}
            </div>
          )}

          {/* Price and CTA */}
          <div className="flex items-center justify-between pt-4 border-t">
            <div>
              {course.price > 0 ? (
                <span className="text-2xl font-bold">${course.price}</span>
              ) : (
                <span className="text-2xl font-bold text-green-600">Free</span>
              )}
            </div>
            <Button
              onClick={handleEnroll}
              className="group-hover:bg-primary/90"
            >
              {enrollment ? 'Continue Learning' : 'Enroll Now'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

### **Video Player Component**
```typescript
// components/course/VideoPlayer.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Maximize, 
  Settings,
  SkipBack,
  SkipForward
} from 'lucide-react';
import { api } from '@/lib/api';

interface VideoPlayerProps {
  lessonId: string;
  videoUrl: string;
  duration: number;
  currentPosition: number;
  onProgress?: (position: number, duration: number) => void;
}

export function VideoPlayer({ 
  lessonId, 
  videoUrl, 
  duration, 
  currentPosition = 0,
  onProgress 
}: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(currentPosition);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const controlsTimeoutRef = useRef<NodeJS.Timeout>();
  
  const queryClient = useQueryClient();

  // Progress update mutation
  const updateProgressMutation = useMutation({
    mutationFn: (data: { position: number; duration: number }) => 
      api.progress.updateLessonProgress({
        lesson_id: lessonId,
        progress_percentage: (data.position / data.duration) * 100,
        time_spent_minutes: Math.floor(data.position / 60),
        last_position_seconds: Math.floor(data.position),
        completed: data.position >= data.duration * 0.9,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['progress', lessonId] });
    },
  });

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      const position = video.currentTime;
      setCurrentTime(position);
      
      // Update progress every 10 seconds
      if (position % 10 < 0.1) {
        updateProgressMutation.mutate({ position, duration });
        onProgress?.(position, duration);
      }
    };

    const handleEnded = () => {
      setIsPlaying(false);
      updateProgressMutation.mutate({ position: duration, duration });
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('ended', handleEnded);
    };
  }, [duration, lessonId, onProgress, updateProgressMutation]);

  useEffect(() => {
    if (currentPosition > 0 && videoRef.current) {
      videoRef.current.currentTime = currentPosition;
    }
  }, [currentPosition]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (value: number[]) => {
    const video = videoRef.current;
    if (!video) return;

    const newTime = value[0];
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (value: number[]) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = value[0];
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isMuted) {
      video.volume = volume;
      setIsMuted(false);
    } else {
      video.volume = 0;
      setIsMuted(true);
    }
  };

  const skip = (seconds: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.currentTime = Math.max(0, Math.min(duration, video.currentTime + seconds));
  };

  const toggleFullscreen = () => {
    const container = containerRef.current;
    if (!container) return;

    if (!isFullscreen) {
      if (container.requestFullscreen) {
        container.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleMouseMove = () => {
    setShowControls(true);
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false);
      }
    }, 3000);
  };

  return (
    <div
      ref={containerRef}
      className="relative bg-black rounded-lg overflow-hidden group"
      onMouseMove={handleMouseMove}
      onMouseLeave={() => isPlaying && setShowControls(false)}
    >
      <video
        ref={videoRef}
        src={videoUrl}
        className="w-full h-full"
        onClick={togglePlay}
      />

      {/* Controls Overlay */}
      <div
        className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 transition-opacity duration-300 ${
          showControls ? 'opacity-100' : 'opacity-0'
        }`}
      >
        {/* Progress Bar */}
        <div className="mb-4">
          <Slider
            value={[currentTime]}
            onValueChange={handleSeek}
            max={duration}
            step={1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-white mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => skip(-10)}
              className="text-white hover:bg-white/20"
            >
              <SkipBack className="h-4 w-4" />
            </Button>

            <Button
              size="sm"
              variant="ghost"
              onClick={togglePlay}
              className="text-white hover:bg-white/20"
            >
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>

            <Button
              size="sm"
              variant="ghost"
              onClick={() => skip(10)}
              className="text-white hover:bg-white/20"
            >
              <SkipForward className="h-4 w-4" />
            </Button>

            <div className="flex items-center gap-2 ml-4">
              <Button
                size="sm"
                variant="ghost"
                onClick={toggleMute}
                className="text-white hover:bg-white/20"
              >
                {isMuted || volume === 0 ? (
                  <VolumeX className="h-4 w-4" />
                ) : (
                  <Volume2 className="h-4 w-4" />
                )}
              </Button>
              <div className="w-20">
                <Slider
                  value={[isMuted ? 0 : volume]}
                  onValueChange={handleVolumeChange}
                  max={1}
                  step={0.1}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              className="text-white hover:bg-white/20"
            >
              <Settings className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={toggleFullscreen}
              className="text-white hover:bg-white/20"
            >
              <Maximize className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Play Button Overlay (when paused) */}
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Button
            size="lg"
            onClick={togglePlay}
            className="rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm"
          >
            <Play className="h-8 w-8 text-white" />
          </Button>
        </div>
      )}
    </div>
  );
}
```

## 🔧 Infrastructure & Deployment

### **Docker Configuration**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### **Kubernetes Deployment**
```yaml
# kubernetes/lms-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: brain-ai-lms
  labels:
    app: brain-ai-lms
spec:
  replicas: 3
  selector:
    matchLabels:
      app: brain-ai-lms
  template:
    metadata:
      labels:
        app: brain-ai-lms
    spec:
      containers:
      - name: backend
        image: brain-ai-lms/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: lms-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: lms-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: brain-ai-lms-service
spec:
  selector:
    app: brain-ai-lms
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: brain-ai-lms-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - lms.brain-ai.com
    secretName: brain-ai-lms-tls
  rules:
  - host: lms.brain-ai.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: brain-ai-lms-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: brain-ai-lms-frontend-service
            port:
              number: 80
```

## 📊 Analytics & Monitoring

### **Student Analytics Dashboard**
```typescript
// components/analytics/StudentAnalytics.tsx
'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  Clock, 
  Target, 
  TrendingUp, 
  Award,
  Calendar
} from 'lucide-react';
import { api } from '@/lib/api';

export function StudentAnalytics() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['student-analytics'],
    queryFn: () => api.analytics.getStudentAnalytics(),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Courses Enrolled</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.totalCourses}</div>
            <p className="text-xs text-muted-foreground">
              {analytics?.completedCourses} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Learning Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.floor((analytics?.totalTimeSpent || 0) / 60)}h
            </div>
            <p className="text-xs text-muted-foreground">
              {analytics?.totalTimeSpent} minutes total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics?.averageScore?.toFixed(1)}%
            </div>
            <Progress value={analytics?.averageScore || 0} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Achievements</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.achievements?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Badges earned
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Learning Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Learning Progress</CardTitle>
          <CardDescription>
            Your progress across all enrolled courses
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analytics?.courseProgress?.map((course: any) => (
              <div key={course.courseId} className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{course.title}</h4>
                  <Badge variant={course.status === 'completed' ? 'default' : 'secondary'}>
                    {course.status}
                  </Badge>
                </div>
                <Progress value={course.progress} className="w-full" />
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{course.completedLessons} of {course.totalLessons} lessons</span>
                  <span>{course.progress}% complete</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Your latest learning activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {analytics?.recentActivity?.map((activity: any) => (
              <div key={activity.id} className="flex items-center gap-4">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                    <Calendar className="h-4 w-4 text-primary" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">
                    {activity.type === 'lesson_completed' && 'Completed lesson'}
                    {activity.type === 'quiz_passed' && 'Passed quiz'}
                    {activity.type === 'achievement_earned' && 'Earned achievement'}
                  </p>
                  <p className="text-sm text-muted-foreground truncate">
                    {activity.description}
                  </p>
                </div>
                <div className="text-sm text-muted-foreground">
                  {new Date(activity.timestamp).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Achievements */}
      {analytics?.achievements && analytics.achievements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Achievements</CardTitle>
            <CardDescription>
              Badges and milestones you've earned
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {analytics.achievements.map((achievement: any) => (
                <div key={achievement.type} className="text-center space-y-2">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                    <Award className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{achievement.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(achievement.earnedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

## 🚀 Implementation Checklist

### **Phase 1: Foundation (Weeks 1-4)**
- [ ] Database schema design and implementation
- [ ] Basic FastAPI backend with authentication
- [ ] Next.js frontend with routing and layout
- [ ] User management and profile system
- [ ] Basic course creation and management

### **Phase 2: Core Features (Weeks 5-8)**
- [ ] Course enrollment and payment processing
- [ ] Video player with progress tracking
- [ ] Quiz and assessment system
- [ ] Progress analytics and dashboards
- [ ] Mobile responsive design

### **Phase 3: Advanced Features (Weeks 9-12)**
- [ ] Interactive coding labs
- [ ] Community features (forums, discussions)
- [ ] Advanced analytics and reporting
- [ ] Certificate generation and verification
- [ ] Mobile app development

### **Phase 4: Scale & Optimize (Weeks 13-16)**
- [ ] Performance optimization
- [ ] CDN setup for video delivery
- [ ] Advanced search and filtering
- [ ] Recommendation engine
- [ ] Internationalization support

## 🎯 Success Metrics

### **Student Engagement**
- Course completion rate: >80%
- Average session duration: >30 minutes
- Lesson completion rate: >90%
- Quiz pass rate: >85%

### **Platform Performance**
- Page load time: <3 seconds
- Video streaming: <2 seconds start time
- API response time: <200ms
- Platform uptime: 99.9%

### **Business Metrics**
- Monthly active users: Target 1,000+ by month 6
- Course enrollment rate: >15% conversion
- Student satisfaction: >4.5/5 rating
- Revenue per student: >$500 average

---

This technical implementation guide provides a comprehensive roadmap for building a world-class Learning Management System for Brain AI education. The combination of modern technologies, scalable architecture, and focus on student experience will create a platform that stands out in the competitive online education market.

*Implementation Guide prepared by: MiniMax Agent*  
*Date: 2025-12-20*  
*Ready for immediate development*