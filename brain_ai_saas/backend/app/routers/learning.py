"""
Learning Router
Handle Brain AI continuous learning system, feedback processing, and analytics
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
import uuid
import json
import logging
from datetime import datetime

from app.database import db
from app.models.learning import (
    LearningEvent, LearningEventCreate, LearningEventResponse,
    FeedbackRequest, FeedbackBatch, LearningAnalytics,
    LearningConfig, LearningProgress, LearningInsight,
    LearningTrend, LearningHealth, LearningMetrics,
    LearningSummary
)
from app.models.user import User
from app.models.memory import MemoryResponse
from app.models.common import APIResponse, PaginatedResponse
from app.dependencies import (
    get_current_user, get_current_tenant, Timer, check_tenant_limits
)
from app.services.learning_service import LearningService

logger = logging.getLogger(__name__)
router = APIRouter()
learning_service = LearningService()


@router.post("/feedback", response_model=APIResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Submit feedback for learning"""
    try:
        with Timer("feedback_processing"):
            # Verify memory belongs to tenant if memory_id provided
            if feedback.memory_id:
                memory = await db.fetchrow(
                    "SELECT id, strength FROM memories WHERE id = $1 AND tenant_id = $2",
                    feedback.memory_id,
                    current_tenant['id']
                )
                
                if not memory:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Memory not found"
                    )
            
            # Create learning event
            event_id = str(uuid.uuid4())
            
            await db.execute("""
                INSERT INTO learning_events (
                    id, tenant_id, memory_id, event_type, feedback_type, 
                    outcome, confidence, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
            event_id,
            current_tenant['id'],
            feedback.memory_id,
            "feedback_received",
            feedback.feedback_type,
            json.dumps(feedback.outcome or {}),
            feedback.confidence,
            json.dumps(feedback.context or {})
            )
            
            # Process feedback if memory_id provided
            strength_change = 0
            if feedback.memory_id:
                strength_change = learning_service.calculate_strength_change(
                    feedback.feedback_type, 
                    feedback.confidence
                )
                
                # Update memory strength
                await db.execute("""
                    UPDATE memories 
                    SET strength = GREATEST(0.0, LEAST(1.0, strength + $1)),
                        updated_at = NOW()
                    WHERE id = $2 AND tenant_id = $3
                """, strength_change, feedback.memory_id, current_tenant['id'])
            
            # Trigger learning process
            background_tasks.add_task(
                learning_service.process_feedback,
                event_id,
                feedback,
                current_tenant['id']
            )
            
            # Log feedback submission
            background_tasks.add_task(
                logger.info, 
                f"Feedback submitted: {feedback.feedback_type} for memory {feedback.memory_id or 'N/A'}"
            )
            
            return APIResponse(
                message="Feedback processed successfully",
                data={
                    "event_id": event_id,
                    "strength_change": strength_change,
                    "feedback_type": feedback.feedback_type
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit feedback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process feedback"
        )


@router.post("/feedback/batch", response_model=APIResponse)
async def submit_feedback_batch(
    batch_data: FeedbackBatch,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Submit multiple feedback items in batch"""
    try:
        with Timer("batch_feedback_processing"):
            processed_count = 0
            errors = []
            
            for i, feedback_item in enumerate(batch_data.feedback_items):
                try:
                    # Verify memory if provided
                    if feedback_item.memory_id:
                        memory = await db.fetchrow(
                            "SELECT id FROM memories WHERE id = $1 AND tenant_id = $2",
                            feedback_item.memory_id,
                            current_tenant['id']
                        )
                        
                        if not memory:
                            errors.append(f"Feedback {i+1}: Memory not found")
                            continue
                    
                    # Create learning event
                    event_id = str(uuid.uuid4())
                    
                    await db.execute("""
                        INSERT INTO learning_events (
                            id, tenant_id, memory_id, event_type, feedback_type, 
                            outcome, confidence, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """, 
                    event_id,
                    current_tenant['id'],
                    feedback_item.memory_id,
                    "feedback_received",
                    feedback_item.feedback_type,
                    json.dumps(feedback_item.outcome or {}),
                    feedback_item.confidence,
                    json.dumps(feedback_item.context or {})
                    )
                    
                    # Process feedback if memory_id provided
                    if feedback_item.memory_id:
                        strength_change = learning_service.calculate_strength_change(
                            feedback_item.feedback_type, 
                            feedback_item.confidence
                        )
                        
                        await db.execute("""
                            UPDATE memories 
                            SET strength = GREATEST(0.0, LEAST(1.0, strength + $1)),
                                updated_at = NOW()
                            WHERE id = $2 AND tenant_id = $3
                        """, strength_change, feedback_item.memory_id, current_tenant['id'])
                    
                    processed_count += 1
                    
                except Exception as e:
                    errors.append(f"Feedback {i+1}: {str(e)}")
            
            # Process batch in background
            background_tasks.add_task(
                learning_service.process_batch_feedback,
                batch_data,
                current_tenant['id']
            )
            
            return APIResponse(
                message=f"Batch feedback completed: {processed_count} items processed",
                data={
                    "processed_count": processed_count,
                    "total_count": len(batch_data.feedback_items),
                    "errors": errors
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch feedback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process batch feedback"
        )


@router.get("/analytics/{project_id}", response_model=APIResponse)
async def get_learning_analytics(
    project_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get learning analytics for a project"""
    try:
        with Timer("learning_analytics"):
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
            
            analytics = await learning_service.get_learning_analytics(
                project_id, 
                current_tenant['id'], 
                days
            )
            
            return APIResponse(data=analytics)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get learning analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning analytics"
        )


@router.get("/progress/{memory_id}", response_model=APIResponse)
async def get_memory_learning_progress(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get learning progress for a specific memory"""
    try:
        # Verify memory belongs to tenant
        memory = await db.fetchrow(
            "SELECT id, strength FROM memories WHERE id = $1 AND tenant_id = $2",
            memory_id,
            current_tenant['id']
        )
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found"
            )
        
        # Get learning events for this memory
        learning_events = await db.fetch("""
            SELECT * FROM learning_events 
            WHERE memory_id = $1 AND tenant_id = $2
            ORDER BY created_at DESC
        """, memory_id, current_tenant['id'])
        
        # Calculate progress metrics
        total_feedback = len(learning_events)
        avg_confidence = sum(event['confidence'] for event in learning_events) / total_feedback if total_feedback > 0 else 0
        feedback_types = {}
        for event in learning_events:
            feedback_types[event['feedback_type']] = feedback_types.get(event['feedback_type'], 0) + 1
        
        # Calculate improvement
        initial_strength = await db.fetchval("""
            SELECT strength FROM memories 
            WHERE id = $1 AND tenant_id = $2
        """, memory_id, current_tenant['id'])
        
        current_strength = memory['strength']
        improvement_percentage = ((current_strength - initial_strength) / initial_strength * 100) if initial_strength > 0 else 0
        
        progress = LearningProgress(
            memory_id=memory_id,
            initial_strength=initial_strength,
            current_strength=current_strength,
            total_feedback_received=total_feedback,
            last_feedback_date=learning_events[0]['created_at'] if learning_events else None,
            improvement_percentage=improvement_percentage,
            learning_efficiency=avg_confidence
        )
        
        return APIResponse(data=progress)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get learning progress error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning progress"
        )


@router.get("/insights/{project_id}", response_model=APIResponse)
async def get_learning_insights(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get AI-generated learning insights and recommendations"""
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
        
        insights = await learning_service.generate_insights(project_id, current_tenant['id'])
        
        return APIResponse(data=insights)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get learning insights error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate learning insights"
        )


@router.get("/trends/{project_id}", response_model=APIResponse)
async def get_learning_trends(
    project_id: str,
    period: str = "week",
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get learning trends over time"""
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
        
        trends = await learning_service.get_learning_trends(
            project_id, 
            current_tenant['id'], 
            period
        )
        
        return APIResponse(data=trends)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get learning trends error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning trends"
        )


@router.get("/health", response_model=APIResponse)
async def get_learning_system_health(
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get learning system health status"""
    try:
        health = await learning_service.get_system_health(current_tenant['id'])
        
        return APIResponse(data=health)
        
    except Exception as e:
        logger.error(f"Get learning health error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning system health"
        )


@router.get("/metrics", response_model=APIResponse)
async def get_learning_metrics(
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get detailed learning metrics"""
    try:
        metrics = await learning_service.get_learning_metrics(current_tenant['id'])
        
        return APIResponse(data=metrics)
        
    except Exception as e:
        logger.error(f"Get learning metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning metrics"
        )


@router.get("/summary/{project_id}", response_model=APIResponse)
async def get_learning_summary(
    project_id: str,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get learning summary for a project"""
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
        
        summary = await learning_service.get_learning_summary(project_id, current_tenant['id'])
        
        return APIResponse(data=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get learning summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning summary"
        )


@router.get("/events/{project_id}", response_model=PaginatedResponse[LearningEventResponse])
async def get_learning_events(
    project_id: str,
    page: int = 1,
    per_page: int = 50,
    event_type: Optional[str] = None,
    feedback_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get learning events for a project"""
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
        
        # Build query conditions
        conditions = [
            "le.tenant_id = $1",
            "m.project_id = $2"
        ]
        params = [current_tenant['id'], project_id]
        param_count = 2
        
        if event_type:
            param_count += 1
            conditions.append(f"le.event_type = ${param_count}")
            params.append(event_type)
        
        if feedback_type:
            param_count += 1
            conditions.append(f"le.feedback_type = ${param_count}")
            params.append(feedback_type)
        
        where_clause = f"WHERE {' AND '.join(conditions)}"
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) 
            FROM learning_events le
            JOIN memories m ON le.memory_id = m.id
            {where_clause}
        """
        total = await db.fetchval(count_query, *params)
        
        # Get events with pagination
        offset = (page - 1) * per_page
        param_count += 1
        params.append(per_page)
        param_count += 1
        params.append(offset)
        
        query = f"""
            SELECT le.*, m.pattern_signature 
            FROM learning_events le
            JOIN memories m ON le.memory_id = m.id
            {where_clause}
            ORDER BY le.created_at DESC
            LIMIT ${param_count-1} OFFSET ${param_count}
        """
        
        events = await db.fetch(query, *params)
        
        # Convert to response models
        event_list = []
        for event in events:
            event_dict = dict(event)
            event_response = LearningEventResponse(
                id=event_dict['id'],
                event_type=event_dict['event_type'],
                feedback_type=event_dict['feedback_type'],
                outcome=json.loads(event_dict['outcome']) if event_dict['outcome'] else {},
                confidence=event_dict['confidence'],
                metadata=json.loads(event_dict['metadata']) if event_dict['metadata'] else {},
                created_at=event_dict['created_at'],
                memory_id=event_dict['memory_id']
            )
            event_list.append(event_response)
        
        # Calculate pagination
        pages = (total + per_page - 1) // per_page
        
        return PaginatedResponse(
            items=event_list,
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
        logger.error(f"Get learning events error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning events"
        )


@router.post("/config", response_model=APIResponse)
async def update_learning_config(
    config: LearningConfig,
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Update learning system configuration (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Store configuration in tenant settings
        await db.execute("""
            UPDATE tenants 
            SET settings = jsonb_set(
                COALESCE(settings, '{}'::jsonb),
                '{learning_config}',
                $1::jsonb
            ),
            updated_at = NOW()
            WHERE id = $2
        """, json.dumps(config.dict()), current_tenant['id'])
        
        # Update learning service
        learning_service.update_config(config)
        
        return APIResponse(message="Learning configuration updated successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update learning config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update learning configuration"
        )


@router.get("/config", response_model=APIResponse)
async def get_learning_config(
    current_user: User = Depends(get_current_user),
    current_tenant: Dict[str, Any] = Depends(get_current_tenant)
):
    """Get current learning configuration"""
    try:
        tenant = await db.fetchrow(
            "SELECT settings FROM tenants WHERE id = $1",
            current_tenant['id']
        )
        
        settings = tenant['settings'] or {}
        learning_config = settings.get('learning_config', {})
        
        # Merge with defaults
        config = LearningConfig(**learning_config)
        
        return APIResponse(data=config)
        
    except Exception as e:
        logger.error(f"Get learning config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning configuration"
        )
