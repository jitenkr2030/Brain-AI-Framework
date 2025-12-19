#!/bin/bash

# Brain AI Framework Demo Startup Script
# Quick deployment script for demonstration purposes

echo "🧠 Brain AI Framework - Demo Deployment"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "demo.py" ]; then
    echo "❌ Please run this script from the brain_ai directory"
    exit 1
fi

echo "📦 Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv package manager..."
    uv pip install -r requirements-minimal.txt
else
    echo "Using pip package manager..."
    pip install -r requirements-minimal.txt
fi

echo ""
echo "🧪 Running functionality test..."
python test_demo.py

echo ""
echo "🚀 Starting Brain AI Demo Server..."
echo ""
echo "📡 The demo will be available at: http://localhost:8000"
echo "📖 API documentation: http://localhost:8000/docs"
echo "🎯 Demo examples: http://localhost:8000/demo/examples"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the demo server
python demo.py