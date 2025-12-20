"""
Projects Router
Handle project management within tenants
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import uuid
import logging
from datetime import datetime

from app.database import db
from app.models.user import User
from app.models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectStats, ProjectSettings, ProjectHealth, ProjectSummary,
    ProjectExport
)
from app.models.common import APIResponse, PaginatedResponse
from app.dependencies import (
    get_current_user, get_current_tenant, Timer, check_tenant_limits
)
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)
router = APIRouter()
project_service = ProjectService()


@router.post("/", response_model=APIResponse)
async def create_project(
    project_data: ProjectCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Create a new project"""
    try:
        with Timer("project_creation"):
            # Check tenant limits
            limits_check = await check_tenant_limits(current_tenant['id'])
            if limits_check['limits']['project_count']['exceeded']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Project limit exceeded for your plan"
                )
            
            # Create project
            project_id = str(uuid.uuid4())
            
            await db.execute("""
                INSERT INTO projects (
                    id, tenant_id, name, description, settings
                ) VALUES ($1, $2, $3, $4, $5)
            """, 
            project_id,
            current_tenant['id'],
            project_data.name,
            project_data.description,
            project_data.settings or {}
            )
            
            # Log project creation
            background_tasks.add_task(
                logger.info, 
                f"Project created: {project_data.name} ({project_id}) by {current_user.email}"
            )
            
            return APIResponse(
                message="Project created successfully",
                data={"project_id": project_id}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.get("/", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """List projects for current tenant"""
    try:
        with Timer("project_listing"):
            # Build query conditions
            conditions = ["tenant_id = $1"]
            params = [current_tenant['id']]
            param_count = 1
            
            if search:
                param_count += 1
                conditions.append(f"(name ILIKE ${param_count} OR description ILIKE ${param_count})")
                params.append(f"%{search}%")
            
            where_clause = f"WHERE {' AND '.join(conditions)}"
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM projects {where_clause}"
            total = await db.fetchval(count_query, *params)
            
            # Get projects with pagination
            offset = (page - 1) * per_page
            param_count += 1
            params.append(per_page)
            param_count += 1
            params.append(offset)
            
            query = f"""
                SELECT * FROM projects 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_count-1} OFFSET ${param_count}
            """
            
            projects = await db.fetch(query, *params)
            
            # Convert to response models
            project_list = [ProjectResponse(**dict(project)) for project in projects]
            
            # Calculate pagination
            pages = (total + per_page - 1) // per_page
            
            return PaginatedResponse(
                items=project_list,
                total=total,
                page=page,
                per_page=per_page,
                pages=pages,
                has_next=page < pages,
                has_prev=page > 1
            )
            
    except Exception as e:
        logger.error(f"List projects error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch projects"
        )


@router.get("/{project_id}", response_model=APIResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get a specific project"""
    try:
        with Timer("project_retrieval"):
            result = await db.fetchrow(
                "SELECT * FROM projects WHERE id = $1 AND tenant_id = $2",
                project_id,
                current_tenant['id']
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Get additional project statistics
            stats = await project_service.get_project_stats(project_id, current_tenant['id'])
            health = await project_service.get_project_health(project_id, current_tenant['id'])
            
            return APIResponse(
                data={
                    "project": ProjectResponse(**dict(result)),
                    "stats": stats,
                    "health": health
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch project"
        )


@router.put("/{project_id}", response_model=APIResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Update a project"""
    try:
        # Verify project belongs to tenant
        project = await db.fetchrow(
            "SELECT id FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0
        
        update_data = project_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
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
        params.append(project_id)
        param_count += 1
        params.append(current_tenant['id'])
        
        query = f"""
            UPDATE projects 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${param_count-1} AND tenant_id = ${param_count}
            RETURNING *
        """
        
        result = await db.fetchrow(query, *params)
        
        if not result:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Log project update
        background_tasks.add_task(
            logger.info, 
            f"Project updated: {project_id} by {current_user.email}"
        )
        
        return APIResponse(
            message="Project updated successfully",
            data=ProjectResponse(**dict(result))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )


@router.delete("/{project_id}", response_model=APIResponse)
async def delete_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Delete a project and all its memories"""
    try:
        # Verify project belongs to tenant
        project = await db.fetchrow(
            "SELECT id, name FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Delete all memories in the project first
        await db.execute(
            "DELETE FROM memories WHERE project_id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        # Delete learning events related to the project
        await db.execute("""
            DELETE FROM learning_events 
            WHERE tenant_id = $1 
            AND memory_id IN (SELECT id FROM memories WHERE project_id = $2)
        """, current_tenant['id'], project_id)
        
        # Delete the project
        result = await db.execute(
            "DELETE FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Log project deletion
        background_tasks.add_task(
            logger.info, 
            f"Project deleted: {project['name']} ({project_id}) by {current_user.email}"
        )
        
        return APIResponse(message="Project deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )


@router.get("/{project_id}/stats", response_model=APIResponse)
async def get_project_statistics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get project statistics"""
    try:
        # Verify project belongs to tenant
        project = await db.fetchrow(
            "SELECT id FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        stats = await project_service.get_project_stats(project_id, current_tenant['id'])
        
        return APIResponse(data=stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch project statistics"
        )


@router.get("/{project_id}/health", response_model=APIResponse)
async def get_project_health(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get project health status"""
    try:
        # Verify project belongs to tenant
        project = await db.fetchrow(
            "SELECT id FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        health = await project_service.get_project_health(project_id, current_tenant['id'])
        
        return APIResponse(data=health)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project health error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch project health"
        )


@router.get("/{project_id}/export", response_model=APIResponse)
async def export_project_data(
    project_id: str,
    export_config: ProjectExport,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Export project data"""
    try:
        # Verify project belongs to tenant
        project = await db.fetchrow(
            "SELECT id, name FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Start export process in background
        background_tasks.add_task(
            project_service.export_project_data,
            project_id,
            current_tenant['id'],
            export_config,
            current_user.email
        )
        
        return APIResponse(
            message="Export started. You will receive an email when it's ready.",
            data={
                "project_name": project['name'],
                "export_format": export_config.format,
                "estimated_completion": "5-10 minutes"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export project error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start project export"
        )


@router.get("/{project_id}/settings", response_model=APIResponse)
async def get_project_settings(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get project settings"""
    try:
        result = await db.fetchrow(
            "SELECT settings FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        settings = ProjectSettings(**result['settings'])
        
        return APIResponse(data=settings)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get project settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch project settings"
        )


@router.put("/{project_id}/settings", response_model=APIResponse)
async def update_project_settings(
    project_id: str,
    settings_update: ProjectSettings,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Update project settings"""
    try:
        # Verify project belongs to tenant
        project = await db.fetchrow(
            "SELECT id FROM projects WHERE id = $1 AND tenant_id = $2",
            project_id,
            current_tenant['id']
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Update settings
        await db.execute(
            "UPDATE projects SET settings = $1, updated_at = NOW() WHERE id = $2 AND tenant_id = $3",
            settings_update.dict(),
            project_id,
            current_tenant['id']
        )
        
        return APIResponse(message="Project settings updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update project settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project settings"
        )


@router.get("/summary/list", response_model=List[ProjectSummary])
async def get_projects_summary(
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get summary of all projects for quick overview"""
    try:
        projects = await db.fetch("""
            SELECT 
                p.id,
                p.name,
                p.description,
                p.memory_count,
                p.created_at,
                p.updated_at,
                MAX(m.last_accessed) as last_activity
            FROM projects p
            LEFT JOIN memories m ON p.id = m.project_id
            WHERE p.tenant_id = $1
            GROUP BY p.id, p.name, p.description, p.memory_count, p.created_at, p.updated_at
            ORDER BY p.updated_at DESC
        """, current_tenant['id'])
        
        # Determine health status for each project
        summaries = []
        for project in projects:
            # Simple health calculation based on recent activity
            last_activity = project['last_activity']
            if last_activity and (datetime.now() - last_activity).days < 7:
                health_status = "healthy"
            elif project['memory_count'] > 0:
                health_status = "degraded"
            else:
                health_status = "unhealthy"
            
            summaries.append(ProjectSummary(
                id=project['id'],
                name=project['name'],
                description=project['description'],
                memory_count=project['memory_count'],
                last_activity=last_activity,
                health_status=health_status
            ))
        
        return summaries
        
    except Exception as e:
        logger.error(f"Get projects summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch projects summary"
        )
