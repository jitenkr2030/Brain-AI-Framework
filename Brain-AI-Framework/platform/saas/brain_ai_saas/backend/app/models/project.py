"""
Project models for organizing work within tenants
Projects contain memories and represent different use cases or applications
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class ProjectBase(BaseModel):
    """Base project model"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Project-specific settings")


class ProjectCreate(ProjectBase):
    """Model for creating a new project"""
    tenant_id: uuid.UUID = Field(..., description="Tenant ID")


class ProjectUpdate(BaseModel):
    """Model for updating an existing project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    settings: Optional[Dict[str, Any]] = None


class Project(ProjectBase):
    """Complete project model"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    memory_count: int = Field(default=0, description="Number of memories in project")
    api_call_count: int = Field(default=0, description="Number of API calls made")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    """Project response model"""
    id: uuid.UUID
    name: str
    description: Optional[str]
    memory_count: int
    api_call_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectStats(BaseModel):
    """Project statistics"""
    total_memories: int
    memories_by_type: Dict[str, int]
    total_api_calls: int
    avg_response_time_ms: float
    last_activity: Optional[datetime]
    growth_rate_daily: float


class ProjectSettings(BaseModel):
    """Project configuration settings"""
    auto_learning_enabled: bool = Field(default=True, description="Enable automatic learning")
    memory_retention_days: int = Field(default=365, ge=1, le=3650, description="Memory retention period")
    max_memories_per_type: Dict[str, int] = Field(default_factory=dict, description="Memory limits by type")
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="Learning rate")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold for memory matching")
    export_enabled: bool = Field(default=True, description="Enable data export")
    api_rate_limit: int = Field(default=100, ge=1, description="API rate limit per minute")


class ProjectHealth(BaseModel):
    """Project health and performance metrics"""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    memory_usage_percent: float = Field(..., ge=0.0, le=100.0)
    api_usage_percent: float = Field(..., ge=0.0, le=100.0)
    avg_response_time_ms: float
    error_rate_percent: float
    last_health_check: datetime
    issues: list[str] = Field(default_factory=list)


class ProjectSummary(BaseModel):
    """Project summary for listings"""
    id: uuid.UUID
    name: str
    description: Optional[str]
    memory_count: int
    last_activity: Optional[datetime]
    health_status: str
    
    class Config:
        from_attributes = True


class ProjectExport(BaseModel):
    """Project data export configuration"""
    format: str = Field(..., pattern="^(json|csv|xml)$", description="Export format")
    include_memories: bool = Field(default=True, description="Include memories")
    include_learning_events: bool = Field(default=True, description="Include learning events")
    include_analytics: bool = Field(default=False, description="Include analytics")
    date_from: Optional[datetime] = Field(None, description="Export from date")
    date_to: Optional[datetime] = Field(None, description="Export to date")
