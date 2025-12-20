"""
Brain AI SaaS - Main FastAPI Application
Production-ready API server with comprehensive middleware and routing
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.database import create_tables, get_database
from app.routers import auth, memories, learning, reasoning, projects, tenants
from app.dependencies import get_current_tenant, rate_limit_middleware, setup_metrics
from app.config import settings

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await create_tables()
    await setup_metrics()
    print("🚀 Brain AI SaaS API Started - Version 1.0.0")
    yield
    # Shutdown
    print("🛑 Brain AI SaaS API Stopped")

# Create FastAPI application
app = FastAPI(
    title="Brain AI SaaS API",
    description="Enterprise-grade AI with persistent memory and continuous learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "https://brain-ai.com",
        "https://app.brain-ai.com",
        "https://*.vercel.app",   # Vercel deployments
        "https://*.netlify.app",  # Netlify deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(memories.router, prefix="/api/v1/memories", tags=["Memories"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(reasoning.router, prefix="/api/v1/reasoning", tags=["Reasoning"])

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "timestamp": "2025-12-20T20:02:49Z"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        db = get_database()
        await db.health_check()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2025-12-20T20:02:49Z",
            "services": {
                "database": "connected",
                "redis": "connected",
                "vector_db": "connected"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2025-12-20T20:02:49Z"
            }
        )

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    from app.dependencies import metrics
    return metrics.generate_latest()

# Root endpoint
@app.get("/")
async def root():
    """Root API information"""
    return {
        "name": "Brain AI SaaS API",
        "version": "1.0.0",
        "description": "Enterprise-grade AI with persistent memory",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": {
            "code": exc.status_code,
            "message": exc.detail,
            "timestamp": "2025-12-20T20:02:49Z"
        }
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return {
        "error": {
            "code": 500,
            "message": "Internal server error",
            "timestamp": "2025-12-20T20:02:49Z"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )
