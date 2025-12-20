"""
Tenants Router
Handle tenant management, creation, and configuration
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import EmailStr
import secrets
import logging
import uuid

from app.database import db
from app.models.tenant import (
    Tenant, TenantCreate, TenantUpdate, TenantResponse, 
    TenantStats, TenantUsage, TenantLimits
)
from app.models.user import User, UserCreate
from app.models.common import APIResponse, PaginatedResponse
from app.dependencies import get_current_user, get_admin_user, get_current_tenant, Timer
from app.models.subscription import PLANS

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=APIResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(get_admin_user)
):
    """Create a new tenant (admin only)"""
    try:
        with Timer("tenant_creation"):
            # Generate unique API key
            api_key = f"ba_{secrets.token_urlsafe(32)}"
            
            # Create tenant
            tenant_id = str(uuid.uuid4())
            
            await db.execute("""
                INSERT INTO tenants (
                    id, name, slug, plan, api_key, status, settings
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
            tenant_id,
            tenant_data.name,
            tenant_data.slug,
            tenant_data.plan,
            api_key,
            "active",
            tenant_data.settings or {}
            )
            
            # Create default admin user for tenant
            admin_user_id = str(uuid.uuid4())
            from app.dependencies import get_password_hash
            
            await db.execute("""
                INSERT INTO users (
                    id, tenant_id, email, password_hash, role, first_name, last_name
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            admin_user_id,
            tenant_id,
            tenant_data.email,
            get_password_hash(secrets.token_urlsafe(16)),  # Temporary password
            "admin",
            "Admin",
            "User"
            )
            
            # Create default subscription
            await db.execute("""
                INSERT INTO subscriptions (
                    tenant_id, plan, status
                ) VALUES ($1, $2, $3)
            """,
            tenant_id,
            tenant_data.plan,
            "active"
            )
            
            # Log tenant creation
            background_tasks.add_task(
                logger.info, 
                f"Tenant created: {tenant_data.name} ({tenant_id}) by admin {admin_user.email}"
            )
            
            return APIResponse(
                message="Tenant created successfully",
                data={
                    "tenant_id": tenant_id,
                    "api_key": api_key,
                    "admin_user_id": admin_user_id
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tenant creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tenant"
        )


@router.get("/me", response_model=APIResponse)
async def get_current_tenant_info(current_tenant: Dict[str, Any] = Depends(get_current_tenant)):
    """Get current tenant information"""
    try:
        tenant_response = TenantResponse(**current_tenant)
        
        # Get additional stats
        stats = await get_tenant_stats(current_tenant['id'])
        
        return APIResponse(
            data={
                "tenant": tenant_response,
                "stats": stats
            }
        )
        
    except Exception as e:
        logger.error(f"Get tenant info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tenant information"
        )


@router.put("/me", response_model=APIResponse)
async def update_current_tenant(
    tenant_update: TenantUpdate,
    current_tenant: Dict[str, Any] = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user)
):
    """Update current tenant (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0
        
        for field, value in tenant_update.dict(exclude_unset=True).items():
            param_count += 1
            if field == "settings":
                update_fields.append(f"{field} = ${param_count}")
                params.append(value or {})
            else:
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not update_fields:
            return APIResponse(message="No changes to update")
        
        param_count += 1
        params.append(current_tenant['id'])
        
        query = f"""
            UPDATE tenants 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${param_count}
            RETURNING *
        """
        
        result = await db.fetchrow(query, *params)
        
        if not result:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # If plan changed, update subscription
        if tenant_update.plan:
            await db.execute("""
                UPDATE subscriptions 
                SET plan = $1, updated_at = NOW() 
                WHERE tenant_id = $2
            """, tenant_update.plan, current_tenant['id'])
        
        return APIResponse(
            message="Tenant updated successfully",
            data=TenantResponse(**dict(result))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tenant update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant"
        )


@router.get("/", response_model=PaginatedResponse[TenantResponse])
async def list_tenants(
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    plan: Optional[str] = None,
    status: Optional[str] = None,
    admin_user: User = Depends(get_admin_user)
):
    """List all tenants (admin only)"""
    try:
        # Build query conditions
        conditions = []
        params = []
        param_count = 0
        
        if search:
            param_count += 1
            conditions.append(f"(name ILIKE ${param_count} OR slug ILIKE ${param_count})")
            params.append(f"%{search}%")
        
        if plan:
            param_count += 1
            conditions.append(f"plan = ${param_count}")
            params.append(plan)
        
        if status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(status)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM tenants {where_clause}"
        total = await db.fetchval(count_query, *params)
        
        # Get tenants with pagination
        offset = (page - 1) * per_page
        param_count += 1
        params.append(per_page)
        param_count += 1
        params.append(offset)
        
        query = f"""
            SELECT * FROM tenants 
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_count-1} OFFSET ${param_count}
        """
        
        tenants = await db.fetch(query, *params)
        
        # Convert to response models
        tenant_list = [TenantResponse(**dict(tenant)) for tenant in tenants]
        
        # Calculate pagination
        pages = (total + per_page - 1) // per_page
        
        return PaginatedResponse(
            items=tenant_list,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )
        
    except Exception as e:
        logger.error(f"List tenants error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tenants"
        )


@router.get("/{tenant_id}", response_model=APIResponse)
async def get_tenant(
    tenant_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Get tenant by ID (admin only)"""
    try:
        tenant = await db.fetchrow(
            "SELECT * FROM tenants WHERE id = $1",
            tenant_id
        )
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Get additional information
        stats = await get_tenant_stats(tenant_id)
        usage = await get_tenant_usage(tenant_id)
        
        return APIResponse(
            data={
                "tenant": TenantResponse(**dict(tenant)),
                "stats": stats,
                "usage": usage
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tenant error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tenant"
        )


@router.delete("/{tenant_id}", response_model=APIResponse)
async def delete_tenant(
    tenant_id: str,
    background_tasks: BackgroundTasks,
    admin_user: User = Depends(get_admin_user)
):
    """Delete tenant (admin only) - soft delete by changing status"""
    try:
        # Check if tenant exists
        tenant = await db.fetchrow(
            "SELECT name FROM tenants WHERE id = $1",
            tenant_id
        )
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Soft delete by setting status to cancelled
        await db.execute(
            "UPDATE tenants SET status = 'cancelled', updated_at = NOW() WHERE id = $1",
            tenant_id
        )
        
        # Cancel subscription
        await db.execute(
            "UPDATE subscriptions SET status = 'cancelled', updated_at = NOW() WHERE tenant_id = $1",
            tenant_id
        )
        
        # Log deletion
        background_tasks.add_task(
            logger.info, 
            f"Tenant deleted: {tenant['name']} ({tenant_id}) by admin {admin_user.email}"
        )
        
        return APIResponse(message="Tenant deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete tenant error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tenant"
        )


@router.get("/{tenant_id}/stats", response_model=APIResponse)
async def get_tenant_statistics(
    tenant_id: str,
    current_tenant: Dict[str, Any] = Depends(get_current_tenant),
    admin_user: User = Depends(get_admin_user)
):
    """Get tenant statistics"""
    try:
        # Users can only view their own stats unless they're admin
        if current_tenant['id'] != tenant_id and admin_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        stats = await get_tenant_stats(tenant_id)
        
        return APIResponse(data=stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tenant stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tenant statistics"
        )


@router.get("/{tenant_id}/usage", response_model=APIResponse)
async def get_tenant_usage_info(
    tenant_id: str,
    current_tenant: Dict[str, Any] = Depends(get_current_tenant),
    admin_user: User = Depends(get_admin_user)
):
    """Get tenant usage information"""
    try:
        # Users can only view their own usage unless they're admin
        if current_tenant['id'] != tenant_id and admin_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        usage = await get_tenant_usage(tenant_id)
        
        return APIResponse(data=usage)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tenant usage error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tenant usage"
        )


@router.get("/{tenant_id}/limits", response_model=APIResponse)
async def get_tenant_limits(
    tenant_id: str,
    current_tenant: Dict[str, Any] = Depends(get_current_tenant),
    admin_user: User = Depends(get_admin_user)
):
    """Get tenant plan limits"""
    try:
        # Users can only view their own limits unless they're admin
        if current_tenant['id'] != tenant_id and admin_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get tenant plan
        tenant = await db.fetchrow(
            "SELECT plan FROM tenants WHERE id = $1",
            tenant_id
        )
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Get plan limits
        plan_limits = PLANS.get(tenant['plan'])
        
        if not plan_limits:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        return APIResponse(data=plan_limits)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tenant limits error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tenant limits"
        )


# Helper functions
async def get_tenant_stats(tenant_id: str) -> TenantStats:
    """Get comprehensive tenant statistics"""
    try:
        # Get basic counts
        stats = await db.fetchrow("""
            SELECT 
                COUNT(DISTINCT p.id) as total_projects,
                COUNT(DISTINCT m.id) as total_memories,
                COUNT(DISTINCT au.id) as total_api_calls
            FROM tenants t
            LEFT JOIN projects p ON t.id = p.tenant_id
            LEFT JOIN memories m ON p.id = m.project_id
            LEFT JOIN api_usage au ON t.id = au.tenant_id
            WHERE t.id = $1
            GROUP BY t.id
        """, tenant_id)
        
        if not stats:
            return TenantStats(
                total_projects=0,
                total_memories=0,
                total_api_calls=0
            )
        
        # Get plan limits
        tenant = await db.fetchrow("SELECT plan FROM tenants WHERE id = $1", tenant_id)
        plan_limits = PLANS.get(tenant['plan']) if tenant else None
        
        return TenantStats(
            total_projects=stats['total_projects'],
            total_memories=stats['total_memories'],
            total_api_calls=stats['total_api_calls'],
            plan_limit_projects=plan_limits.max_projects if plan_limits else None,
            plan_limit_memories=plan_limits.max_memories if plan_limits else None,
            plan_limit_api_calls=plan_limits.max_api_calls_per_month if plan_limits else None
        )
        
    except Exception as e:
        logger.error(f"Get tenant stats error: {e}")
        raise


async def get_tenant_usage(tenant_id: str) -> TenantUsage:
    """Get tenant usage for current period"""
    try:
        # Get current month usage
        usage = await db.fetchrow("""
            SELECT 
                COUNT(DISTINCT p.id) as project_count,
                COUNT(DISTINCT m.id) as memory_count,
                COUNT(DISTINCT au.id) as api_call_count
            FROM tenants t
            LEFT JOIN projects p ON t.id = p.tenant_id
            LEFT JOIN memories m ON p.id = m.project_id
            LEFT JOIN api_usage au ON t.id = au.tenant_id 
                AND au.created_at >= DATE_TRUNC('month', NOW())
            WHERE t.id = $1
            GROUP BY t.id
        """, tenant_id)
        
        if not usage:
            return TenantUsage(
                project_count=0,
                memory_count=0,
                api_call_count=0,
                storage_used_mb=0.0,
                bandwidth_used_mb=0.0,
                period_start=datetime.now().replace(day=1),
                period_end=datetime.now()
            )
        
        # Calculate storage and bandwidth (simplified calculation)
        storage_used_mb = usage['memory_count'] * 0.001  # Rough estimate
        bandwidth_used_mb = usage['api_call_count'] * 0.01  # Rough estimate
        
        # Get period dates
        period_start = datetime.now().replace(day=1)
        period_end = datetime.now()
        
        return TenantUsage(
            project_count=usage['project_count'],
            memory_count=usage['memory_count'],
            api_call_count=usage['api_call_count'],
            storage_used_mb=storage_used_mb,
            bandwidth_used_mb=bandwidth_used_mb,
            period_start=period_start,
            period_end=period_end
        )
        
    except Exception as e:
        logger.error(f"Get tenant usage error: {e}")
        raise
