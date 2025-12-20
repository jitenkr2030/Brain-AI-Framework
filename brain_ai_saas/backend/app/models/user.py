"""
User models for authentication and authorization
Users belong to tenants and have different role-based permissions
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    role: str = Field(default="user", pattern="^(admin|user|viewer)$", description="User role")


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, description="User password")
    tenant_id: uuid.UUID = Field(..., description="Tenant ID")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Model for updating an existing user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|user|viewer)$")
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Remember login session")


class User(UserBase):
    """Complete user model"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    password_hash: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="Whether user is active")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""
    id: uuid.UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """User profile model for self-service"""
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    role: str
    tenant_name: str
    tenant_plan: str


class PasswordChange(BaseModel):
    """Model for password change"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Ensure passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class TokenData(BaseModel):
    """Token data for JWT"""
    user_id: str
    tenant_id: str
    role: str
    exp: int


class PasswordReset(BaseModel):
    """Model for password reset request"""
    email: EmailStr = Field(..., description="User email for password reset")


class PasswordResetConfirm(BaseModel):
    """Model for password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Ensure passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserSession(BaseModel):
    """User session information"""
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    role: str
    first_name: Optional[str]
    last_name: Optional[str]
    login_time: datetime
    expires_at: datetime
