#!/usr/bin/env python3
"""
Brain-Inspired AI Framework - Application Entry Point
Production-grade, scalable AI system with persistent memory and continuous learning.
"""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.lifecycle import start_brain_system, shutdown_brain_system
from api.routes import router
from services.monitoring import setup_monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🧠 Starting Brain-Inspired AI Framework...")
    
    try:
        # Initialize the brain system
        await start_brain_system()
        logger.info("✅ Brain system initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start brain system: {e}")
        raise
    finally:
        logger.info("🧠 Shutting down Brain-Inspired AI Framework...")
        await shutdown_brain_system()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Brain-Inspired AI Framework",
        description="🧠 An AI system that learns continuously, remembers permanently, and reasons without retraining.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # API routes
    app.include_router(router, prefix="/api/v1")
    
    # Monitoring setup
    setup_monitoring(app)
    
    return app


def signal_handler(signum, frame):
    """Handle graceful shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


async def main():
    """Main application entry point"""
    settings = get_settings()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and configure the app
    app = create_app()
    
    # Import uvicorn for running the server
    try:
        import uvicorn
        logger.info(f"🚀 Starting server on {settings.HOST}:{settings.PORT}")
        
        config = uvicorn.Config(
            app=app,
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            workers=1 if settings.DEBUG else settings.WORKERS
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server interrupted by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise


if __name__ == "__main__":
    # Setup logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the application
    asyncio.run(main())