"""
Memories Router
Handle Brain AI memory management, storage, retrieval, and search
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import uuid
import json
import logging
from datetime import datetime

from app.database import db
from app.models.memory import (
    Memory, MemoryCreate, MemoryUpdate, MemoryResponse, 
    MemoryQuery, MemorySearchResult, MemoryBatchCreate,
    MemoryStats, MemoryAnalytics, MemoryExport, MemorySuggestion,
    MemoryPattern, MemoryHealth
)
from app.models.user import User
from app.models.project import Project
from app.models.common import APIResponse, PaginatedResponse
from app.dependencies import (
    get_current_user, get_current_tenant, Timer, check_tenant_limits,
    metrics
)
from app.services.memory_service import MemoryService

logger = logging.getLogger(__name__)
router = APIRouter()
memory_service = MemoryService()


@router.post("/", response_model=APIResponse)
async def create_memory(
    memory_data: MemoryCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Create a new memory"""
    try:
        with Timer("memory_creation"):
            # Verify project belongs to tenant
            project = await db.fetchrow(
                "SELECT id FROM projects WHERE id = $1 AND tenant_id = $2",
                memory_data.project_id,
                current_tenant['id']
            )
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            
            # Check tenant limits
            limits_check = await check_tenant_limits(current_tenant['id'])
            if limits_check['limits']['memory_count']['exceeded']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Memory limit exceeded for your plan"
                )
            
            # Create memory
            memory_id = str(uuid.uuid4())
            
            await db.execute("""
                INSERT INTO memories (
                    id, tenant_id, project_id, pattern_signature, memory_type,
                    content, context, strength, tags, confidence
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, 
            memory_id,
            current_tenant['id'],
            memory_data.project_id,
            memory_data.pattern_signature,
            memory_data.memory_type,
            json.dumps(memory_data.content),
            json.dumps(memory_data.context or {}),
            memory_data.strength,
            memory_data.tags,
            memory_data.confidence
            )
            
            # Update project memory count
            await db.execute(
                "UPDATE projects SET memory_count = memory_count + 1 WHERE id = $1",
                memory_data.project_id
            )
            
            # Create learning event for new memory
            await db.execute("""
                INSERT INTO learning_events (
                    id, tenant_id, memory_id, event_type, metadata
                ) VALUES ($1, $2, $3, $4, $5)
            """,
            str(uuid.uuid4()),
            current_tenant['id'],
            memory_id,
            "memory_created",
            json.dumps({"pattern_signature": memory_data.pattern_signature})
            )
            
            # Vector embedding (if enabled)
            if memory_service.vector_db_enabled:
                background_tasks.add_task(
                    memory_service.store_embedding,
                    memory_id,
                    memory_data.content,
                    memory_data.memory_type
                )
            
            # Log memory creation
            background_tasks.add_task(
                logger.info, 
                f"Memory created: {memory_data.pattern_signature} in project {memory_data.project_id}"
            )
            
            return APIResponse(
                message="Memory created successfully",
                data={"memory_id": memory_id}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memory creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create memory"
        )


@router.get("/project/{project_id}", response_model=PaginatedResponse[MemoryResponse])
async def get_project_memories(
    project_id: str,
    memory_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    min_strength: float = 0.0,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get memories for a project"""
    try:
        with Timer("memory_retrieval"):
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
            
            # Build query
            query = """
                SELECT * FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
            """
            params = [current_tenant['id'], project_id]
            param_count = 2
            
            if memory_type:
                param_count += 1
                query += f" AND memory_type = ${param_count}"
                params.append(memory_type)
            
            if tags:
                param_count += 1
                query += f" AND tags && ${param_count}"
                params.append(tags)
            
            if min_strength > 0:
                param_count += 1
                query += f" AND strength >= ${param_count}"
                params.append(min_strength)
            
            # Add pagination
            param_count += 1
            params.append(limit)
            param_count += 1
            params.append(offset)
            
            query += f" ORDER BY strength DESC, created_at DESC LIMIT ${param_count-1} OFFSET ${param_count}"
            
            # Get total count
            count_query = query.replace("SELECT *", "SELECT COUNT(*)").split("ORDER BY")[0]
            total = await db.fetchval(count_query, *params[:-2])
            
            # Get memories
            results = await db.fetch(query, *params)
            
            # Convert to response models
            memories = []
            for row in results:
                # Update access count
                await db.execute(
                    "UPDATE memories SET access_count = access_count + 1, last_accessed = NOW() WHERE id = $1",
                    row['id']
                )
                
                memories.append(MemoryResponse(
                    id=row['id'],
                    pattern_signature=row['pattern_signature'],
                    memory_type=row['memory_type'],
                    content=json.loads(row['content']),
                    context=json.loads(row['context']),
                    strength=row['strength'],
                    access_count=row['access_count'] + 1,  # Include the increment
                    tags=row['tags'],
                    confidence=row['confidence'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ))
            
            # Calculate pagination
            pages = (total + limit - 1) // limit
            
            return PaginatedResponse(
                items=memories,
                total=total,
                page=(offset // limit) + 1,
                per_page=limit,
                pages=pages,
                has_next=offset + limit < total,
                has_prev=offset > 0
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get memories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch memories"
        )


@router.post("/search", response_model=List[MemorySearchResult])
async def search_memories(
    query: MemoryQuery,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Search memories using semantic similarity"""
    try:
        with Timer("memory_search"):
            # Build search query
            search_query = """
                SELECT * FROM memories 
                WHERE tenant_id = $1
            """
            params = [current_tenant['id']]
            param_count = 1
            
            if query.pattern_signature:
                param_count += 1
                search_query += f" AND pattern_signature ILIKE %{param_count}"
                params.append(f"%{query.pattern_signature}%")
            
            if query.memory_type:
                param_count += 1
                search_query += f" AND memory_type = ${param_count}"
                params.append(query.memory_type)
            
            if query.tags:
                param_count += 1
                search_query += f" AND tags && ${param_count}"
                params.append(query.tags)
            
            search_query += f" AND strength >= ${param_count + 1} ORDER BY strength DESC"
            params.append(query.min_strength)
            
            # Add limit
            if query.limit:
                search_query += f" LIMIT ${param_count + 2}"
                params.append(query.limit)
            
            results = await db.fetch(search_query, *params)
            
            # Vector search if enabled and content-based search
            search_results = []
            if memory_service.vector_db_enabled and query.pattern_signature:
                vector_results = await memory_service.semantic_search(
                    query.pattern_signature,
                    current_tenant['id'],
                    query.limit or 50
                )
                search_results = vector_results
            else:
                # Convert database results to search results
                for row in results:
                    # Update access count
                    await db.execute(
                        "UPDATE memories SET access_count = access_count + 1, last_accessed = NOW() WHERE id = $1",
                        row['id']
                    )
                    
                    search_results.append(MemorySearchResult(
                        memory=MemoryResponse(
                            id=row['id'],
                            pattern_signature=row['pattern_signature'],
                            memory_type=row['memory_type'],
                            content=json.loads(row['content']),
                            context=json.loads(row['context']),
                            strength=row['strength'],
                            access_count=row['access_count'] + 1,
                            tags=row['tags'],
                            confidence=row['confidence'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        ),
                        similarity_score=1.0,  # Exact match
                        matched_fields=["pattern_signature"]
                    ))
            
            return search_results
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search memories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search memories"
        )


@router.get("/{memory_id}", response_model=APIResponse)
async def get_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get a specific memory"""
    try:
        with Timer("memory_retrieval"):
            result = await db.fetchrow(
                "SELECT * FROM memories WHERE id = $1 AND tenant_id = $2",
                memory_id,
                current_tenant['id']
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Memory not found"
                )
            
            # Update access count
            await db.execute(
                "UPDATE memories SET access_count = access_count + 1, last_accessed = NOW() WHERE id = $1",
                memory_id
            )
            
            memory_response = MemoryResponse(
                id=result['id'],
                pattern_signature=result['pattern_signature'],
                memory_type=result['memory_type'],
                content=json.loads(result['content']),
                context=json.loads(result['context']),
                strength=result['strength'],
                access_count=result['access_count'] + 1,
                tags=result['tags'],
                confidence=result['confidence'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
            
            return APIResponse(data=memory_response)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get memory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch memory"
        )


@router.put("/{memory_id}", response_model=APIResponse)
async def update_memory(
    memory_id: str,
    memory_update: MemoryUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Update a memory"""
    try:
        # Verify memory belongs to tenant
        memory = await db.fetchrow(
            "SELECT id, project_id FROM memories WHERE id = $1 AND tenant_id = $2",
            memory_id,
            current_tenant['id']
        )
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found"
            )
        
        # Build update query dynamically
        update_fields = []
        params = []
        param_count = 0
        
        update_data = memory_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            param_count += 1
            if field in ["content", "context"]:
                update_fields.append(f"{field} = ${param_count}")
                params.append(json.dumps(value))
            else:
                update_fields.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not update_fields:
            return APIResponse(message="No changes to update")
        
        param_count += 1
        params.append(memory_id)
        param_count += 1
        params.append(current_tenant['id'])
        
        query = f"""
            UPDATE memories 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE id = ${param_count-1} AND tenant_id = ${param_count}
            RETURNING *
        """
        
        result = await db.fetchrow(query, *params)
        
        if not result:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Create learning event for update
        await db.execute("""
            INSERT INTO learning_events (
                id, tenant_id, memory_id, event_type, metadata
            ) VALUES ($1, $2, $3, $4, $5)
        """,
        str(uuid.uuid4()),
        current_tenant['id'],
        memory_id,
        "memory_updated",
        json.dumps({"updated_fields": list(update_data.keys())})
        )
        
        # Update vector embedding if content changed
        if "content" in update_data and memory_service.vector_db_enabled:
            background_tasks.add_task(
                memory_service.update_embedding,
                memory_id,
                json.loads(result['content']),
                result['memory_type']
            )
        
        return APIResponse(
            message="Memory updated successfully",
            data=MemoryResponse(
                id=result['id'],
                pattern_signature=result['pattern_signature'],
                memory_type=result['memory_type'],
                content=json.loads(result['content']),
                context=json.loads(result['context']),
                strength=result['strength'],
                access_count=result['access_count'],
                tags=result['tags'],
                confidence=result['confidence'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update memory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update memory"
        )


@router.delete("/{memory_id}", response_model=APIResponse)
async def delete_memory(
    memory_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Delete a memory"""
    try:
        # Get memory info before deletion
        memory = await db.fetchrow(
            "SELECT id, project_id FROM memories WHERE id = $1 AND tenant_id = $2",
            memory_id,
            current_tenant['id']
        )
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found"
            )
        
        # Delete memory
        result = await db.execute(
            "DELETE FROM memories WHERE id = $1 AND tenant_id = $2",
            memory_id,
            current_tenant['id']
        )
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Update project memory count
        await db.execute(
            "UPDATE projects SET memory_count = memory_count - 1 WHERE id = $1",
            memory['project_id']
        )
        
        # Create learning event for deletion
        await db.execute("""
            INSERT INTO learning_events (
                id, tenant_id, event_type, metadata
            ) VALUES ($1, $2, $3, $4)
        """,
        str(uuid.uuid4()),
        current_tenant['id'],
        "memory_deleted",
        json.dumps({"memory_id": memory_id})
        )
        
        # Delete vector embedding if enabled
        if memory_service.vector_db_enabled:
            background_tasks.add_task(
                memory_service.delete_embedding,
                memory_id
            )
        
        return APIResponse(message="Memory deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete memory error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete memory"
        )


@router.post("/batch", response_model=APIResponse)
async def create_memory_batch(
    batch_data: MemoryBatchCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Create multiple memories in batch"""
    try:
        with Timer("batch_memory_creation"):
            created_count = 0
            errors = []
            
            for i, memory_data in enumerate(batch_data.memories):
                try:
                    # Verify project belongs to tenant
                    project = await db.fetchrow(
                        "SELECT id FROM projects WHERE id = $1 AND tenant_id = $2",
                        memory_data.project_id,
                        current_tenant['id']
                    )
                    
                    if not project:
                        errors.append(f"Memory {i+1}: Project not found")
                        continue
                    
                    # Create memory
                    memory_id = str(uuid.uuid4())
                    
                    await db.execute("""
                        INSERT INTO memories (
                            id, tenant_id, project_id, pattern_signature, memory_type,
                            content, context, strength, tags, confidence
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """, 
                    memory_id,
                    current_tenant['id'],
                    memory_data.project_id,
                    memory_data.pattern_signature,
                    memory_data.memory_type,
                    json.dumps(memory_data.content),
                    json.dumps(memory_data.context or {}),
                    memory_data.strength,
                    memory_data.tags,
                    memory_data.confidence
                    )
                    
                    # Update project memory count
                    await db.execute(
                        "UPDATE projects SET memory_count = memory_count + 1 WHERE id = $1",
                        memory_data.project_id
                    )
                    
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Memory {i+1}: {str(e)}")
            
            # Log batch creation
            background_tasks.add_task(
                logger.info, 
                f"Batch memory creation: {created_count} memories created, {len(errors)} errors"
            )
            
            return APIResponse(
                message=f"Batch creation completed: {created_count} memories created",
                data={
                    "created_count": created_count,
                    "total_count": len(batch_data.memories),
                    "errors": errors
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch memory creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create memories in batch"
        )


@router.get("/project/{project_id}/stats", response_model=APIResponse)
async def get_project_memory_stats(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get memory statistics for a project"""
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
        
        # Get comprehensive statistics
        stats = await memory_service.get_memory_statistics(project_id, current_tenant['id'])
        
        return APIResponse(data=stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get memory stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch memory statistics"
        )


@router.get("/project/{project_id}/analytics", response_model=APIResponse)
async def get_project_memory_analytics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get memory analytics for a project"""
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
        
        # Get analytics data
        analytics = await memory_service.get_memory_analytics(project_id, current_tenant['id'])
        
        return APIResponse(data=analytics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get memory analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch memory analytics"
        )


@router.get("/health", response_model=APIResponse)
async def get_memory_system_health(
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get memory system health status"""
    try:
        health = await memory_service.get_system_health(current_tenant['id'])
        
        return APIResponse(data=health)
        
    except Exception as e:
        logger.error(f"Get memory health error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch memory system health"
        )
