"""
Memory models for Brain AI persistent memory system
Memories are the core data structure that powers the Brain AI framework
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class MemoryBase(BaseModel):
    """Base memory model"""
    pattern_signature: str = Field(..., min_length=1, max_length=255, description="Unique pattern identifier")
    memory_type: str = Field(..., pattern="^(episodic|semantic|procedural|working|associative)$", description="Type of memory")
    content: Dict[str, Any] = Field(..., description="Memory content (structured data)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Memory context")
    strength: float = Field(default=0.5, ge=0.0, le=1.0, description="Memory strength (0-1)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Memory tags")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence level (0-1)")


class MemoryCreate(MemoryBase):
    """Model for creating a new memory"""
    tenant_id: uuid.UUID = Field(..., description="Tenant ID")
    project_id: uuid.UUID = Field(..., description="Project ID")


class MemoryUpdate(BaseModel):
    """Model for updating an existing memory"""
    pattern_signature: Optional[str] = Field(None, min_length=1, max_length=255)
    memory_type: Optional[str] = Field(None, pattern="^(episodic|semantic|procedural|working|associative)$")
    content: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    strength: Optional[float] = Field(None, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class MemoryQuery(BaseModel):
    """Model for searching memories"""
    pattern_signature: Optional[str] = Field(None, description="Pattern to search for")
    memory_type: Optional[str] = Field(None, pattern="^(episodic|semantic|procedural|working|associative)$")
    tags: Optional[List[str]] = Field(None, description="Tags to filter by")
    min_strength: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum strength threshold")
    limit: Optional[int] = Field(default=50, ge=1, le=1000, description="Maximum results to return")
    offset: Optional[int] = Field(default=0, ge=0, description="Results offset for pagination")


class Memory(MemoryBase):
    """Complete memory model"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    project_id: uuid.UUID
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemoryResponse(BaseModel):
    """Memory response model"""
    id: uuid.UUID
    pattern_signature: str
    memory_type: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    strength: float
    access_count: int
    tags: List[str]
    confidence: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemorySearchResult(BaseModel):
    """Memory search result with similarity score"""
    memory: MemoryResponse
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity to query")
    matched_fields: List[str] = Field(default_factory=list, description="Fields that matched")


class MemoryBatchCreate(BaseModel):
    """Model for creating multiple memories at once"""
    memories: List[MemoryCreate] = Field(..., min_items=1, max_items=100, description="Memories to create")
    batch_name: Optional[str] = Field(None, description="Optional batch identifier")


class MemoryStats(BaseModel):
    """Memory statistics for a project"""
    total_memories: int
    memories_by_type: Dict[str, int]
    avg_strength: float
    avg_confidence: float
    total_access_count: int
    most_accessed_memories: List[Dict[str, Any]]
    strongest_memories: List[Dict[str, Any]]
    newest_memories: List[Dict[str, Any]]
    oldest_memories: List[Dict[str, Any]]


class MemoryAnalytics(BaseModel):
    """Memory analytics and insights"""
    growth_trend: List[Dict[str, Any]]
    type_distribution: Dict[str, int]
    strength_distribution: Dict[str, float]
    tag_frequency: Dict[str, int]
    access_patterns: Dict[str, Any]
    learning_effectiveness: float


class MemoryExport(BaseModel):
    """Memory export configuration"""
    format: str = Field(..., pattern="^(json|csv|xml)$", description="Export format")
    include_content: bool = Field(default=True, description="Include memory content")
    include_context: bool = Field(default=True, description="Include memory context")
    include_metadata: bool = Field(default=True, description="Include metadata")
    memory_types: Optional[List[str]] = Field(None, description="Filter by memory types")
    date_from: Optional[datetime] = Field(None, description="Export from date")
    date_to: Optional[datetime] = Field(None, description="Export to date")


class MemoryPattern(BaseModel):
    """Memory pattern for advanced matching"""
    pattern: str = Field(..., description="Pattern string")
    pattern_type: str = Field(..., pattern="^(exact|fuzzy|regex|semantic)$", description="Pattern matching type")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Pattern weight")
    memory_types: Optional[List[str]] = Field(None, description="Applicable memory types")


class MemorySuggestion(BaseModel):
    """Suggested memories based on context"""
    memory: MemoryResponse
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    suggestion_reason: str = Field(..., description="Why this memory was suggested")
    related_patterns: List[str] = Field(default_factory=list)


# Memory type constants for easy reference
MEMORY_TYPES = {
    "episodic": "Specific events or experiences",
    "semantic": "General knowledge and facts", 
    "procedural": "How-to knowledge and processes",
    "working": "Temporary working memory",
    "associative": "Linked associations and relationships"
}


class MemoryHealth(BaseModel):
    """Memory system health metrics"""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    total_memories: int
    avg_strength: float
    avg_confidence: float
    access_rate_per_hour: float
    learning_events_per_hour: float
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
