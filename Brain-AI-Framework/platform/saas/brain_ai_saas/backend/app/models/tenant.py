"""
Tenant models for multi-tenancy
Tenant is the top-level entity in our SaaS architecture
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import uuid


class TenantBase(BaseModel):
    """Base tenant model"""
    name: str = Field(..., min_length=1, max_length=255, description="Tenant name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly identifier")
    plan: str = Field(..., pattern="^(free|starter|professional|enterprise)$", description="Subscription plan")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tenant-specific settings")


class TenantCreate(TenantBase):
    """Model for creating a new tenant"""
    email: EmailStr = Field(..., description="Primary contact email")
    
    @validator('slug')
    def validate_slug(cls, v):
        """Validate slug format"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()


class TenantUpdate(BaseModel):
    """Model for updating an existing tenant"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    plan: Optional[str] = Field(None, pattern="^(free|starter|professional|enterprise)$")
    settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(active|suspended|cancelled)$")


class Tenant(TenantBase):
    """Complete tenant model"""
    id: uuid.UUID
    api_key: str = Field(..., description="API key for tenant authentication")
    status: str = Field(default="active", pattern="^(active|suspended|cancelled)$")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantResponse(BaseModel):
    """Tenant response model (without sensitive data)"""
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantStats(BaseModel):
    """Tenant statistics"""
    total_projects: int
    total_memories: int
    total_api_calls: int
    plan_limit_projects: Optional[int]
    plan_limit_memories: Optional[int]
    plan_limit_api_calls: Optional[int]


class TenantUsage(BaseModel):
    """Tenant usage tracking"""
    project_count: int
    memory_count: int
    api_call_count: int
    storage_used_mb: float
    bandwidth_used_mb: float
    period_start: datetime
    period_end: datetime


class TenantLimits(BaseModel):
    """Tenant plan limits"""
    max_projects: int
    max_memories: int
    max_api_calls_per_month: int
    max_storage_gb: float
    max_bandwidth_gb_per_month: float
    rate_limit_per_minute: int
    priority_support: bool
    custom_integrations: bool
    white_label: bool
