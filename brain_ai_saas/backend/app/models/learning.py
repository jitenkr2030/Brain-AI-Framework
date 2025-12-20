"""
Learning models for Brain AI continuous learning system
Learning events track feedback and drive memory improvement
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class LearningEventBase(BaseModel):
    """Base learning event model"""
    event_type: str = Field(..., min_length=1, max_length=100, description="Type of learning event")
    feedback_type: Optional[str] = Field(None, pattern="^(POSITIVE|NEGATIVE|NEUTRAL|CORRECTION|CONFIRMATION)$", description="Type of feedback")
    outcome: Optional[Dict[str, Any]] = Field(None, description="Outcome data")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence in the feedback")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")


class LearningEventCreate(LearningEventBase):
    """Model for creating a learning event"""
    tenant_id: uuid.UUID = Field(..., description="Tenant ID")
    memory_id: Optional[uuid.UUID] = Field(None, description="Associated memory ID")


class LearningEvent(LearningEventBase):
    """Complete learning event model"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    memory_id: Optional[uuid.UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LearningEventResponse(BaseModel):
    """Learning event response model"""
    id: uuid.UUID
    event_type: str
    feedback_type: Optional[str]
    outcome: Optional[Dict[str, Any]]
    confidence: float
    metadata: Dict[str, Any]
    created_at: datetime
    memory_id: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    """Model for submitting feedback"""
    memory_id: Optional[uuid.UUID] = Field(None, description="Memory ID (optional for general feedback)")
    feedback_type: str = Field(..., pattern="^(POSITIVE|NEGATIVE|NEUTRAL|CORRECTION|CONFIRMATION)$", description="Type of feedback")
    outcome: Optional[Dict[str, Any]] = Field(None, description="Outcome or result")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence level")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    reasoning: Optional[str] = Field(None, max_length=1000, description="Reasoning behind feedback")


class FeedbackBatch(BaseModel):
    """Model for batch feedback submission"""
    feedback_items: List[FeedbackRequest] = Field(..., min_items=1, max_items=100, description="Feedback items")
    batch_id: Optional[str] = Field(None, description="Optional batch identifier")


class LearningAnalytics(BaseModel):
    """Learning analytics and insights"""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_feedback: Dict[str, int]
    avg_confidence: float
    learning_rate: float
    improvement_trend: List[Dict[str, Any]]
    feedback_distribution: Dict[str, float]
    memory_impact: Dict[str, Any]


class LearningConfig(BaseModel):
    """Learning system configuration"""
    auto_learning_enabled: bool = Field(default=True, description="Enable automatic learning")
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="Base learning rate")
    strength_decay_rate: float = Field(default=0.01, ge=0.0, le=0.1, description="Strength decay rate")
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence for learning")
    feedback_weight: float = Field(default=1.0, ge=0.0, le=2.0, description="Feedback impact weight")
    batch_processing_enabled: bool = Field(default=True, description="Enable batch learning processing")


class LearningProgress(BaseModel):
    """Learning progress tracking"""
    memory_id: uuid.UUID
    initial_strength: float
    current_strength: float
    total_feedback_received: int
    last_feedback_date: Optional[datetime]
    improvement_percentage: float
    learning_efficiency: float


class LearningInsight(BaseModel):
    """Learning insight or recommendation"""
    insight_type: str = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact_score: float = Field(..., ge=0.0, le=1.0, description="Potential impact")
    actionable: bool = Field(..., description="Whether action can be taken")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested actions")


class LearningTrend(BaseModel):
    """Learning trend analysis"""
    period: str = Field(..., description="Time period")
    events_count: int
    avg_confidence: float
    improvement_rate: float
    top_feedback_types: List[str]
    learning_efficiency: float


class LearningHealth(BaseModel):
    """Learning system health metrics"""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    total_events: int
    events_per_hour: float
    avg_processing_time_ms: float
    success_rate: float
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class LearningMetrics(BaseModel):
    """Detailed learning metrics"""
    feedback_accuracy: float
    learning_velocity: float
    memory_retention_rate: float
    adaptation_speed: float
    error_correction_rate: float
    overall_learning_score: float


# Feedback type constants
FEEDBACK_TYPES = {
    "POSITIVE": "Positive reinforcement",
    "NEGATIVE": "Negative feedback",
    "NEUTRAL": "Neutral observation",
    "CORRECTION": "Correction or fix",
    "CONFIRMATION": "Confirmation of correctness"
}


# Learning event types
LEARNING_EVENT_TYPES = [
    "feedback_received",
    "memory_strength_updated",
    "pattern_recognized",
    "anomaly_detected",
    "adaptation_applied",
    "knowledge_extracted",
    "association_formed",
    "error_corrected",
    "performance_measured",
    "optimization_applied"
]


class LearningSummary(BaseModel):
    """Learning summary for a project"""
    total_events: int
    avg_confidence: float
    improvement_rate: float
    top_insights: List[LearningInsight]
    health_status: str
    last_activity: Optional[datetime]
