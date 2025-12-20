"""
Learning Service
Core service for Brain AI continuous learning system
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from app.database import db
from app.models.learning import (
    LearningConfig, LearningAnalytics, LearningInsight,
    LearningTrend, LearningHealth, LearningMetrics,
    LearningSummary, FeedbackRequest
)

logger = logging.getLogger(__name__)


class LearningService:
    """Service for Brain AI continuous learning operations"""
    
    def __init__(self):
        self.config = LearningConfig()
    
    def update_config(self, config: LearningConfig):
        """Update learning configuration"""
        self.config = config
        logger.info(f"Learning configuration updated: {config.dict()}")
    
    def calculate_strength_change(self, feedback_type: str, confidence: float) -> float:
        """Calculate strength change based on feedback type and confidence"""
        base_changes = {
            "POSITIVE": 0.1,
            "NEGATIVE": -0.1,
            "NEUTRAL": 0.0,
            "CORRECTION": 0.05,
            "CONFIRMATION": 0.08
        }
        
        base_change = base_changes.get(feedback_type, 0.0)
        
        # Apply learning rate and confidence
        adjusted_change = base_change * confidence * self.config.learning_rate
        
        return adjusted_change
    
    async def process_feedback(self, event_id: str, feedback: FeedbackRequest, tenant_id: str):
        """Process individual feedback (runs in background)"""
        try:
            logger.info(f"Processing feedback {event_id} for tenant {tenant_id}")
            
            # Analyze feedback impact
            await self._analyze_feedback_impact(event_id, feedback, tenant_id)
            
            # Update memory patterns if needed
            if feedback.memory_id:
                await self._update_memory_patterns(feedback.memory_id, feedback, tenant_id)
            
            # Generate learning insights
            if self.config.auto_learning_enabled:
                await self._generate_learning_insights(feedback, tenant_id)
            
        except Exception as e:
            logger.error(f"Process feedback error: {e}")
    
    async def process_batch_feedback(self, batch_data, tenant_id: str):
        """Process batch feedback (runs in background)"""
        try:
            logger.info(f"Processing batch feedback for tenant {tenant_id}")
            
            # Analyze batch patterns
            await self._analyze_batch_patterns(batch_data, tenant_id)
            
            # Generate insights for the batch
            if self.config.auto_learning_enabled:
                await self._generate_batch_insights(batch_data, tenant_id)
            
        except Exception as e:
            logger.error(f"Process batch feedback error: {e}")
    
    async def get_learning_analytics(self, project_id: str, tenant_id: str, days: int = 30) -> LearningAnalytics:
        """Get comprehensive learning analytics"""
        try:
            # Get basic learning statistics
            basic_stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_events,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN feedback_type = 'POSITIVE' THEN 1 END) as positive_feedback,
                    COUNT(CASE WHEN feedback_type = 'NEGATIVE' THEN 1 END) as negative_feedback,
                    COUNT(CASE WHEN feedback_type = 'NEUTRAL' THEN 1 END) as neutral_feedback,
                    COUNT(CASE WHEN feedback_type = 'CORRECTION' THEN 1 END) as corrections,
                    COUNT(CASE WHEN feedback_type = 'CONFIRMATION' THEN 1 END) as confirmations
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE le.tenant_id = $1 
                AND m.project_id = $2
                AND le.created_at >= NOW() - INTERVAL '%s days'
            """, tenant_id, project_id, days)
            
            # Get events by type
            events_by_type = await db.fetch("""
                SELECT event_type, COUNT(*) as count
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE le.tenant_id = $1 AND m.project_id = $2
                AND le.created_at >= NOW() - INTERVAL '%s days'
                GROUP BY event_type
            """, tenant_id, project_id, days)
            
            # Get improvement trend
            improvement_trend = await db.fetch("""
                SELECT 
                    DATE_TRUNC('day', le.created_at) as date,
                    AVG(
                        CASE 
                            WHEN le.feedback_type IN ('POSITIVE', 'CONFIRMATION') THEN 1
                            WHEN le.feedback_type = 'NEGATIVE' THEN -1
                            ELSE 0
                        END
                    ) as improvement_score
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE le.tenant_id = $1 AND m.project_id = $2
                AND le.created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE_TRUNC('day', le.created_at)
                ORDER BY date
            """, tenant_id, project_id, days)
            
            # Get memory impact analysis
            memory_impact = await db.fetchrow("""
                SELECT 
                    COUNT(DISTINCT m.id) as total_memories_with_feedback,
                    AVG(m.strength) as avg_strength_with_feedback,
                    AVG(m.strength - m_initial.strength) as avg_strength_improvement
                FROM memories m
                JOIN (
                    SELECT id, strength as initial_strength
                    FROM memories 
                    WHERE project_id = $2
                ) m_initial ON m.id = m_initial.id
                JOIN learning_events le ON m.id = le.memory_id
                WHERE m.tenant_id = $1 AND m.project_id = $2
                AND le.created_at >= NOW() - INTERVAL '%s days'
            """, tenant_id, project_id, days)
            
            # Calculate learning rate
            total_events = basic_stats['total_events'] or 0
            time_period = days
            learning_rate = total_events / time_period if time_period > 0 else 0
            
            return LearningAnalytics(
                total_events=total_events,
                events_by_type={row['event_type']: row['count'] for row in events_by_type},
                events_by_feedback={
                    "POSITIVE": basic_stats['positive_feedback'] or 0,
                    "NEGATIVE": basic_stats['negative_feedback'] or 0,
                    "NEUTRAL": basic_stats['neutral_feedback'] or 0,
                    "CORRECTION": basic_stats['corrections'] or 0,
                    "CONFIRMATION": basic_stats['confirmations'] or 0
                },
                avg_confidence=float(basic_stats['avg_confidence'] or 0),
                learning_rate=learning_rate,
                improvement_trend=[
                    {
                        "date": row['date'],
                        "score": float(row['improvement_score'] or 0)
                    }
                    for row in improvement_trend
                ],
                feedback_distribution={
                    "POSITIVE": (basic_stats['positive_feedback'] or 0) / max(total_events, 1),
                    "NEGATIVE": (basic_stats['negative_feedback'] or 0) / max(total_events, 1),
                    "NEUTRAL": (basic_stats['neutral_feedback'] or 0) / max(total_events, 1),
                    "CORRECTION": (basic_stats['corrections'] or 0) / max(total_events, 1),
                    "CONFIRMATION": (basic_stats['confirmations'] or 0) / max(total_events, 1)
                },
                memory_impact={
                    "total_memories_with_feedback": memory_impact['total_memories_with_feedback'] or 0,
                    "avg_strength_with_feedback": float(memory_impact['avg_strength_with_feedback'] or 0),
                    "avg_strength_improvement": float(memory_impact['avg_strength_improvement'] or 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Get learning analytics error: {e}")
            raise
    
    async def generate_insights(self, project_id: str, tenant_id: str) -> List[LearningInsight]:
        """Generate AI-powered learning insights"""
        try:
            insights = []
            
            # Analyze memory strength distribution
            strength_analysis = await db.fetchrow("""
                SELECT 
                    COUNT(CASE WHEN strength < 0.3 THEN 1 END) as weak_memories,
                    COUNT(CASE WHEN strength >= 0.7 THEN 1 END) as strong_memories,
                    COUNT(*) as total_memories,
                    AVG(strength) as avg_strength
                FROM memories 
                WHERE project_id = $1 AND tenant_id = $2
            """, project_id, tenant_id)
            
            if strength_analysis:
                total = strength_analysis['total_memories'] or 0
                weak_count = strength_analysis['weak_memories'] or 0
                strong_count = strength_analysis['strong_memories'] or 0
                
                if weak_count > total * 0.3:
                    insights.append(LearningInsight(
                        insight_type="memory_quality",
                        title="High Percentage of Weak Memories",
                        description=f"{weak_count} memories have low strength (< 0.3). Consider providing more feedback to strengthen them.",
                        impact_score=0.8,
                        actionable=True,
                        suggested_actions=[
                            "Review and provide feedback on weak memories",
                            "Increase user interaction with the system",
                            "Consider memory consolidation strategies"
                        ]
                    ))
                
                if strong_count < total * 0.2:
                    insights.append(LearningInsight(
                        insight_type="memory_quality",
                        title="Few High-Quality Memories",
                        description=f"Only {strong_count} memories have high strength (≥ 0.7). Focus on strengthening important memories.",
                        impact_score=0.7,
                        actionable=True,
                        suggested_actions=[
                            "Identify critical memories for strengthening",
                            "Provide more positive feedback on important patterns",
                            "Review memory organization and tagging"
                        ]
                    ))
            
            # Analyze feedback patterns
            feedback_patterns = await db.fetchrow("""
                SELECT 
                    COUNT(CASE WHEN feedback_type = 'NEGATIVE' THEN 1 END) as negative_count,
                    COUNT(CASE WHEN feedback_type = 'POSITIVE' THEN 1 END) as positive_count,
                    COUNT(*) as total_feedback
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE m.project_id = $1 AND m.tenant_id = $2
                AND le.created_at >= NOW() - INTERVAL '30 days'
            """, project_id, tenant_id)
            
            if feedback_patterns:
                total_feedback = feedback_patterns['total_feedback'] or 0
                negative_feedback = feedback_patterns['negative_count'] or 0
                
                if total_feedback > 0 and negative_feedback / total_feedback > 0.5:
                    insights.append(LearningInsight(
                        insight_type="feedback_pattern",
                        title="High Negative Feedback Rate",
                        description="More than 50% of feedback is negative. Consider reviewing memory quality and user guidance.",
                        impact_score=0.9,
                        actionable=True,
                        suggested_actions=[
                            "Review memory content accuracy",
                            "Improve user onboarding and guidance",
                            "Analyze user interaction patterns"
                        ]
                    ))
            
            # Analyze learning velocity
            recent_events = await db.fetchval("""
                SELECT COUNT(*)
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE m.project_id = $1 AND m.tenant_id = $2
                AND le.created_at >= NOW() - INTERVAL '7 days'
            """, project_id, tenant_id)
            
            if recent_events < 5:
                insights.append(LearningInsight(
                    insight_type="learning_velocity",
                    title="Low Learning Activity",
                    description="Few learning events in the past week. Consider increasing user engagement.",
                    impact_score=0.6,
                    actionable=True,
                    suggested_actions=[
                        "Encourage more user interactions",
                        "Implement proactive feedback prompts",
                        "Review system usability"
                    ]
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Generate insights error: {e}")
            return []
    
    async def get_learning_trends(self, project_id: str, tenant_id: str, period: str) -> List[LearningTrend]:
        """Get learning trends over time"""
        try:
            # Determine time interval based on period
            if period == "day":
                interval = "1 day"
                date_format = "YYYY-MM-DD"
            elif period == "week":
                interval = "1 week"
                date_format = "YYYY-'W'WW"
            else:  # month
                interval = "1 month"
                date_format = "YYYY-MM"
            
            # Get trends
            trends = await db.fetch(f"""
                SELECT 
                    DATE_TRUNC('{period}', le.created_at) as period,
                    COUNT(*) as events_count,
                    AVG(le.confidence) as avg_confidence,
                    COUNT(CASE WHEN le.feedback_type IN ('POSITIVE', 'CONFIRMATION') THEN 1 END) as positive_events,
                    COUNT(CASE WHEN le.feedback_type = 'NEGATIVE' THEN 1 END) as negative_events,
                    AVG(
                        CASE 
                            WHEN le.feedback_type IN ('POSITIVE', 'CONFIRMATION') THEN 1
                            WHEN le.feedback_type = 'NEGATIVE' THEN -1
                            ELSE 0
                        END
                    ) as improvement_rate
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE le.tenant_id = $1 AND m.project_id = $2
                AND le.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY DATE_TRUNC('{period}', le.created_at)
                ORDER BY period
            """, tenant_id, project_id)
            
            trend_list = []
            for trend in trends:
                # Calculate learning efficiency
                total_events = trend['events_count'] or 0
                if total_events > 0:
                    learning_efficiency = (trend['positive_events'] or 0 - trend['negative_events'] or 0) / total_events
                else:
                    learning_efficiency = 0
                
                # Get top feedback types
                top_feedback = await db.fetch(f"""
                    SELECT le.feedback_type, COUNT(*) as count
                    FROM learning_events le
                    JOIN memories m ON le.memory_id = m.id
                    WHERE le.tenant_id = $1 AND m.project_id = $2
                    AND DATE_TRUNC('{period}', le.created_at) = $3
                    GROUP BY le.feedback_type
                    ORDER BY count DESC
                    LIMIT 3
                """, tenant_id, project_id, trend['period'])
                
                trend_list.append(LearningTrend(
                    period=trend['period'].strftime(date_format),
                    events_count=total_events,
                    avg_confidence=float(trend['avg_confidence'] or 0),
                    improvement_rate=float(trend['improvement_rate'] or 0),
                    top_feedback_types=[fb['feedback_type'] for fb in top_feedback],
                    learning_efficiency=learning_efficiency
                ))
            
            return trend_list
            
        except Exception as e:
            logger.error(f"Get learning trends error: {e}")
            return []
    
    async def get_system_health(self, tenant_id: str) -> LearningHealth:
        """Get learning system health"""
        try:
            # Get basic health metrics
            health_stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as recent_events,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN feedback_type = 'NEGATIVE' THEN 1 END) as negative_events,
                    COUNT(*) as total_feedback_events
                FROM learning_events 
                WHERE tenant_id = $1
                AND created_at >= NOW() - INTERVAL '7 days'
            """, tenant_id)
            
            # Calculate processing metrics
            total_events = health_stats['total_events'] or 0
            recent_events = health_stats['recent_events'] or 0
            avg_confidence = float(health_stats['avg_confidence'] or 0)
            negative_events = health_stats['negative_events'] or 0
            total_feedback = health_stats['total_feedback_events'] or 0
            
            # Calculate rates
            events_per_hour = recent_events / 24 if recent_events > 0 else 0
            success_rate = 1.0 - (negative_events / max(total_feedback, 1))
            
            # Determine health status
            issues = []
            recommendations = []
            
            if total_events == 0:
                issues.append("No learning activity")
                recommendations.append("Start using the system to generate learning data")
            elif recent_events == 0 and total_events > 10:
                issues.append("No recent learning activity")
                recommendations.append("Increase system usage to maintain learning")
            
            if avg_confidence < 0.4:
                issues.append("Low average feedback confidence")
                recommendations.append("Improve feedback quality or user training")
            
            if success_rate < 0.7:
                issues.append("Low learning success rate")
                recommendations.append("Review system performance and user guidance")
            
            # Calculate overall status
            if len(issues) == 0:
                status = "healthy"
            elif len(issues) <= 2:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return LearningHealth(
                status=status,
                total_events=total_events,
                events_per_hour=events_per_hour,
                avg_processing_time_ms=50.0,  # Simplified - would measure actual processing time
                success_rate=success_rate,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Get learning health error: {e}")
            raise
    
    async def get_learning_metrics(self, tenant_id: str) -> LearningMetrics:
        """Get detailed learning metrics"""
        try:
            # Get comprehensive metrics
            metrics_data = await db.fetchrow("""
                SELECT 
                    -- Feedback accuracy
                    COUNT(CASE WHEN feedback_type IN ('POSITIVE', 'CONFIRMATION') THEN 1 END) as positive_feedback,
                    COUNT(CASE WHEN feedback_type = 'NEGATIVE' THEN 1 END) as negative_feedback,
                    COUNT(*) as total_feedback,
                    
                    -- Learning velocity
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '1 hour' THEN 1 END) as hourly_events,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '1 day' THEN 1 END) as daily_events,
                    
                    -- Memory retention
                    AVG(m.strength) as avg_memory_strength,
                    COUNT(CASE WHEN m.strength >= 0.7 THEN 1 END) as high_strength_memories,
                    COUNT(m.id) as total_memories,
                    
                    -- Error correction
                    COUNT(CASE WHEN feedback_type = 'CORRECTION' THEN 1 END) as corrections
                FROM learning_events le
                LEFT JOIN memories m ON le.memory_id = m.id
                WHERE le.tenant_id = $1
                AND le.created_at >= NOW() - INTERVAL '30 days'
            """, tenant_id)
            
            if not metrics_data:
                return LearningMetrics(
                    feedback_accuracy=0.0,
                    learning_velocity=0.0,
                    memory_retention_rate=0.0,
                    adaptation_speed=0.0,
                    error_correction_rate=0.0,
                    overall_learning_score=0.0
                )
            
            # Calculate metrics
            total_feedback = metrics_data['total_feedback'] or 0
            positive_feedback = metrics_data['positive_feedback'] or 0
            negative_feedback = metrics_data['negative_feedback'] or 0
            corrections = metrics_data['corrections'] or 0
            
            feedback_accuracy = positive_feedback / max(total_feedback, 1)
            learning_velocity = (metrics_data['daily_events'] or 0) / 30.0  # Events per day average
            memory_retention_rate = (metrics_data['avg_memory_strength'] or 0)
            adaptation_speed = (metrics_data['hourly_events'] or 0) * 24  # Events per day estimate
            error_correction_rate = corrections / max(total_feedback, 1)
            
            # Overall learning score (weighted average)
            overall_score = (
                feedback_accuracy * 0.3 +
                min(1.0, learning_velocity / 10.0) * 0.2 +
                memory_retention_rate * 0.3 +
                min(1.0, adaptation_speed / 100.0) * 0.1 +
                error_correction_rate * 0.1
            )
            
            return LearningMetrics(
                feedback_accuracy=feedback_accuracy,
                learning_velocity=learning_velocity,
                memory_retention_rate=memory_retention_rate,
                adaptation_speed=adaptation_speed,
                error_correction_rate=error_correction_rate,
                overall_learning_score=overall_score
            )
            
        except Exception as e:
            logger.error(f"Get learning metrics error: {e}")
            raise
    
    async def get_learning_summary(self, project_id: str, tenant_id: str) -> LearningSummary:
        """Get learning summary for a project"""
        try:
            # Get basic summary data
            summary_data = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_events,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_events,
                    MAX(created_at) as last_activity
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE le.tenant_id = $1 AND m.project_id = $2
            """, tenant_id, project_id)
            
            # Calculate improvement rate
            recent_improvement = await db.fetchval("""
                SELECT AVG(
                    CASE 
                        WHEN le.feedback_type IN ('POSITIVE', 'CONFIRMATION') THEN 1
                        WHEN le.feedback_type = 'NEGATIVE' THEN -1
                        ELSE 0
                    END
                )
                FROM learning_events le
                JOIN memories m ON le.memory_id = m.id
                WHERE le.tenant_id = $1 AND m.project_id = $2
                AND le.created_at >= NOW() - INTERVAL '7 days'
            """, tenant_id, project_id)
            
            # Get top insights
            insights = await self.generate_insights(project_id, tenant_id)
            top_insights = insights[:3]  # Top 3 insights
            
            # Determine health status
            total_events = summary_data['total_events'] or 0
            recent_events = summary_data['recent_events'] or 0
            avg_confidence = float(summary_data['avg_confidence'] or 0)
            
            if total_events == 0:
                health_status = "unhealthy"
            elif recent_events > total_events * 0.2 and avg_confidence > 0.6:
                health_status = "healthy"
            elif recent_events > 0 and avg_confidence > 0.4:
                health_status = "degraded"
            else:
                health_status = "unhealthy"
            
            return LearningSummary(
                total_events=total_events,
                avg_confidence=avg_confidence,
                improvement_rate=float(recent_improvement or 0),
                top_insights=top_insights,
                health_status=health_status,
                last_activity=summary_data['last_activity']
            )
            
        except Exception as e:
            logger.error(f"Get learning summary error: {e}")
            raise
    
    # Helper methods
    async def _analyze_feedback_impact(self, event_id: str, feedback: FeedbackRequest, tenant_id: str):
        """Analyze the impact of feedback on the system"""
        # This would implement more sophisticated analysis
        # For now, it's a placeholder for future enhancement
        pass
    
    async def _update_memory_patterns(self, memory_id: str, feedback: FeedbackRequest, tenant_id: str):
        """Update memory patterns based on feedback"""
        # This would implement pattern learning and adaptation
        # For now, it's a placeholder for future enhancement
        pass
    
    async def _generate_learning_insights(self, feedback: FeedbackRequest, tenant_id: str):
        """Generate insights based on feedback"""
        # This would implement real-time insight generation
        # For now, it's a placeholder for future enhancement
        pass
    
    async def _analyze_batch_patterns(self, batch_data, tenant_id: str):
        """Analyze patterns in batch feedback"""
        # This would implement batch pattern analysis
        # For now, it's a placeholder for future enhancement
        pass
    
    async def _generate_batch_insights(self, batch_data, tenant_id: str):
        """Generate insights for batch feedback"""
        # This would implement batch insight generation
        # For now, it's a placeholder for future enhancement
        pass
