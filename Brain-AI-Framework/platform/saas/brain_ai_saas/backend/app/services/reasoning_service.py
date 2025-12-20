"""
Reasoning Service
Core service for Brain AI reasoning engine and query processing
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from app.database import db
from app.config import settings

logger = logging.getLogger(__name__)


class ReasoningService:
    """Service for Brain AI reasoning operations"""
    
    def __init__(self):
        self.vector_search_enabled = settings.ENABLE_VECTOR_SEARCH
    
    async def process_query(self, query: Dict[str, Any], tenant_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a reasoning query"""
        try:
            query_text = query.get("query", "")
            max_memories = query.get("max_memories", 10)
            confidence_threshold = query.get("confidence_threshold", 0.3)
            
            # Get relevant memories
            relevant_memories = await self._get_relevant_memories(
                tenant_id,
                project_id,
                query_text,
                max_memories,
                confidence_threshold
            )
            
            # Process reasoning
            reasoning_result = await self._reason_over_memories(
                query_text,
                relevant_memories
            )
            
            # Generate explanation
            explanation = await self._generate_explanation(
                query_text,
                reasoning_result,
                relevant_memories
            )
            
            # Store query record
            query_id = await self._store_query_record(
                query,
                reasoning_result,
                relevant_memories,
                tenant_id,
                project_id
            )
            
            return {
                "query_id": query_id,
                "query": query_text,
                "response": reasoning_result["response"],
                "confidence": reasoning_result["confidence"],
                "memories_used": [m["id"] for m in relevant_memories],
                "explanation": explanation,
                "processing_time_ms": reasoning_result.get("processing_time_ms", 0)
            }
            
        except Exception as e:
            logger.error(f"Process query error: {e}")
            raise
    
    async def _get_relevant_memories(
        self, 
        tenant_id: str, 
        project_id: Optional[str], 
        query: str, 
        max_memories: int, 
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Get relevant memories for reasoning"""
        try:
            # Build query conditions
            conditions = ["tenant_id = $1"]
            params = [tenant_id]
            param_count = 1
            
            if project_id:
                param_count += 1
                conditions.append(f"project_id = ${param_count}")
                params.append(project_id)
            
            # Add text search
            if query:
                param_count += 1
                conditions.append(f"""
                    (pattern_signature ILIKE ${param_count} 
                     OR content::text ILIKE ${param_count}
                     OR context::text ILIKE ${param_count})
                """)
                params.append(f"%{query}%")
            
            # Add confidence threshold
            param_count += 1
            conditions.append(f"confidence >= ${param_count}")
            params.append(confidence_threshold)
            
            where_clause = f"WHERE {' AND '.join(conditions)}"
            
            # Get memories ordered by relevance
            query_sql = f"""
                SELECT * FROM memories 
                {where_clause}
                ORDER BY strength DESC, confidence DESC, access_count DESC
                LIMIT ${param_count + 1}
            """
            params.append(max_memories)
            
            memories = await db.fetch(query_sql, *params)
            
            # Convert to list of dicts
            relevant_memories = []
            for memory in memories:
                relevant_memories.append({
                    "id": memory['id'],
                    "pattern_signature": memory['pattern_signature'],
                    "memory_type": memory['memory_type'],
                    "content": json.loads(memory['content']),
                    "context": json.loads(memory['context']),
                    "strength": memory['strength'],
                    "confidence": memory['confidence'],
                    "access_count": memory['access_count'],
                    "tags": memory['tags']
                })
            
            # If vector search is enabled, also do semantic search
            if self.vector_search_enabled and query:
                semantic_results = await self._semantic_search(
                    query,
                    tenant_id,
                    project_id,
                    max_memories
                )
                
                # Merge and deduplicate results
                all_memories = {m["id"]: m for m in relevant_memories}
                for sem_mem in semantic_results:
                    if sem_mem["id"] not in all_memories:
                        all_memories[sem_mem["id"]] = sem_mem
                
                # Sort by combined relevance score
                relevant_memories = list(all_memories.values())
                relevant_memories.sort(key=lambda m: (m["strength"] + m["confidence"]) / 2, reverse=True)
                relevant_memories = relevant_memories[:max_memories]
            
            return relevant_memories
            
        except Exception as e:
            logger.error(f"Get relevant memories error: {e}")
            return []
    
    async def _semantic_search(self, query: str, tenant_id: str, project_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        # This would integrate with Pinecone or similar vector database
        # For now, return empty list (fallback to text search)
        return []
    
    async def _reason_over_memories(self, query: str, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform reasoning over retrieved memories"""
        try:
            if not memories:
                return {
                    "response": "I don't have enough information to answer that question.",
                    "confidence": 0.0,
                    "reasoning": "No relevant memories found",
                    "processing_time_ms": 0
                }
            
            start_time = datetime.now()
            
            # Simple reasoning algorithm (in production, this would be more sophisticated)
            relevant_info = []
            total_strength = 0
            total_confidence = 0
            
            for memory in memories:
                # Calculate relevance score
                relevance = self._calculate_relevance(query, memory)
                
                # Add to reasoning if relevant enough
                if relevance > 0.3:
                    relevant_info.append({
                        "memory": memory,
                        "relevance": relevance,
                        "strength": memory["strength"],
                        "confidence": memory["confidence"]
                    })
                    
                    total_strength += memory["strength"] * relevance
                    total_confidence += memory["confidence"] * relevance
            
            # Generate response
            if not relevant_info:
                response = "I found some information, but it's not directly relevant to your question."
                confidence = 0.3
            else:
                # Aggregate information from relevant memories
                response = await self._aggregate_information(query, relevant_info)
                confidence = min(1.0, total_confidence / len(relevant_info))
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "response": response,
                "confidence": confidence,
                "memories_used": len(relevant_info),
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Reason over memories error: {e}")
            return {
                "response": "I'm having trouble processing that request.",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "processing_time_ms": 0
            }
    
    def _calculate_relevance(self, query: str, memory: Dict[str, Any]) -> float:
        """Calculate relevance score between query and memory"""
        try:
            # Simple keyword matching (in production, use semantic similarity)
            query_words = set(query.lower().split())
            
            # Check pattern signature
            pattern_words = set(memory["pattern_signature"].lower().split())
            pattern_match = len(query_words.intersection(pattern_words)) / max(len(query_words), 1)
            
            # Check content
            content_text = json.dumps(memory["content"]).lower()
            content_words = set(content_text.split())
            content_match = len(query_words.intersection(content_words)) / max(len(query_words), 1)
            
            # Combine scores with memory quality
            relevance = (pattern_match * 0.4 + content_match * 0.3) * memory["strength"] * memory["confidence"]
            
            return min(1.0, relevance)
            
        except Exception as e:
            logger.error(f"Calculate relevance error: {e}")
            return 0.0
    
    async def _aggregate_information(self, query: str, relevant_info: List[Dict[str, Any]]) -> str:
        """Aggregate information from multiple memories"""
        try:
            # Sort by relevance
            relevant_info.sort(key=lambda x: x["relevance"], reverse=True)
            
            # Extract key information
            key_points = []
            for info in relevant_info[:5]:  # Top 5 most relevant
                memory = info["memory"]
                content = memory["content"]
                
                # Extract text content
                if isinstance(content, dict) and "text" in content:
                    key_points.append(content["text"])
                elif isinstance(content, str):
                    key_points.append(content)
            
            if not key_points:
                return "I found some relevant information but couldn't extract specific details."
            
            # Simple aggregation (in production, use more sophisticated NLP)
            if len(key_points) == 1:
                return key_points[0]
            else:
                # Combine multiple points
                combined = " Based on the information available: " + "; ".join(key_points[:3])
                return combined
            
        except Exception as e:
            logger.error(f"Aggregate information error: {e}")
            return "I found relevant information but had trouble processing it."
    
    async def _generate_explanation(self, query: str, reasoning_result: Dict[str, Any], memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate explanation for the reasoning process"""
        try:
            explanation = {
                "query": query,
                "memories_found": len(memories),
                "memories_used": reasoning_result.get("memories_used", 0),
                "confidence": reasoning_result["confidence"],
                "reasoning_steps": [],
                "key_memories": []
            }
            
            # Add reasoning steps
            if memories:
                explanation["reasoning_steps"].append(
                    f"Found {len(memories)} relevant memories"
                )
                
                explanation["reasoning_steps"].append(
                    f"Used {reasoning_result.get('memories_used', 0)} memories for reasoning"
                )
                
                explanation["reasoning_steps"].append(
                    f"Overall confidence: {reasoning_result['confidence']:.2f}"
                )
            
            # Add key memories
            for memory in memories[:3]:  # Top 3 memories
                explanation["key_memories"].append({
                    "pattern": memory["pattern_signature"],
                    "type": memory["memory_type"],
                    "strength": memory["strength"],
                    "confidence": memory["confidence"]
                })
            
            return explanation
            
        except Exception as e:
            logger.error(f"Generate explanation error: {e}")
            return {"error": str(e)}
    
    async def _store_query_record(
        self, 
        query: Dict[str, Any], 
        reasoning_result: Dict[str, Any], 
        memories: List[Dict[str, Any]], 
        tenant_id: str, 
        project_id: Optional[str]
    ) -> str:
        """Store query record for analytics"""
        try:
            query_id = str(uuid.uuid4())
            
            await db.execute("""
                INSERT INTO learning_events (
                    id, tenant_id, event_type, metadata
                ) VALUES ($1, $2, $3, $4)
            """,
            query_id,
            tenant_id,
            "reasoning_query",
            json.dumps({
                "query": query,
                "response": reasoning_result,
                "memories_used": [m["id"] for m in memories],
                "project_id": project_id,
                "processing_time_ms": reasoning_result.get("processing_time_ms", 0)
            })
            )
            
            return query_id
            
        except Exception as e:
            logger.error(f"Store query record error: {e}")
            return str(uuid.uuid4())  # Return random ID even if storage fails
    
    async def get_relevant_context(
        self, 
        project_id: str, 
        tenant_id: str, 
        query: Optional[str], 
        memory_types: Optional[List[str]], 
        limit: int
    ) -> Dict[str, Any]:
        """Get relevant context for reasoning"""
        try:
            # Build query for context memories
            conditions = ["tenant_id = $1", "project_id = $2"]
            params = [tenant_id, project_id]
            param_count = 2
            
            if memory_types:
                param_count += 1
                conditions.append(f"memory_type = ANY(${param_count})")
                params.append(memory_types)
            
            # Order by recency and strength
            query_sql = f"""
                SELECT * FROM memories 
                WHERE {' AND '.join(conditions)}
                ORDER BY updated_at DESC, strength DESC
                LIMIT ${param_count + 1}
            """
            params.append(limit)
            
            memories = await db.fetch(query_sql, *params)
            
            context_memories = []
            for memory in memories:
                context_memories.append({
                    "id": memory['id'],
                    "pattern_signature": memory['pattern_signature'],
                    "memory_type": memory['memory_type'],
                    "content": json.loads(memory['content']),
                    "strength": memory['strength'],
                    "confidence": memory['confidence'],
                    "updated_at": memory['updated_at'].isoformat()
                })
            
            return {
                "context_memories": context_memories,
                "total_found": len(context_memories),
                "query": query,
                "memory_types": memory_types
            }
            
        except Exception as e:
            logger.error(f"Get relevant context error: {e}")
            return {"context_memories": [], "total_found": 0}
    
    async def get_explanation(self, query_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get explanation for a specific query"""
        try:
            result = await db.fetchrow("""
                SELECT metadata FROM learning_events 
                WHERE id = $1 AND tenant_id = $2 AND event_type = 'reasoning_query'
            """, query_id, tenant_id)
            
            if not result:
                return None
            
            metadata = json.loads(result['metadata'] or '{}')
            return {
                "query_id": query_id,
                "query": metadata.get('query', {}),
                "response": metadata.get('response', {}),
                "memories_used": metadata.get('memories_used', []),
                "processing_time_ms": metadata.get('processing_time_ms', 0),
                "created_at": result.get('created_at')
            }
            
        except Exception as e:
            logger.error(f"Get explanation error: {e}")
            return None
    
    async def get_analytics(self, project_id: str, tenant_id: str, days: int) -> Dict[str, Any]:
        """Get reasoning analytics"""
        try:
            # Get query statistics
            stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG((metadata->>'processing_time_ms')::numeric) as avg_processing_time,
                    AVG((metadata->>'response'->>'confidence')::numeric) as avg_confidence,
                    COUNT(CASE WHEN (metadata->>'response'->>'confidence')::numeric >= 0.7 THEN 1 END) as high_confidence_queries
                FROM learning_events 
                WHERE tenant_id = $1 
                AND event_type = 'reasoning_query'
                AND metadata->>'project_id' = $2
                AND created_at >= NOW() - INTERVAL '%s days'
            """, tenant_id, project_id, days)
            
            # Get query trends
            trends = await db.fetch("""
                SELECT 
                    DATE_TRUNC('day', created_at) as date,
                    COUNT(*) as query_count,
                    AVG((metadata->>'response'->>'confidence')::numeric) as avg_confidence
                FROM learning_events 
                WHERE tenant_id = $1 
                AND event_type = 'reasoning_query'
                AND metadata->>'project_id' = $2
                AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE_TRUNC('day', created_at)
                ORDER BY date
            """, tenant_id, project_id, days)
            
            # Get top queries
            top_queries = await db.fetch("""
                SELECT 
                    metadata->>'query'->>'query' as query_text,
                    COUNT(*) as frequency,
                    AVG((metadata->>'response'->>'confidence')::numeric) as avg_confidence
                FROM learning_events 
                WHERE tenant_id = $1 
                AND event_type = 'reasoning_query'
                AND metadata->>'project_id' = $2
                AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY metadata->>'query'->>'query'->>'query'
                ORDER BY frequency DESC
                LIMIT 10
            """, tenant_id, project_id, days)
            
            return {
                "total_queries": stats['total_queries'] or 0,
                "avg_processing_time_ms": float(stats['avg_processing_time'] or 0),
                "avg_confidence": float(stats['avg_confidence'] or 0),
                "high_confidence_percentage": (
                    (stats['high_confidence_queries'] or 0) / max(stats['total_queries'] or 1, 1) * 100
                ),
                "query_trends": [
                    {
                        "date": trend['date'],
                        "query_count": trend['query_count'],
                        "avg_confidence": float(trend['avg_confidence'] or 0)
                    }
                    for trend in trends
                ],
                "top_queries": [
                    {
                        "query": query['query_text'],
                        "frequency": query['frequency'],
                        "avg_confidence": float(query['avg_confidence'] or 0)
                    }
                    for query in top_queries
                ]
            }
            
        except Exception as e:
            logger.error(f"Get analytics error: {e}")
            raise
    
    async def get_performance_metrics(self, project_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get reasoning performance metrics"""
        try:
            # Get recent performance data
            recent_performance = await db.fetchrow("""
                SELECT 
                    AVG((metadata->>'processing_time_ms')::numeric) as avg_response_time,
                    COUNT(CASE WHEN (metadata->>'processing_time_ms')::numeric <= 1000 THEN 1 END) as fast_queries,
                    COUNT(*) as total_queries
                FROM learning_events 
                WHERE tenant_id = $1 
                AND event_type = 'reasoning_query'
                AND metadata->>'project_id' = $2
                AND created_at >= NOW() - INTERVAL '24 hours'
            """, tenant_id, project_id)
            
            # Calculate performance metrics
            total_queries = recent_performance['total_queries'] or 0
            fast_queries = recent_performance['fast_queries'] or 0
            avg_response_time = float(recent_performance['avg_response_time'] or 0)
            
            fast_query_percentage = (fast_queries / max(total_queries, 1)) * 100
            
            return {
                "avg_response_time_ms": avg_response_time,
                "fast_queries_percentage": fast_query_percentage,
                "total_queries_24h": total_queries,
                "performance_score": self._calculate_performance_score(avg_response_time, fast_query_percentage)
            }
            
        except Exception as e:
            logger.error(f"Get performance metrics error: {e}")
            raise
    
    def _calculate_performance_score(self, avg_response_time: float, fast_query_percentage: float) -> float:
        """Calculate overall performance score (0-100)"""
        # Response time score (lower is better)
        time_score = max(0, 100 - (avg_response_time / 10))  # 1000ms = 0 points
        
        # Fast query percentage score
        speed_score = fast_query_percentage
        
        # Weighted average
        return (time_score * 0.6 + speed_score * 0.4)
    
    async def update_feedback_metrics(self, query_id: str, rating: float, tenant_id: str):
        """Update metrics based on user feedback"""
        try:
            # Store feedback
            await db.execute("""
                INSERT INTO learning_events (
                    id, tenant_id, event_type, metadata
                ) VALUES ($1, $2, $3, $4)
            """,
            str(uuid.uuid4()),
            tenant_id,
            "reasoning_feedback",
            json.dumps({
                "query_id": query_id,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            })
            )
            
        except Exception as e:
            logger.error(f"Update feedback metrics error: {e}")
    
    async def get_system_health(self, tenant_id: str) -> Dict[str, Any]:
        """Get reasoning system health"""
        try:
            # Get recent activity
            recent_queries = await db.fetchval("""
                SELECT COUNT(*)
                FROM learning_events 
                WHERE tenant_id = $1 
                AND event_type = 'reasoning_query'
                AND created_at >= NOW() - INTERVAL '1 hour'
            """, tenant_id)
            
            # Get average response time
            avg_response_time = await db.fetchval("""
                SELECT AVG((metadata->>'processing_time_ms')::numeric)
                FROM learning_events 
                WHERE tenant_id = $1 
                AND event_type = 'reasoning_query'
                AND created_at >= NOW() - INTERVAL '24 hours'
            """, tenant_id)
            
            # Determine health status
            issues = []
            recommendations = []
            
            if recent_queries == 0:
                issues.append("No recent reasoning activity")
                recommendations.append("Increase system usage to maintain health")
            
            if avg_response_time and avg_response_time > 2000:
                issues.append("Slow average response time")
                recommendations.append("Optimize queries or upgrade infrastructure")
            
            if recent_queries < 5:
                recommendations.append("Consider improving user engagement")
            
            # Calculate status
            if len(issues) == 0:
                status = "healthy"
            elif len(issues) <= 1:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return {
                "status": status,
                "recent_queries_1h": recent_queries,
                "avg_response_time_ms": float(avg_response_time or 0),
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Get system health error: {e}")
            raise
    
    async def log_query(self, query: Dict[str, Any], result: Dict[str, Any], tenant_id: str):
        """Log query for analytics"""
        # This is already handled in _store_query_record
        pass
    
    async def log_batch_queries(self, queries: List[Dict[str, Any]], results: List[Dict[str, Any]], tenant_id: str):
        """Log batch queries for analytics"""
        try:
            await db.execute("""
                INSERT INTO learning_events (
                    id, tenant_id, event_type, metadata
                ) VALUES ($1, $2, $3, $4)
            """,
            str(uuid.uuid4()),
            tenant_id,
            "batch_reasoning_queries",
            json.dumps({
                "query_count": len(queries),
                "success_count": len([r for r in results if r.get("success")]),
                "timestamp": datetime.now().isoformat()
            })
            )
            
        except Exception as e:
            logger.error(f"Log batch queries error: {e}")
