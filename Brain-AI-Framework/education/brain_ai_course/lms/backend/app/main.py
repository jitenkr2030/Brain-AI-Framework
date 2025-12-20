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
from app.models.lms_models import User, UserRole
from app.routers import (
    courses as courses_router,
    interactive as interactive_router,
    pricing as pricing_router,
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
app.include_router(courses_router.router, prefix="/api/v1/courses", tags=["Courses"])
app.include_router(interactive_router.router, prefix="/api/v1/interactive", tags=["Interactive Features"])
app.include_router(pricing_router.router, prefix="/api/v1/pricing", tags=["Pricing & Revenue"])
app.include_router(community_router.router, prefix="/api/v1/community", tags=["Community Features"])

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
        "message": "Brain AI LMS API - Phase 3: Revenue Optimization",
        "version": "3.0.0",
        "status": "online",
        "phase": "Revenue Optimization Complete",
        "features": {
            "core_lms": "Phase 1 - MVP Development",
            "interactive_features": "Phase 2 - Competitive Differentiation", 
            "revenue_optimization": "Phase 3 - Current Phase"
        },
        "revenue_features": [
            "Tiered Course Pricing (Foundation $2,500, Implementation $3,500, Mastery $5,000)",
            "Corporate Packages ($15K-100K)",
            "Certification Programs ($500-2,000)",
            "Stripe Payment Processing",
            "Subscription Management",
            "Revenue Analytics Dashboard"
        ],
        "community_features": [
            "Alumni Network",
            "Study Groups",
            "Expert Office Hours",
            "Event Management",
            "Job Opportunities",
            "Community Analytics"
        ],
        "brain_ai_available": BRAIN_AI_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Brain AI LMS - Phase 3",
        "version": "3.0.0",
        "phase": "Revenue Optimization",
        "revenue_service_healthy": True,
        "community_service_healthy": True,
        "interactive_service_healthy": True,
        "course_service_healthy": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )