"""
API Schemas
Pydantic models for request/response validation.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    """Memory types"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    ASSOCIATIVE = "associative"


class FeedbackType(str, Enum):
    """Feedback types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"
    CONFIRMATION = "confirmation"


class ReasoningType(str, Enum):
    """Reasoning types"""
    ANALYSIS = "analysis"
    EXPLANATION = "explanation"
    PREDICTION = "prediction"
    PLANNING = "planning"
    SYNTHESIS = "synthesis"
    COMPARISON = "comparison"
    EVALUATION = "evaluation"
    DEBUGGING = "debugging"


class EventType(str, Enum):
    """Event types"""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    LEARNING = "learning"
    MEMORY_ACCESS = "memory_access"
    REASONING = "reasoning"
    FEEDBACK = "feedback"
    SYSTEM = "system"
    USER_ACTION = "user_action"
    DATA_INPUT = "data_input"


# Memory schemas

class MemoryContent(BaseModel):
    """Memory content schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = []


class MemoryContext(BaseModel):
    """Memory context schema"""
    state: str = "normal"
    intensity: str = "medium"
    source: str = "system"
    metadata: Dict[str, Any] = {}


class MemoryCreate(BaseModel):
    """Schema for creating a memory"""
    pattern_signature: str = Field(..., description="Pattern signature for the memory")
    memory_type: MemoryType = MemoryType.EPISODIC
    content: MemoryContent = Field(..., description="Memory content")
    context: MemoryContext = Field(..., description="Memory context")
    strength: float = Field(default=0.5, ge=0.0, le=1.0, description="Memory strength")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Memory confidence")
    tags: List[str] = Field(default=[], description="Memory tags")


class MemoryUpdate(BaseModel):
    """Schema for updating a memory"""
    content: Optional[MemoryContent] = None
    context: Optional[MemoryContext] = None
    strength: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None


class MemoryResponse(BaseModel):
    """Schema for memory response"""
    id: str
    pattern_signature: str
    memory_type: MemoryType
    content: MemoryContent
    context: MemoryContext
    strength: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    associations: List[str]
    tags: List[str]
    confidence: float
    updated_at: datetime


# Processing schemas

class ProcessingRequest(BaseModel):
    """Schema for processing request"""
    data: Dict[str, Any] = Field(..., description="Input data to process")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    reasoning_type: ReasoningType = ReasoningType.ANALYSIS
    memory_filter: Optional[Dict[str, Any]] = Field(default={}, description="Memory filter criteria")


class ProcessingResponse(BaseModel):
    """Schema for processing response"""
    success: bool
    encoded_event: Dict[str, Any]
    active_memories: List[MemoryResponse]
    reasoning_result: Dict[str, Any]
    memory_count: int
    execution_time: float
    processing_metadata: Dict[str, Any]


# Feedback schemas

class FeedbackCreate(BaseModel):
    """Schema for creating feedback"""
    memory_id: str = Field(..., description="ID of memory to update")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    outcome: Dict[str, Any] = Field(..., description="Feedback outcome data")
    source: str = Field(default="user", description="Source of feedback")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Feedback confidence")


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    success: bool
    memory_id: str
    learning_update: Dict[str, Any]
    confidence: float
    message: str
    timestamp: datetime


# Reasoning schemas

class ReasoningRequest(BaseModel):
    """Schema for reasoning request"""
    query: str = Field(..., description="Reasoning query")
    reasoning_type: ReasoningType = ReasoningType.ANALYSIS
    memory_snapshot: List[Dict[str, Any]] = Field(..., description="Memory snapshot to reason with")
    context: Dict[str, Any] = Field(..., description="Context for reasoning")
    constraints: Optional[List[str]] = Field(default=[], description="Reasoning constraints")


class ReasoningResponse(BaseModel):
    """Schema for reasoning response"""
    result: str
    confidence: float
    reasoning_type: ReasoningType
    execution_time: float
    tokens_used: int
    timestamp: datetime
    metadata: Dict[str, Any]


