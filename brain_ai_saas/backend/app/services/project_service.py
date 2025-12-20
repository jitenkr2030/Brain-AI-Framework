"""
Project Service
Service for project-specific operations and analytics
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from app.database import db
from app.models.project import ProjectSettings
from app.models.memory import MemoryExport

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for project operations"""
    
    async def get_project_stats(self, project_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive project statistics"""
        try:
            # Basic project info
            project = await db.fetchrow(
                "SELECT * FROM projects WHERE id = $1 AND tenant_id = $2",
                project_id,
                tenant_id
            )
            
            if not project:
                raise ValueError("Project not found")
            
            # Memory statistics
            memory_stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(strength) as avg_strength,
                    AVG(confidence) as avg_confidence,
                    SUM(access_count) as total_access_count,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_creations,
                    COUNT(CASE WHEN last_accessed >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_accesses
                FROM memories 
                WHERE project_id = $1 AND tenant_id = $2
            """, project_id, tenant_id)
            
            # Memories by type
            memories_by_type = await db.fetch("""
                SELECT memory_type, COUNT(*) as count
                FROM memories 
                WHERE project_id = $1 AND tenant_id = $2
                GROUP BY memory_type
            """, project_id, tenant_id)
            
            # API usage statistics
            api_stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_api_calls,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_api_calls
                FROM api_usage 
                WHERE tenant_id = $1 
                AND created_at >= (SELECT MIN(created_at) FROM memories WHERE project_id = $2)
            """, tenant_id, project_id)
            
            # Calculate growth rate (daily)
            recent_memories = memory_stats['recent_creations'] or 0
            days_back = min(7, (datetime.now() - project['created_at']).days)
            growth_rate_daily = recent_memories / days_back if days_back > 0 else 0
            
            return {
                "project_info": {
                    "id": project['id'],
                    "name": project['name'],
                    "description": project['description'],
                    "created_at": project['created_at'],
                    "updated_at": project['updated_at']
                },
                "memory_statistics": {
                    "total_memories": memory_stats['total_memories'] or 0,
                    "memories_by_type": {row['memory_type']: row['count'] for row in memories_by_type},
                    "avg_strength": float(memory_stats['avg_strength'] or 0),
                    "avg_confidence": float(memory_stats['avg_confidence'] or 0),
                    "total_access_count": memory_stats['total_access_count'] or 0,
                    "recent_creations": memory_stats['recent_creations'] or 0,
                    "recent_accesses": memory_stats['recent_accesses'] or 0
                },
                "api_statistics": {
                    "total_api_calls": api_stats['total_api_calls'] or 0,
                    "avg_response_time_ms": float(api_stats['avg_response_time'] or 0),
                    "recent_api_calls": api_stats['recent_api_calls'] or 0
                },
                "performance_metrics": {
                    "growth_rate_daily": growth_rate_daily,
                    "memory_utilization": self._calculate_memory_utilization(memory_stats),
                    "activity_level": self._calculate_activity_level(memory_stats, api_stats)
                }
            }
            
        except Exception as e:
            logger.error(f"Get project stats error: {e}")
            raise
    
    async def get_project_health(self, project_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get project health and performance metrics"""
        try:
            # Get health-related metrics
            health_stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(strength) as avg_strength,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN last_accessed >= NOW() - INTERVAL '24 hours' THEN 1 END) as recent_accesses,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as recent_creations,
                    COUNT(CASE WHEN strength < 0.3 THEN 1 END) as weak_memories,
                    MAX(last_accessed) as last_activity
                FROM memories 
                WHERE project_id = $1 AND tenant_id = $2
            """, project_id, tenant_id)
            
            # Get API performance metrics
            api_performance = await db.fetchrow("""
                SELECT 
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count,
                    COUNT(*) as total_requests
                FROM api_usage 
                WHERE tenant_id = $1 
                AND created_at >= NOW() - INTERVAL '24 hours'
            """, tenant_id)
            
            # Calculate health metrics
            total_memories = health_stats['total_memories'] or 0
            avg_strength = float(health_stats['avg_strength'] or 0)
            avg_confidence = float(health_stats['avg_confidence'] or 0)
            recent_accesses = health_stats['recent_accesses'] or 0
            recent_creations = health_stats['recent_creations'] or 0
            weak_memories = health_stats['weak_memories'] or 0
            
            avg_response_time = float(api_performance['avg_response_time'] or 0)
            error_count = api_performance['error_count'] or 0
            total_requests = api_performance['total_requests'] or 0
            
            # Calculate percentages
            memory_usage_percent = min(100, (total_memories / 1000) * 100) if total_memories > 0 else 0
            weak_memory_percent = (weak_memories / total_memories * 100) if total_memories > 0 else 0
            error_rate_percent = (error_count / total_requests * 100) if total_requests > 0 else 0
            
            # Determine health status
            issues = []
            recommendations = []
            
            if total_memories == 0:
                issues.append("No memories in project")
                recommendations.append("Add initial memories to get started")
            elif total_memories < 10:
                issues.append("Very few memories")
                recommendations.append("Consider adding more memories for better functionality")
            
            if avg_strength < 0.3:
                issues.append("Low average memory strength")
                recommendations.append("Provide more feedback to improve memory strength")
            
            if avg_confidence < 0.3:
                issues.append("Low average confidence")
                recommendations.append("Review and improve memory content quality")
            
            if recent_accesses == 0 and total_memories > 10:
                issues.append("No recent activity")
                recommendations.append("Use the project more frequently to maintain health")
            
            if weak_memory_percent > 20:
                issues.append("High percentage of weak memories")
                recommendations.append("Review and strengthen low-confidence memories")
            
            if avg_response_time > 1000:
                issues.append("Slow API response times")
                recommendations.append("Consider optimizing queries or upgrading plan")
            
            if error_rate_percent > 5:
                issues.append("High error rate")
                recommendations.append("Review API usage and error logs")
            
            # Calculate overall status
            critical_issues = len([issue for issue in issues if any(word in issue.lower() 
                                 for word in ["no memories", "high error", "slow response"])])
            
            if critical_issues > 0:
                status = "unhealthy"
            elif len(issues) <= 2:
                status = "healthy"
            else:
                status = "degraded"
            
            return {
                "status": status,
                "memory_usage_percent": memory_usage_percent,
                "api_usage_percent": min(100, (total_requests / 100) * 100),
                "avg_response_time_ms": avg_response_time,
                "error_rate_percent": error_rate_percent,
                "last_health_check": datetime.now(),
                "issues": issues,
                "recommendations": recommendations,
                "health_score": self._calculate_health_score(issues, avg_strength, avg_confidence)
            }
            
        except Exception as e:
            logger.error(f"Get project health error: {e}")
            raise
    
    async def export_project_data(self, project_id: str, tenant_id: str, 
                                export_config: MemoryExport, user_email: str):
        """Export project data (runs in background)"""
        try:
            logger.info(f"Starting data export for project {project_id} by {user_email}")
            
            # Build export query based on configuration
            conditions = ["tenant_id = $1", "project_id = $2"]
            params = [tenant_id, project_id]
            param_count = 2
            
            if export_config.memory_types:
                param_count += 1
                conditions.append(f"memory_type = ANY(${param_count})")
                params.append(export_config.memory_types)
            
            if export_config.date_from:
                param_count += 1
                conditions.append(f"created_at >= ${param_count}")
                params.append(export_config.date_from)
            
            if export_config.date_to:
                param_count += 1
                conditions.append(f"created_at <= ${param_count}")
                params.append(export_config.date_to)
            
            where_clause = f"WHERE {' AND '.join(conditions)}"
            
            # Get memories
            query = f"""
                SELECT * FROM memories 
                {where_clause}
                ORDER BY created_at DESC
            """
            
            memories = await db.fetch(query, *params)
            
            # Format data based on export format
            export_data = []
            for memory in memories:
                memory_data = {
                    "id": memory['id'],
                    "pattern_signature": memory['pattern_signature'],
                    "memory_type": memory['memory_type'],
                    "strength": memory['strength'],
                    "confidence": memory['confidence'],
                    "access_count": memory['access_count'],
                    "tags": memory['tags'],
                    "created_at": memory['created_at'].isoformat(),
                    "updated_at": memory['updated_at'].isoformat()
                }
                
                if export_config.include_content:
                    memory_data["content"] = json.loads(memory['content'])
                
                if export_config.include_context:
                    memory_data["context"] = json.loads(memory['context'])
                
                if export_config.include_metadata:
                    memory_data["last_accessed"] = memory['last_accessed'].isoformat() if memory['last_accessed'] else None
                
                export_data.append(memory_data)
            
            # Generate file based on format
            filename = f"project_{project_id}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if export_config.format == "json":
                file_content = json.dumps(export_data, indent=2, default=str)
                filename += ".json"
            elif export_config.format == "csv":
                import csv
                import io
                
                output = io.StringIO()
                if export_data:
                    writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
                    writer.writeheader()
                    writer.writerows(export_data)
                
                file_content = output.getvalue()
                filename += ".csv"
            else:  # XML
                file_content = self._convert_to_xml(export_data)
                filename += ".xml"
            
            # In a real implementation, you would:
            # 1. Upload the file to cloud storage (S3, GCS, etc.)
            # 2. Send an email to the user with download link
            # 3. Clean up temporary files
            
            logger.info(f"Data export completed for project {project_id}: {filename}")
            
            # Log completion
            await db.execute("""
                INSERT INTO learning_events (
                    id, tenant_id, event_type, metadata
                ) VALUES ($1, $2, $3, $4)
            """,
            str(uuid.uuid4()),
            tenant_id,
            "project_data_exported",
            json.dumps({
                "project_id": project_id,
                "export_format": export_config.format,
                "record_count": len(export_data),
                "filename": filename
            })
            )
            
        except Exception as e:
            logger.error(f"Export project data error: {e}")
            # In a real implementation, send error notification to user
    
    def _calculate_memory_utilization(self, memory_stats: Dict[str, Any]) -> float:
        """Calculate memory utilization score"""
        total = memory_stats['total_memories'] or 0
        avg_strength = float(memory_stats['avg_strength'] or 0)
        
        if total == 0:
            return 0.0
        
        # Score based on total memories and average strength
        utilization = min(100, (total / 100) * 50 + avg_strength * 50)
        return utilization
    
    def _calculate_activity_level(self, memory_stats: Dict[str, Any], 
                                api_stats: Dict[str, Any]) -> str:
        """Calculate activity level"""
        recent_accesses = memory_stats['recent_accesses'] or 0
        recent_api_calls = api_stats['recent_api_calls'] or 0
        
        total_activity = recent_accesses + recent_api_calls
        
        if total_activity > 50:
            return "high"
        elif total_activity > 10:
            return "medium"
        elif total_activity > 0:
            return "low"
        else:
            return "inactive"
    
    def _calculate_health_score(self, issues: List[str], avg_strength: float, 
                              avg_confidence: float) -> float:
        """Calculate overall health score (0-100)"""
        base_score = 100
        
        # Deduct points for issues
        for issue in issues:
            if "no memories" in issue.lower():
                base_score -= 30
            elif "low" in issue.lower():
                base_score -= 15
            elif "slow" in issue.lower() or "error" in issue.lower():
                base_score -= 10
        
        # Adjust based on quality metrics
        quality_adjustment = (avg_strength + avg_confidence) * 20
        base_score += quality_adjustment
        
        return max(0, min(100, base_score))
    
    def _convert_to_xml(self, data: List[Dict[str, Any]]) -> str:
        """Convert data to XML format"""
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_parts.append('<memories>')
        
        for item in data:
            xml_parts.append('  <memory>')
            for key, value in item.items():
                if value is not None:
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    xml_parts.append(f'    <{key}>{str(value)}</{key}>')
            xml_parts.append('  </memory>')
        
        xml_parts.append('</memories>')
        return '\n'.join(xml_parts)
    
    async def cleanup_inactive_memories(self, project_id: str, tenant_id: str, 
                                      days_inactive: int = 90):
        """Clean up old, inactive memories"""
        try:
            # Find inactive memories
            inactive_memories = await db.fetch("""
                SELECT id, pattern_signature, strength
                FROM memories 
                WHERE project_id = $1 AND tenant_id = $2
                    AND (last_accessed IS NULL OR last_accessed <= NOW() - INTERVAL '%s days')
                    AND strength < 0.2
                ORDER BY strength ASC, created_at ASC
                LIMIT 500
            """, project_id, tenant_id, days_inactive)
            
            deleted_count = 0
            for memory in inactive_memories:
                try:
                    # Delete memory
                    await db.execute(
                        "DELETE FROM memories WHERE id = $1 AND tenant_id = $2",
                        memory['id'],
                        tenant_id
                    )
                    
                    # Update project memory count
                    await db.execute(
                        "UPDATE projects SET memory_count = memory_count - 1 WHERE id = $1",
                        project_id
                    )
                    
                    deleted_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to delete inactive memory {memory['id']}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} inactive memories from project {project_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cleanup inactive memories error: {e}")
            raise
