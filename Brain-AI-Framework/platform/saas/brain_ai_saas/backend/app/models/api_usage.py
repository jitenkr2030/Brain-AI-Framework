"""
API usage tracking models
Track and monitor API usage for billing and analytics
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class APIUsage(BaseModel):
    """API usage record"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    endpoint: str
    method: str
    status_code: int
    response_time_ms: Optional[int] = None
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIUsageStats(BaseModel):
    """API usage statistics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    total_request_size_mb: float
    total_response_size_mb: float
    requests_by_endpoint: dict
    requests_by_method: dict
    requests_by_status: dict
    hourly_usage: list[dict]
    daily_usage: list[dict]


class APIUsageSummary(BaseModel):
    """API usage summary for billing"""
    period_start: datetime
    period_end: datetime
    total_requests: int
    request_limit: Optional[int]
    usage_percentage: float
    avg_response_time_ms: float
    top_endpoints: list[dict]
    cost_estimate: Optional[float] = None


class RateLimitInfo(BaseModel):
    """Rate limit information"""
    limit: int
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None


class APIEndpointStats(BaseModel):
    """Statistics for a specific API endpoint"""
    endpoint: str
    total_calls: int
    success_rate: float
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    error_rate: float
    most_common_errors: list[dict]


class APIUsageAlert(BaseModel):
    """API usage alert configuration"""
    alert_type: str = Field(..., description="Type of alert")
    threshold: int = Field(..., description="Threshold value")
    period_minutes: int = Field(..., description="Time period in minutes")
    enabled: bool = Field(default=True, description="Whether alert is enabled")
    notification_email: Optional[str] = Field(None, description="Email for notifications")
