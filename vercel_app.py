#!/usr/bin/env python3
"""
Simplified FastAPI app for Vercel deployment
Serves the Brain AI Framework landing page with basic API endpoints
"""

import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

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

class HealthResponse(BaseModel):
    status: str
    message: str

class InfoResponse(BaseModel):
    name: str
    version: str
    description: str
    features: list

@app.get("/", response_class=HTMLResponse)
async def serve_landing_page():
    """Serve the main landing page"""
    try:
        # Read the index.html file
        index_path = Path("index.html")
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            # Fallback HTML if index.html doesn't exist
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>🧠 Brain AI Framework</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    h1 { color: #333; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🧠 Brain AI Framework</h1>
                    <p>Revolutionary Brain-Inspired AI System</p>
                    <p>Status: <strong>Running Successfully</strong></p>
                </div>
            </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"""
        <html><body>
        <h1>Brain AI Framework</h1>
        <p>Framework is running but landing page file not found.</p>
        <p>Error: {str(e)}</p>
        </body></html>
        """)

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

@app.get("/api/status")
async def status_endpoint():
    """Status endpoint for monitoring"""
    return {
        "status": "online",
        "version": "1.0.0",
        "uptime": "active",
        "endpoints": {
            "health": "/health",
            "info": "/api/info", 
            "demo": "/api/demo",
            "docs": "/docs"
        }
    }

# Vercel handler function
def main():
    """Main handler for Vercel"""
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()