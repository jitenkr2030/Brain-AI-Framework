"""
API Routes
FastAPI routes for the Brain-Inspired AI Framework.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from loguru import logger

from app.lifecycle import get_brain_system


router = APIRouter()


# Request/Response Models

class ProcessInputRequest(BaseModel):
    """Request model for processing input"""
    data: Dict[str, Any] = Field(..., description="Input data to process")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    reasoning_type: Optional[str] = Field(default="analysis", description="Type of reasoning to perform")


class ProcessInputResponse(BaseModel):
    """Response model for processed input"""
    success: bool
    result: Dict[str, Any]
    reasoning_result: Optional[Dict[str, Any]] = None
    memory_count: int
    execution_time: float


class FeedbackRequest(BaseModel):
    """Request model for feedback"""
    memory_id: str = Field(..., description="ID of memory to update")
    feedback_type: str = Field(..., description="Type of feedback (positive, negative, neutral)")
    outcome: Dict[str, Any] = Field(..., description="Feedback outcome data")
    source: Optional[str] = Field(default="user", description="Source of feedback")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")


class FeedbackResponse(BaseModel):
    """Response model for feedback"""
    success: bool
    memory_id: str
    learning_update: Dict[str, Any]
    message: str


class ExplanationRequest(BaseModel):
    """Request model for explanation"""
    decision: str = Field(..., description="Decision to explain")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Decision context")


class PredictionRequest(BaseModel):
    """Request model for prediction"""
    situation: Dict[str, Any] = Field(..., description="Current situation")
    time_horizon: Optional[str] = Field(default="near_term", description="Prediction time horizon")


class PlanRequest(BaseModel):
    """Request model for planning"""
    goal: str = Field(..., description="Goal to achieve")
    constraints: Optional[List[str]] = Field(default=[], description="Planning constraints")


class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    status: str
    brain_system: Dict[str, Any]
    statistics: Dict[str, Any]
    uptime: float


# API Routes

@router.post("/process", response_model=ProcessInputResponse)
async def process_input(request: ProcessInputRequest):
    """
    Process input through the brain-inspired AI pipeline
    
    This endpoint:
    1. Encodes the input into patterns
    2. Retrieves relevant memories
    3. Applies sparse activation
    4. Performs reasoning
    5. Returns the result
    """
    try:
        brain_system = get_brain_system()
        
        if not brain_system._initialized:
            raise HTTPException(status_code=503, detail="Brain system not initialized")
        
        # Add reasoning type to context
        context = request.context.copy()
        context["query"] = f"Analyze this input: {request.data}"
        context["reasoning_type"] = request.reasoning_type
        
        # Process through brain system
        result = await brain_system.process_input(request.data)
        
        return ProcessInputResponse(
            success=True,
            result=result,
            reasoning_result=result.get("reasoning_result"),
            memory_count=len(result.get("active_memories", [])),
            execution_time=0.0  # Would be measured in real implementation
        )
        
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", response_model=FeedbackResponse)
async def provide_feedback(request: FeedbackRequest):
    """
    Provide feedback to update memory strength
    
    This endpoint processes feedback and updates memory through the learning engine.
    """
    try:
        brain_system = get_brain_system()
        
        if not brain_system._initialized:
            raise HTTPException(status_code=503, detail="Brain system not initialized")
        
        # Process feedback
        await brain_system.process_feedback(
            memory_id=request.memory_id,
            feedback_type=request.feedback_type,
            outcome=request.outcome
        )
        
        return FeedbackResponse(
            success=True,
            memory_id=request.memory_id,
            learning_update={"status": "processed"},
            message=f"Feedback processed for memory {request.memory_id}"
        )
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
async def explain_decision(request: ExplanationRequest):
    """
    Get explanation for a decision using memory
    
    Uses the reasoning engine to explain why a decision was made.
    """
    try:
        brain_system = get_brain_system()
        
        if not brain_system._initialized:
            raise HTTPException(status_code=503, detail="Brain system not initialized")
        
        # This would need access to the active memories from the original decision
        # For now, return a placeholder response
        explanation = {
            "decision": request.decision,
            "explanation": f"Decision '{request.decision}' was made based on available context and memory patterns.",
            "confidence": 0.7,
            "supporting_memories": [],
            "reasoning_trace": "Based on current context and available information."
        }
        
        return {
            "success": True,
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def make_prediction(request: PredictionRequest):
    """
    Make a prediction based on current situation and memories
    """
    try:
        brain_system = get_brain_system()
        
        if not brain_system._initialized:
            raise HTTPException(status_code=503, detail="Brain system not initialized")
        
        # Placeholder prediction
        prediction = {
            "prediction": f"Based on the current situation, likely outcomes include continuation of current patterns with moderate confidence.",
            "confidence": 0.6,
            "time_horizon": request.time_horizon,
            "based_on_memories": 0,
            "reasoning_trace": "Prediction based on general patterns."
        }
        
        return {
            "success": True,
            "prediction": prediction
        }
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan")
async def create_plan(request: PlanRequest):
    """
    Create an action plan to achieve a goal
    """
    try:
        brain_system = get_brain_system()
        
        if not brain_system._initialized:
            raise HTTPException(status_code=503, detail="Brain system not initialized")
        
        # Placeholder plan
        plan = {
            "plan": f"To achieve '{request.goal}', consider the following steps:\n1. Assess current situation\n2. Identify key factors\n3. Execute targeted actions\n4. Monitor progress\n5. Adjust as needed",
            "confidence": 0.6,
            "goal": request.goal,
            "constraints": request.constraints,
            "based_on_experience": 0,
            "plan_metadata": {"type": "strategic", "timeframe": "medium_term"}
        }
        
        return {
            "success": True,
            "plan": plan
        }
        
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Get current system status and statistics
    """
    try:
        brain_system = get_brain_system()
        
        # Get brain system statistics
        brain_stats = {}
        if brain_system._initialized:
            brain_stats = {
                "initialized": True,
                "memory_count": len(brain_system.memory_store._memory_cache) if brain_system.memory_store else 0,
                "encoder_stats": brain_system.encoder.get_pattern_stats() if brain_system.encoder else {},
                "memory_stats": brain_system.memory_store.get_statistics() if brain_system.memory_store else {},
                "learning_stats": brain_system.learning_engine.get_learning_statistics() if brain_system.learning_engine else {},
                "routing_stats": brain_system.sparse_router.get_activation_statistics() if brain_system.sparse_router else {},
                "reasoning_stats": brain_system.reasoning_engine.get_reasoning_statistics() if brain_system.reasoning_engine else {}
            }
        else:
            brain_stats = {"initialized": False}
        
        # Get persistence stats
        persistence_stats = {}
        if brain_system.persistence_manager:
            persistence_stats = brain_system.persistence_manager.get_statistics()
        
        return SystemStatusResponse(
            status="healthy" if brain_system._initialized else "initializing",
            brain_system=brain_stats,
            statistics=persistence_stats,
            uptime=0.0  # Would be calculated from startup time
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    try:
        brain_system = get_brain_system()
        
        if brain_system.persistence_manager:
            health = await brain_system.persistence_manager.health_check()
        else:
            health = {"status": "unknown", "error": "No persistence manager"}
        
        return {
            "status": "healthy" if health.get("status") == "healthy" else "unhealthy",
            "brain_initialized": brain_system._initialized,
            "database": health
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/memories")
async def get_memories(limit: int = 100):
    """
    Get current memories
    """
    try:
        brain_system = get_brain_system()
        
        if not brain_system._initialized or not brain_system.memory_store:
            return {"memories": [], "total": 0}
        
        memories = list(brain_system.memory_store._memory_cache.values())[:limit]
        
        return {
            "memories": [memory.to_dict() for memory in memories],
            "total": len(brain_system.memory_store._memory_cache),
            "displayed": len(memories)
        }
        
    except Exception as e:
        logger.error(f"Error getting memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def run_test(background_tasks: BackgroundTasks):
    """
    Run a simple test of the brain system
    """
    try:
        brain_system = get_brain_system()
        
        if not brain_system._initialized:
            raise HTTPException(status_code=503, detail="Brain system not initialized")
        
        # Create test input
        test_input = {
            "test": True,
            "message": "This is a test input",
            "source": "api_test"
        }
        
        # Process through brain system
        result = await brain_system.process_input(test_input)
        
        return {
            "success": True,
            "test_input": test_input,
            "result": result,
            "message": "Brain system test completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))