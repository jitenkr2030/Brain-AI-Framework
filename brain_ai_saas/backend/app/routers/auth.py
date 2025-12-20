"""
Authentication Router
Handle user authentication, registration, and token management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import EmailStr
from datetime import datetime, timedelta
import secrets
import logging

from app.database import db
from app.models.user import (
    User, UserCreate, UserUpdate, UserLogin, UserResponse, 
    UserProfile, PasswordChange, PasswordReset, PasswordResetConfirm,
    TokenData, UserSession
)
from app.models.common import APIResponse
from app.dependencies import (
    get_current_user, get_password_hash, verify_password, 
    create_access_token, verify_token, get_redis_client
)
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=APIResponse)
async def register_user(user_data: UserCreate, background_tasks: BackgroundTasks):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            user_data.email
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Check if tenant exists and is active
        tenant = await db.fetchrow(
            "SELECT id, status FROM tenants WHERE id = $1",
            user_data.tenant_id
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        if tenant['status'] != 'active':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant is not active"
            )
        
        # Create user
        user_id = secrets.token_hex(16)
        password_hash = get_password_hash(user_data.password)
        
        await db.execute("""
            INSERT INTO users (
                id, tenant_id, email, password_hash, 
                first_name, last_name, role
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, 
        user_id, 
        user_data.tenant_id,
        user_data.email,
        password_hash,
        user_data.first_name,
        user_data.last_name,
        user_data.role
        )
        
        # Log registration
        background_tasks.add_task(
            logger.info, 
            f"User registered: {user_data.email} for tenant {user_data.tenant_id}"
        )
        
        return APIResponse(
            message="User registered successfully",
            data={"user_id": user_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=APIResponse)
async def login_user(login_data: UserLogin, background_tasks: BackgroundTasks):
    """Authenticate user and return access token"""
    try:
        # Find user
        user = await db.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND is_active = true",
            login_data.email
        )
        
        if not user or not verify_password(login_data.password, user['password_hash']):
            background_tasks.add_task(
                logger.warning, 
                f"Failed login attempt for email: {login_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get tenant info
        tenant = await db.fetchrow(
            "SELECT * FROM tenants WHERE id = $1 AND status = 'active'",
            user['tenant_id']
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant is not active"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user['id']),
                "tenant_id": str(user['tenant_id']),
                "role": user['role'],
                "email": user['email']
            },
            expires_delta=access_token_expires
        )
        
        # Update last login
        await db.execute(
            "UPDATE users SET last_login = NOW() WHERE id = $1",
            user['id']
        )
        
        # Store session in Redis
        redis_client = get_redis_client()
        session_data = {
            "user_id": str(user['id']),
            "tenant_id": str(user['tenant_id']),
            "email": user['email'],
            "role": user['role'],
            "login_time": datetime.utcnow().isoformat()
        }
        
        session_key = f"session:{access_token}"
        if login_data.remember_me:
            redis_client.setex(session_key, 30*24*60*60, str(session_data))  # 30 days
        else:
            redis_client.setex(session_key, access_token_expires.total_seconds(), str(session_data))
        
        # Log successful login
        background_tasks.add_task(
            logger.info, 
            f"User logged in: {user['email']} from tenant {user['tenant_id']}"
        )
        
        return APIResponse(
            message="Login successful",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": access_token_expires.total_seconds(),
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "role": user['role'],
                    "tenant_id": user['tenant_id']
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout", response_model=APIResponse)
async def logout_user(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user and invalidate token"""
    try:
        # Remove session from Redis
        redis_client = get_redis_client()
        session_key = f"session:{credentials.credentials}"
        redis_client.delete(session_key)
        
        return APIResponse(message="Logout successful")
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=APIResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    try:
        # Get tenant info
        tenant = await db.fetchrow(
            "SELECT name, plan FROM tenants WHERE id = $1",
            current_user.tenant_id
        )
        
        profile = UserProfile(
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            full_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip(),
            role=current_user.role,
            tenant_name=tenant['name'] if tenant else "Unknown",
            tenant_plan=tenant['plan'] if tenant else "free"
        )
        
        return APIResponse(data=profile)
        
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )


@router.put("/me", response_model=APIResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in user_update.dict(exclude_unset=True).items():
            param_count += 1
            update_fields.append(f"{field} = ${param_count}")
            params.append(value)
        
        if not update_fields:
            return APIResponse(message="No changes to update")
        
        param_count += 1
        params.append(current_user.id)
        
        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${param_count}
            RETURNING *
        """
        
        result = await db.fetchrow(query, *params)
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        return APIResponse(
            message="Profile updated successfully",
            data=UserResponse(**dict(result))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Verify current password
        user = await db.fetchrow(
            "SELECT password_hash FROM users WHERE id = $1",
            current_user.id
        )
        
        if not user or not verify_password(password_data.current_password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        new_password_hash = get_password_hash(password_data.new_password)
        
        await db.execute(
            "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
            new_password_hash,
            current_user.id
        )
        
        return APIResponse(message="Password changed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(reset_data: PasswordReset, background_tasks: BackgroundTasks):
    """Request password reset"""
    try:
        # Check if user exists
        user = await db.fetchrow(
            "SELECT id, email FROM users WHERE email = $1 AND is_active = true",
            reset_data.email
        )
        
        # Always return success to prevent email enumeration
        if user:
            # Generate reset token (in production, use secure token generation)
            reset_token = secrets.token_urlsafe(32)
            
            # Store reset token (expires in 1 hour)
            redis_client = get_redis_client()
            redis_client.setex(f"reset_token:{reset_token}", 3600, str(user['id']))
            
            # In production, send email with reset link
            background_tasks.add_task(
                logger.info, 
                f"Password reset requested for: {reset_data.email}"
            )
        
        return APIResponse(
            message="If the email exists, password reset instructions have been sent"
        )
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return APIResponse(
            message="If the email exists, password reset instructions have been sent"
        )


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(reset_data: PasswordResetConfirm):
    """Reset password using token"""
    try:
        # Verify reset token
        redis_client = get_redis_client()
        user_id = redis_client.get(f"reset_token:{reset_data.token}")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password
        new_password_hash = get_password_hash(reset_data.new_password)
        
        await db.execute(
            "UPDATE users SET password_hash = $1, updated_at = NOW() WHERE id = $2",
            new_password_hash,
            user_id
        )
        
        # Remove reset token
        redis_client.delete(f"reset_token:{reset_data.token}")
        
        return APIResponse(message="Password reset successful")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.get("/verify-token")
async def verify_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if current token is valid"""
    try:
        payload = verify_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {"valid": True, "user_id": payload.get("sub")}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )


@router.get("/refresh-token")
async def refresh_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token"""
    try:
        # Verify current token
        payload = verify_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_token = create_access_token(
            data=payload,
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": access_token_expires.total_seconds()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
