"""
Reasoning Router
Handle Brain AI reasoning engine and query processing
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import uuid
import json
import logging
from datetime import datetime

from app.database import db
from app.models.user import User
from app.models.common import APIResponse, PaginatedResponse
from app.dependencies import (
    get_current_user, get_current_tenant, Timer, check_tenant_limits
)
from app.services.reasoning_service import ReasoningService

logger = logging.getLogger(__name__)
router = APIRouter()
reasoning_service = ReasoningService()


@router.post("/query", response_model=APIResponse)
async def process_reasoning_query(
    query: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Process a reasoning query"""
    try:
        with Timer("reasoning_query"):
            # Verify project belongs to tenant
            project_id = query.get("project_id")
            if project_id:
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
            
            # Process query with reasoning service
            result = await reasoning_service.process_query(
                query,
                current_tenant['id'],
                project_id
            )
            
            # Log query for analytics
            background_tasks.add_task(
                reasoning_service.log_query,
                query,
                result,
                current_tenant['id']
            )
            
            return APIResponse(
                data=result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reasoning query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process reasoning query"
        )


@router.post("/batch", response_model=APIResponse)
async def process_batch_queries(
    queries: List[Dict[str, Any]],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Process multiple reasoning queries in batch"""
    try:
        with Timer("batch_reasoning"):
            results = []
            
            for i, query in enumerate(queries):
                try:
                    # Verify project if specified
                    project_id = query.get("project_id")
                    if project_id:
                        project = await db.fetchrow(
                            "SELECT id FROM projects WHERE id = $1 AND tenant_id = $2",
                            project_id,
                            current_tenant['id']
                        )
                        
                        if not project:
                            results.append({
                                "index": i,
                                "error": "Project not found",
                                "success": False
                            })
                            continue
                    
                    # Process query
                    result = await reasoning_service.process_query(
                        query,
                        current_tenant['id'],
                        project_id
                    )
                    
                    results.append({
                        "index": i,
                        "result": result,
                        "success": True
                    })
                    
                except Exception as e:
                    results.append({
                        "index": i,
                        "error": str(e),
                        "success": False
                    })
            
            # Log batch processing
            background_tasks.add_task(
                reasoning_service.log_batch_queries,
                queries,
                results,
                current_tenant['id']
            )
            
            successful = len([r for r in results if r.get("success")])
            
            return APIResponse(
                message=f"Batch processing completed: {successful}/{len(queries)} queries successful",
                data={
                    "results": results,
                    "successful": successful,
                    "total": len(queries)
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch reasoning error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process batch queries"
        )


@router.get("/context/{project_id}", response_model=APIResponse)
async def get_reasoning_context(
    project_id: str,
    query: Optional[str] = None,
    memory_types: Optional[List[str]] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get relevant context for reasoning"""
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
        
        # Get relevant memories for context
        context = await reasoning_service.get_relevant_context(
            project_id,
            current_tenant['id'],
            query,
            memory_types,
            limit
        )
        
        return APIResponse(data=context)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reasoning context error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reasoning context"
        )


@router.get("/explanations/{query_id}", response_model=APIResponse)
async def get_reasoning_explanation(
    query_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get explanation for a reasoning query"""
    try:
        # Verify query belongs to tenant
        explanation = await reasoning_service.get_explanation(
            query_id,
            current_tenant['id']
        )
        
        if not explanation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query explanation not found"
            )
        
        return APIResponse(data=explanation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reasoning explanation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reasoning explanation"
        )


@router.get("/history/{project_id}", response_model=PaginatedResponse[Dict[str, Any]])
async def get_reasoning_history(
    project_id: str,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get reasoning query history for a project"""
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
        
        # Get query history (stored in learning_events table)
        offset = (page - 1) * per_page
        
        # Get total count
        total = await db.fetchval("""
            SELECT COUNT(*)
            FROM learning_events 
            WHERE tenant_id = $1 
            AND event_type = 'reasoning_query'
            AND metadata->>'project_id' = $2
        """, current_tenant['id'], project_id)
        
        # Get history items
        history_items = await db.fetch("""
            SELECT * FROM learning_events 
            WHERE tenant_id = $1 
            AND event_type = 'reasoning_query'
            AND metadata->>'project_id' = $2
            ORDER BY created_at DESC
            LIMIT $3 OFFSET $4
        """, current_tenant['id'], project_id, per_page, offset)
        
        # Format history items
        formatted_history = []
        for item in history_items:
            metadata = json.loads(item['metadata'] or '{}')
            formatted_history.append({
                "id": item['id'],
                "query": metadata.get('query', ''),
                "response": metadata.get('response', ''),
                "confidence": item['confidence'],
                "processing_time_ms": metadata.get('processing_time_ms', 0),
                "memories_used": metadata.get('memories_used', []),
                "created_at": item['created_at']
            })
        
        # Calculate pagination
        pages = (total + per_page - 1) // per_page
        
        return PaginatedResponse(
            items=formatted_history,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reasoning history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reasoning history"
        )


@router.get("/analytics/{project_id}", response_model=APIResponse)
async def get_reasoning_analytics(
    project_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get reasoning analytics for a project"""
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
        
        analytics = await reasoning_service.get_analytics(
            project_id,
            current_tenant['id'],
            days
        )
        
        return APIResponse(data=analytics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reasoning analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reasoning analytics"
        )


@router.get("/performance/{project_id}", response_model=APIResponse)
async def get_reasoning_performance(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get reasoning performance metrics"""
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
        
        performance = await reasoning_service.get_performance_metrics(
            project_id,
            current_tenant['id']
        )
        
        return APIResponse(data=performance)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get reasoning performance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reasoning performance metrics"
        )


@router.post("/feedback", response_model=APIResponse)
async def submit_reasoning_feedback(
    feedback: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Submit feedback on reasoning results"""
    try:
        query_id = feedback.get("query_id")
        rating = feedback.get("rating")
        comment = feedback.get("comment")
        
        if not query_id or rating is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query ID and rating are required"
            )
        
        # Verify query belongs to tenant
        query_exists = await db.fetchrow("""
            SELECT id FROM learning_events 
            WHERE id = $1 AND tenant_id = $2 AND event_type = 'reasoning_query'
        """, query_id, current_tenant['id'])
        
        if not query_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )
        
        # Store feedback
        await db.execute("""
            INSERT INTO learning_events (
                id, tenant_id, event_type, metadata
            ) VALUES ($1, $2, $3, $4)
        """,
        str(uuid.uuid4()),
        current_tenant['id'],
        "reasoning_feedback",
        json.dumps({
            "query_id": query_id,
            "rating": rating,
            "comment": comment,
            "user_id": str(current_user.id)
        })
        )
        
        # Update reasoning performance tracking
        background_tasks.add_task(
            reasoning_service.update_feedback_metrics,
            query_id,
            rating,
            current_tenant['id']
        )
        
        return APIResponse(message="Feedback submitted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit reasoning feedback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit reasoning feedback"
        )


@router.get("/health", response_model=APIResponse)
async def get_reasoning_system_health(
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get reasoning system health status"""
    try:
        health = await reasoning_service.get_system_health(current_tenant['id'])
        
        return APIResponse(data=health)
        
    except Exception as e:
        logger.error(f"Get reasoning health error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get reasoning system health"
        )