class ExplanationRequest(BaseModel):
    """Schema for explanation request"""
    decision: str = Field(..., description="Decision to explain")
    active_memories: List[Dict[str, Any]] = Field(..., description="Memories that influenced the decision")
    context: Dict[str, Any] = Field(..., description="Decision context")


class ExplanationResponse(BaseModel):
    """Schema for explanation response"""
    explanation: str
    confidence: float
    supporting_memories: List[Dict[str, Any]]
    reasoning_trace: Dict[str, Any]


class PredictionRequest(BaseModel):
    """Schema for prediction request"""
    situation: Dict[str, Any] = Field(..., description="Current situation")
    active_memories: List[Dict[str, Any]] = Field(..., description="Relevant memories")
    time_horizon: str = Field(default="near_term", description="Prediction time horizon")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")


class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    prediction: Dict[str, Any]
    confidence: float
    time_horizon: str
    based_on_memories: int
    reasoning_trace: Dict[str, Any]


class PlanRequest(BaseModel):
    """Schema for planning request"""
    goal: str = Field(..., description="Goal to achieve")
    active_memories: List[Dict[str, Any]] = Field(..., description="Relevant memories for planning")
    constraints: Optional[List[str]] = Field(default=[], description="Planning constraints")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Planning context")


class PlanResponse(BaseModel):
    """Schema for planning response"""
    plan: str
    confidence: float
    goal: str
    constraints: List[str]
    based_on_experience: int
    plan_metadata: Dict[str, Any]


# System schemas

class SystemStatus(BaseModel):
    """Schema for system status"""
    status: str
    brain_initialized: bool
    uptime: float
    memory_count: int
    total_operations: int
    health_check: Dict[str, Any]


class SystemStatistics(BaseModel):
    """Schema for system statistics"""
    memory_store: Dict[str, Any]
    learning_engine: Dict[str, Any]
    reasoning_engine: Dict[str, Any]
    sparse_router: Dict[str, Any]
    feedback_processor: Dict[str, Any]
    persistence_manager: Dict[str, Any]


class SystemResponse(BaseModel):
    """Schema for system response"""
    status: SystemStatus
    statistics: SystemStatistics
    timestamp: datetime


# Error schemas

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    """Schema for validation errors"""
    error: str = "validation_error"
    message: str
    field_errors: Dict[str, List[str]]
    timestamp: datetime


# Utility schemas

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=1000, description="Items per page")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class SortParams(BaseModel):
    """Sorting parameters"""
    sort_by: Optional[str] = Field(default="created_at", description="Field to sort by")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort order")


class FilterParams(BaseModel):
    """Filtering parameters"""
    memory_type: Optional[MemoryType] = None
    min_strength: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_strength: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    pattern_signature: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class SearchRequest(BaseModel):
    """Schema for search requests"""
    query: str = Field(..., description="Search query")
    filters: Optional[FilterParams] = None
    pagination: Optional[PaginationParams] = None
    sort: Optional[SortParams] = None
    search_type: str = Field(default="fulltext", description="Type of search")


class SearchResponse(BaseModel):
    """Schema for search responses"""
    results: List[MemoryResponse]
    total: int
    page: int
    limit: int
    search_metadata: Dict[str, Any]


# Batch operation schemas

class BatchProcessRequest(BaseModel):
    """Schema for batch processing"""
    requests: List[ProcessingRequest] = Field(..., description="List of processing requests")
    parallel: bool = Field(default=True, description="Process requests in parallel")


class BatchProcessResponse(BaseModel):
    """Schema for batch processing response"""
    results: List[ProcessingResponse]
    successful: int
    failed: int
    total_processing_time: float


class BatchFeedbackRequest(BaseModel):
    """Schema for batch feedback"""
    feedback_list: List[FeedbackCreate] = Field(..., description="List of feedback items")
    parallel: bool = Field(default=True, description="Process feedback in parallel")


class BatchFeedbackResponse(BaseModel):
    """Schema for batch feedback response"""
    results: List[FeedbackResponse]
    successful: int
    failed: int