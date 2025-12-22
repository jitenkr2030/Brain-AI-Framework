#!/usr/bin/env python3
"""
Brain AI Framework - Working Demo
Demonstrates the core brain-inspired AI functionality
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from core.encoder import Encoder, EventType, ContextState, IntensityLevel
from core.memory import MemoryStore, MemoryType, MemoryItem
from core.learning import LearningEngine
from core.routing import SparseRouter, ActivationMethod
from core.reasoning import ReasoningEngine
from core.feedback import FeedbackProcessor, FeedbackSource, FeedbackQuality

class MockPersistenceManager:
    """Mock persistence manager for demo purposes"""
    
    async def store_memory(self, memory_data):
        return True
    
    async def load_all_memories(self):
        return []

# Pydantic models for API
class ProcessRequest(BaseModel):
    data: Dict[str, Any]
    context: Dict[str, Any] = {}
    reasoning_type: str = "analysis"

class FeedbackRequest(BaseModel):
    memory_id: str
    feedback_type: str  # "positive", "negative", "neutral"
    outcome: Dict[str, Any] = {}
    source: str = "user"

class ProcessResponse(BaseModel):
    success: bool
    result: Dict[str, Any]
    active_memories: List[Dict[str, Any]]
    reasoning_result: Dict[str, Any] = {}
    message: str

class BrainAISystem:
    """Simplified Brain AI System for Demo"""
    
    def __init__(self):
        self.encoder = Encoder()
        self.memory_store = MemoryStore(MockPersistenceManager())  # Will use in-memory for demo
        self.learning_engine = LearningEngine()
        self.router = SparseRouter()
        self.reasoning_engine = ReasoningEngine()
        self.feedback_processor = FeedbackProcessor(self.learning_engine)
        self.initialized = False
        
    async def initialize(self):
        """Initialize the brain system"""
        try:
            await self.reasoning_engine.initialize()
            self.initialized = True
            logger.info("🧠 Brain AI System initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize brain system: {e}")
            raise
    
    async def process_input(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input through the brain-inspired AI pipeline"""
        if not self.initialized:
            raise Exception("Brain system not initialized")
        
        context = context or {}
        
        # Step 1: Encode input into patterns
        encoded = self.encoder.encode(data)
        pattern = encoded["pattern"]
        context_info = encoded["context"]
        
        logger.info(f"🧠 Processing input: {pattern['type']}")
        
        # Step 2: Create memory from pattern
        memory = self.memory_store.create_memory_item(
            pattern_signature=pattern["signature"],
            content={"data": data, "pattern": pattern},
            context=context_info,
            memory_type=MemoryType.EPISODIC
        )
        
        # Store memory
        memory_id = await self.memory_store.store(memory)
        
        # Step 3: Retrieve relevant memories
        relevant_memories = await self.memory_store.retrieve(
            pattern["signature"], 
            context_info
        )
        
        # Step 4: Apply sparse activation
        active_memories = self.router.activate(
            relevant_memories, 
            context_info
        )
        
        # Step 5: Reasoning
        reasoning_result = await self.reasoning_engine.reason(
            active_memories, 
            {**context_info, "query": str(data)}
        )
        
        return {
            "memory_id": memory_id,
            "pattern": pattern,
            "context": context_info,
            "active_memories": [mem.to_dict() for mem in active_memories],
            "reasoning_result": reasoning_result,
            "total_memories": len(relevant_memories),
            "timestamp": datetime.now().isoformat()
        }
    
    async def provide_feedback(self, memory_id: str, feedback_type: str, outcome: Dict[str, Any], source: str = "user") -> Dict[str, Any]:
        """Process feedback and update memory strength"""
        try:
            result = await self.feedback_processor.process_feedback(
                memory_id=memory_id,
                feedback_type=feedback_type,
                outcome=outcome,
                source=FeedbackSource(source),
                quality=FeedbackQuality.HIGH
            )
            
            return {
                "success": True,
                "feedback_queued": result["feedback_queued"],
                "memory_id": memory_id,
                "message": f"Feedback processed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "memory_id": memory_id
            }

