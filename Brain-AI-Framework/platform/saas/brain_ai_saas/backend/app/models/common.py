"""
Common data models for Brain AI SaaS
Shared models used across the application
"""

from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response format"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    """Error response format"""
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Optional[Dict[str, str]] = None


class MetricsResponse(BaseModel):
    """Metrics response"""
    memory_usage: Dict[str, Any]
    database_connections: int
    active_requests: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
