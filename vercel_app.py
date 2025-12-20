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

@app.get("/pricing.html", response_class=HTMLResponse)
async def serve_pricing_page():
    """Serve the pricing page"""
    try:
        pricing_path = Path("pricing.html")
        if pricing_path.exists():
            with open(pricing_path, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Pricing - Brain AI Framework</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    h1 { color: #333; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>💰 Pricing Plans</h1>
                    <p>Pricing page is currently being updated.</p>
                    <a href="/">← Back to Home</a>
                </div>
            </body>
            </html>
            """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading pricing page: {str(e)}")

@app.get("/contact.html", response_class=HTMLResponse)
async def serve_contact_page():
    """Serve the contact page"""
    try:
        contact_path = Path("contact.html")
        if contact_path.exists():
            with open(contact_path, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Contact - Brain AI Framework</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    h1 { color: #333; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📞 Contact Us</h1>
                    <p>Contact page is currently being updated.</p>
                    <a href="/">← Back to Home</a>
                </div>
            </body>
            </html>
            """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading contact page: {str(e)}")

@app.get("/examples/{path:path}")
async def serve_examples(path: str = ""):
    """Serve files from the examples directory"""
    try:
        # If path is empty, serve examples index
        if not path:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Examples - Brain AI Framework</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    h1 { color: #333; }
                    .examples { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
                    .example { background: #f5f5f5; padding: 20px; border-radius: 10px; }
                    a { color: #007bff; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛠️ Brain AI Examples</h1>
                    <p>Explore real-world implementations of Brain AI Framework</p>
                    <div class="examples">
                        <div class="example">
                            <h3>Compliance Monitor</h3>
                            <p>Monitor and ensure regulatory compliance</p>
                            <a href="/examples/compliance-monitor/">View Example →</a>
                        </div>
                        <div class="example">
                            <h3>Content Creation</h3>
                            <p>AI-powered content generation system</p>
                            <a href="/examples/content-creation/">View Example →</a>
                        </div>
                        <div class="example">
                            <h3>Customer Support</h3>
                            <p>Intelligent customer service automation</p>
                            <a href="/examples/customer-support/">View Example →</a>
                        </div>
                        <div class="example">
                            <h3>Cybersecurity</h3>
                            <p>AI-driven security monitoring</p>
                            <a href="/examples/cybersecurity/">View Example →</a>
                        </div>
                    </div>
                    <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
                </div>
            </body>
            </html>
            """)
        
        # Try to serve the requested file
        file_path = Path("examples") / path
        if file_path.exists() and file_path.is_file():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            # If it's a directory, try to serve an index file
            index_file = file_path / "index.html"
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                return HTMLResponse(content="""
                <html><body>
                <h1>Example Not Found</h1>
                <p>The requested example could not be found.</p>
                <p><a href="/examples/">← Back to Examples</a></p>
                </body></html>
                """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading example: {str(e)}")

@app.get("/docs/{path:path}")
async def serve_docs(path: str = ""):
    """Serve files from the docs directory"""
    try:
        # If path is empty, serve docs index
        if not path:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Documentation - Brain AI Framework</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    h1 { color: #333; }
                    .docs { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
                    .doc { background: #f5f5f5; padding: 20px; border-radius: 10px; }
                    a { color: #007bff; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📚 Brain AI Documentation</h1>
                    <p>Complete guides and API reference for Brain AI Framework</p>
                    <div class="docs">
                        <div class="doc">
                            <h3>Getting Started</h3>
                            <p>Quick start guide and installation</p>
                            <a href="/docs/getting-started.md">Read Guide →</a>
                        </div>
                        <div class="doc">
                            <h3>API Reference</h3>
                            <p>Complete API documentation</p>
                            <a href="/docs/api-reference.md">View API →</a>
                        </div>
                        <div class="doc">
                            <h3>Examples</h3>
                            <p>Code examples and tutorials</p>
                            <a href="/docs/examples.md">View Examples →</a>
                        </div>
                        <div class="doc">
                            <h3>Deployment</h3>
                            <p>Deployment guides and best practices</p>
                            <a href="/docs/deployment-guide.md">Deployment →</a>
                        </div>
                    </div>
                    <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
                </div>
            </body>
            </html>
            """)
        
        # Try to serve the requested file
        file_path = Path("docs") / path
        if file_path.exists() and file_path.is_file():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            # If it's a directory, try to serve an index file
            index_file = file_path / "README.md"
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    content = f.read()
                return HTMLResponse(content=content)
            else:
                return HTMLResponse(content="""
                <html><body>
                <h1>Documentation Not Found</h1>
                <p>The requested documentation could not be found.</p>
                <p><a href="/docs/">← Back to Documentation</a></p>
                </body></html>
                """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading documentation: {str(e)}")

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