# Global brain system instance
brain_system = BrainAISystem()

# FastAPI application
app = FastAPI(
    title="Brain AI Framework Demo",
    description="🧠 A working demonstration of brain-inspired AI with persistent memory and learning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize brain system on startup"""
    await brain_system.initialize()

@app.get("/")
async def root():
    """Root endpoint with demo information"""
    return {
        "message": "🧠 Brain AI Framework Demo",
        "version": "1.0.0",
        "endpoints": {
            "process": "POST /process - Process input through brain AI",
            "feedback": "POST /feedback - Provide feedback to improve learning",
            "status": "GET /status - System status and statistics",
            "memories": "GET /memories - View stored memories"
        },
        "brain_ai_features": [
            "🧠 Pattern Recognition & Encoding",
            "💾 Persistent Memory Storage", 
            "🔬 Sparse Memory Activation",
            "🤔 Intelligent Reasoning",
            "📚 Continuous Learning",
            "🔄 Feedback Processing"
        ]
    }

@app.post("/process", response_model=ProcessResponse)
async def process_input(request: ProcessRequest):
    """Process input through brain-inspired AI pipeline"""
    try:
        result = await brain_system.process_input(request.data, request.context)
        
        return ProcessResponse(
            success=True,
            result=result,
            active_memories=result["active_memories"],
            reasoning_result=result["reasoning_result"],
            message=f"Successfully processed input with {result['total_memories']} relevant memories"
        )
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback to improve learning"""
    try:
        result = await brain_system.provide_feedback(
            request.memory_id,
            request.feedback_type,
            request.outcome,
            request.source
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def system_status():
    """Get system status and statistics"""
    try:
        stats = {
            "initialized": brain_system.initialized,
            "encoder_stats": brain_system.encoder.get_pattern_stats(),
            "router_stats": brain_system.router.get_activation_statistics(),
            "learning_stats": brain_system.learning_engine.get_learning_statistics(),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "healthy" if brain_system.initialized else "initializing",
            "brain_ai_system": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/memories")
async def list_memories():
    """List all stored memories"""
    try:
        # Get all memories from the store
        all_memories = brain_system.memory_store._memory_cache
        
        memories_list = []
        for memory in all_memories.values():
            memories_list.append({
                "id": memory.id,
                "pattern_signature": memory.pattern_signature,
                "memory_type": memory.memory_type.value,
                "strength": memory.strength,
                "access_count": memory.access_count,
                "created_at": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat()
            })
        
        return {
            "total_memories": len(memories_list),
            "memories": memories_list
        }
        
    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo/examples")
async def demo_examples():
    """Get example inputs for demonstration"""
    examples = {
        "business_intelligence": {
            "description": "Analyze business performance data",
            "input": {
                "metric": "revenue",
                "value": 150000,
                "period": "Q4_2025",
                "category": "software_sales"
            },
            "context": {"domain": "business", "priority": "high"}
        },
        "customer_feedback": {
            "description": "Process customer feedback",
            "input": {
                "feedback": "The new feature is excellent but needs better documentation",
                "sentiment": "positive",
                "category": "product_feedback",
                "customer_id": "cust_123"
            },
            "context": {"source": "customer", "priority": "medium"}
        },
        "system_alert": {
            "description": "Handle system monitoring alert",
            "input": {
                "alert_type": "performance",
                "severity": "warning",
                "component": "database",
                "message": "Query response time increased by 50%"
            },
            "context": {"system": "production", "priority": "high"}
        },
        "learning_event": {
            "description": "Record learning from experience",
            "input": {
                "task": "code_review",
                "outcome": "approved_with_suggestions",
                "reviewer": "senior_dev",
                "complexity": "medium"
            },
            "context": {"domain": "development", "priority": "medium"}
        }
    }
    
    return {"examples": examples}

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Brain AI Framework Demo Server...")
    logger.info("📡 Demo endpoints will be available at: http://localhost:8000")
    logger.info("📖 API documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "demo:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )