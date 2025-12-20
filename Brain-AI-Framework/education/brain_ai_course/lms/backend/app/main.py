"""
Brain AI LMS - Main Application
Extends the existing Brain AI Framework with Learning Management System functionality
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import sys

# Add parent directory to path to import Brain AI framework
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from app.database import get_db, engine
from app.models.user import User, UserRole
from app.models.course import Course, Module, Lesson, LessonType, CourseEnrollment
from app.models.progress import Progress, QuizResult
from app.models.payment import Payment, Subscription
from app.routers import (
    auth as auth_router,
    courses as courses_router,
    users as users_router,
    progress as progress_router,
    payments as payments_router,
    content as content_router,
    community as community_router
)

# Import Brain AI specific routers
try:
    from app.routers import memories, learning, reasoning, projects, tenants
    BRAIN_AI_AVAILABLE = True
except ImportError:
    BRAIN_AI_AVAILABLE = False
    print("Warning: Brain AI framework components not available in this context")

# Create tables
from app.models.base import Base
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Brain AI LMS",
    description="Learning Management System for Brain AI Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development
        "http://localhost:3001",
        "https://brainaiframework.vercel.app",  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(courses_router.router, prefix="/api/v1/courses", tags=["Courses"])
app.include_router(progress_router.router, prefix="/api/v1/progress", tags=["Progress"])
app.include_router(payments_router.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(content_router.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(community_router.router, prefix="/api/v1/community", tags=["Community"])

# Include Brain AI routers if available
if BRAIN_AI_AVAILABLE:
    app.include_router(memories.router, prefix="/api/v1/memories", tags=["Brain AI Memories"])
    app.include_router(learning.router, prefix="/api/v1/learning", tags=["Brain AI Learning"])
    app.include_router(reasoning.router, prefix="/api/v1/reasoning", tags=["Brain AI Reasoning"])
    app.include_router(projects.router, prefix="/api/v1/projects", tags=["Brain AI Projects"])
    app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Brain AI Tenants"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Brain AI LMS API",
        "version": "1.0.0",
        "status": "online",
        "brain_ai_available": BRAIN_AI_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Brain AI LMS"}

# LMS-specific endpoints
@app.get("/api/v1/lms/dashboard")
async def get_lms_dashboard(
    current_user: User = Depends(auth_router.get_current_user),
    db: Session = Depends(get_db)
):
    """Get LMS dashboard data for user"""
    from app.services.dashboard_service import DashboardService
    dashboard_service = DashboardService(db)
    
    return await dashboard_service.get_user_dashboard(current_user.id)

@app.get("/api/v1/lms/course-catalog")
async def get_course_catalog(
    level: Optional[str] = None,
    category: Optional[str] = None,
    price_range: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get course catalog with filters"""
    from app.services.course_service import CourseService
    course_service = CourseService(db)
    
    return await course_service.get_filtered_catalog(level, category, price_range)

@app.get("/api/v1/lms/learning-paths")
async def get_learning_paths(
    current_user: User = Depends(auth_router.get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized learning paths for user"""
    from app.services.path_service import PathService
    path_service = PathService(db)
    
    return await path_service.get_personalized_paths(current_user.id)

@app.get("/api/v1/lms/ai-tutor")
async def ai_tutor_chat(
    query: str,
    course_id: Optional[str] = None,
    lesson_id: Optional[str] = None,
    current_user: User = Depends(auth_router.get_current_user),
    db: Session = Depends(get_db)
):
    """AI Tutor chat for course assistance"""
    from app.services.ai_tutor_service import AITutorService
    ai_tutor = AITutorService(db)
    
    return await ai_tutor.handle_tutor_query(
        user_id=current_user.id,
        query=query,
        course_id=course_id,
        lesson_id=lesson_id
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )