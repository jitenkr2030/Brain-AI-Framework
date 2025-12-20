#!/usr/bin/env python3
"""
Simplified FastAPI app for Vercel deployment
Serves the Brain AI Framework landing page with basic API endpoints
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Brain-Inspired AI Framework",
    description="🧠 Revolutionary Brain-Inspired AI Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (the landing page)
app.mount("/static", StaticFiles(directory="static"), name="static")

class HealthResponse(BaseModel):
    status: str
    message: str

class InfoResponse(BaseModel):
    name: str
    version: str
    description: str
    features: list

@app.get("/", response_class=FileResponse)
async def serve_landing_page():
    """Serve the main landing page"""
    return "index.html"

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Brain AI Framework is running successfully"
    )

@app.get("/api/info", response_model=InfoResponse)
async def get_info():
    """Get framework information"""
    return InfoResponse(
        name="Brain-Inspired AI Framework",
        version="1.0.0",
        description="🧠 Revolutionary AI system with continuous learning and persistent memory",
        features=[
            "Continuous Learning",
            "Persistent Memory",
            "Real-time Reasoning",
            "Adaptive Intelligence",
            "Scalable Architecture"
        ]
    )

@app.get("/api/demo")
async def demo_endpoint():
    """Demo endpoint for testing"""
    return {
        "message": "Brain AI Framework Demo",
        "status": "active",
        "features": [
            "🧠 Brain-inspired architecture",
            "🔄 Continuous learning",
            "💾 Persistent memory",
            "⚡ Real-time reasoning",
            "🎯 Adaptive intelligence"
        ]
    }

# Vercel handler function
def main():
    """Main handler for Vercel"""
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()