"""
Memory Service
Core service for Brain AI memory operations, vector search, and analytics
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from app.database import db
from app.config import settings

logger = logging.getLogger(__name__)


class MemoryService:
    """Memory service for Brain AI operations"""
    
    def __init__(self):
        self.vector_db_enabled = settings.ENABLE_VECTOR_SEARCH
        self.embedding_model = None
        self.pinecone_index = None
        
        if self.vector_db_enabled:
            self._init_vector_db()
    
    def _init_vector_db(self):
        """Initialize vector database connection"""
        try:
            if settings.PINECONE_API_KEY:
                import pinecone
                pinecone.init(
                    api_key=settings.PINECONE_API_KEY,
                    environment=settings.PINECONE_ENVIRONMENT
                )
                
                # Create or get indexes for different memory types
                self.pinecone_index = pinecone.Index("brain-ai-memories")
                logger.info("✅ Vector database initialized")
            else:
                logger.warning("⚠️ Pinecone API key not provided, vector search disabled")
                self.vector_db_enabled = False
                
        except ImportError:
            logger.warning("⚠️ Pinecone client not installed, vector search disabled")
            self.vector_db_enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector database: {e}")
            self.vector_db_enabled = False
    
    async def store_embedding(self, memory_id: str, content: Dict[str, Any], memory_type: str):
        """Store vector embedding for a memory"""
        if not self.vector_db_enabled:
            return
        
        try:
            # Generate embedding (simplified - in production use actual embedding model)
            embedding = self._generate_embedding(content)
            
            # Store in Pinecone
            self.pinecone_index.upsert(
                vectors=[{
                    "id": memory_id,
                    "values": embedding,
                    "metadata": {
                        "memory_type": memory_type,
                        "content_hash": hash(json.dumps(content, sort_keys=True))
                    }
                }]
            )
            
        except Exception as e:
            logger.error(f"Failed to store embedding for memory {memory_id}: {e}")
    
    async def update_embedding(self, memory_id: str, content: Dict[str, Any], memory_type: str):
        """Update vector embedding for a memory"""
        if not self.vector_db_enabled:
            return
        
        try:
            embedding = self._generate_embedding(content)
            
            self.pinecone_index.update(
                id=memory_id,
                values=embedding,
                metadata={
                    "memory_type": memory_type,
                    "content_hash": hash(json.dumps(content, sort_keys=True))
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update embedding for memory {memory_id}: {e}")
    
    async def delete_embedding(self, memory_id: str):
        """Delete vector embedding for a memory"""
        if not self.vector_db_enabled:
            return
        
        try:
            self.pinecone_index.delete(ids=[memory_id])
            
        except Exception as e:
            logger.error(f"Failed to delete embedding for memory {memory_id}: {e}")
    
    async def semantic_search(self, query: str, tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        if not self.vector_db_enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding({"text": query})
            
            # Search in Pinecone
            search_results = self.pinecone_index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                filter={
                    "tenant_id": tenant_id  # Multi-tenant filtering
                }
            )
            
            # Convert to MemorySearchResult format
            results = []
            for match in search_results['matches']:
                # Get memory from database
                memory = await db.fetchrow(
                    "SELECT * FROM memories WHERE id = $1 AND tenant_id = $2",
                    match['id'],
                    tenant_id
                )
                
                if memory:
                    results.append({
                        "memory": {
                            "id": memory['id'],
                            "pattern_signature": memory['pattern_signature'],
                            "memory_type": memory['memory_type'],
                            "content": json.loads(memory['content']),
                            "context": json.loads(memory['context']),
                            "strength": memory['strength'],
                            "access_count": memory['access_count'],
                            "tags": memory['tags'],
                            "confidence": memory['confidence'],
                            "created_at": memory['created_at'],
                            "updated_at": memory['updated_at']
                        },
                        "similarity_score": match['score'],
                        "matched_fields": ["content"]
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    def _generate_embedding(self, content: Dict[str, Any]) -> List[float]:
        """Generate embedding for content (simplified implementation)"""
        # This is a simplified embedding generation
        # In production, use actual embedding models like sentence-transformers
        text = str(content.get('text', ''))
        
        # Simple hash-based embedding (for demo purposes only)
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to list of floats (simplified)
        embedding = [float(b) / 255.0 for b in hash_bytes[:768]]  # 768 dimensions
        return embedding
    
    async def get_memory_statistics(self, project_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive memory statistics for a project"""
        try:
            # Basic counts
            stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(strength) as avg_strength,
                    AVG(confidence) as avg_confidence,
                    SUM(access_count) as total_access_count
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
            """, tenant_id, project_id)
            
            # Memories by type
            memories_by_type = await db.fetch("""
                SELECT memory_type, COUNT(*) as count
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                GROUP BY memory_type
            """, tenant_id, project_id)
            
            # Most accessed memories
            most_accessed = await db.fetch("""
                SELECT pattern_signature, access_count, strength
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                ORDER BY access_count DESC
                LIMIT 5
            """, tenant_id, project_id)
            
            # Strongest memories
            strongest = await db.fetch("""
                SELECT pattern_signature, strength, access_count
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                ORDER BY strength DESC
                LIMIT 5
            """, tenant_id, project_id)
            
            # Newest memories
            newest = await db.fetch("""
                SELECT pattern_signature, created_at, strength
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                ORDER BY created_at DESC
                LIMIT 5
            """, tenant_id, project_id)
            
            # Oldest memories
            oldest = await db.fetch("""
                SELECT pattern_signature, created_at, strength
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                ORDER BY created_at ASC
                LIMIT 5
            """, tenant_id, project_id)
            
            return {
                "total_memories": stats['total_memories'] or 0,
                "avg_strength": float(stats['avg_strength'] or 0),
                "avg_confidence": float(stats['avg_confidence'] or 0),
                "total_access_count": stats['total_access_count'] or 0,
                "memories_by_type": {row['memory_type']: row['count'] for row in memories_by_type},
                "most_accessed_memories": [
                    {
                        "pattern_signature": row['pattern_signature'],
                        "access_count": row['access_count'],
                        "strength": row['strength']
                    }
                    for row in most_accessed
                ],
                "strongest_memories": [
                    {
                        "pattern_signature": row['pattern_signature'],
                        "strength": row['strength'],
                        "access_count": row['access_count']
                    }
                    for row in strongest
                ],
                "newest_memories": [
                    {
                        "pattern_signature": row['pattern_signature'],
                        "created_at": row['created_at'],
                        "strength": row['strength']
                    }
                    for row in newest
                ],
                "oldest_memories": [
                    {
                        "pattern_signature": row['pattern_signature'],
                        "created_at": row['created_at'],
                        "strength": row['strength']
                    }
                    for row in oldest
                ]
            }
            
        except Exception as e:
            logger.error(f"Get memory statistics error: {e}")
            raise
    
    async def get_memory_analytics(self, project_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get memory analytics and insights"""
        try:
            # Growth trend (last 30 days)
            growth_trend = await db.fetch("""
                SELECT 
                    DATE_TRUNC('day', created_at) as date,
                    COUNT(*) as count
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                    AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE_TRUNC('day', created_at)
                ORDER BY date
            """, tenant_id, project_id)
            
            # Type distribution
            type_distribution = await db.fetch("""
                SELECT memory_type, COUNT(*) as count
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                GROUP BY memory_type
            """, tenant_id, project_id)
            
            # Strength distribution
            strength_distribution = await db.fetch("""
                SELECT 
                    CASE 
                        WHEN strength >= 0.8 THEN 'High (0.8-1.0)'
                        WHEN strength >= 0.6 THEN 'Medium-High (0.6-0.8)'
                        WHEN strength >= 0.4 THEN 'Medium (0.4-0.6)'
                        WHEN strength >= 0.2 THEN 'Low-Medium (0.2-0.4)'
                        ELSE 'Low (0.0-0.2)'
                    END as strength_range,
                    COUNT(*) as count
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                GROUP BY 
                    CASE 
                        WHEN strength >= 0.8 THEN 'High (0.8-1.0)'
                        WHEN strength >= 0.6 THEN 'Medium-High (0.6-0.8)'
                        WHEN strength >= 0.4 THEN 'Medium (0.4-0.6)'
                        WHEN strength >= 0.2 THEN 'Low-Medium (0.2-0.4)'
                        ELSE 'Low (0.0-0.2)'
                    END
            """, tenant_id, project_id)
            
            # Tag frequency
            tag_frequency = await db.fetch("""
                SELECT unnest(tags) as tag, COUNT(*) as frequency
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                    AND array_length(tags, 1) IS NOT NULL
                GROUP BY unnest(tags)
                ORDER BY frequency DESC
                LIMIT 20
            """, tenant_id, project_id)
            
            # Access patterns (last 7 days)
            access_patterns = await db.fetch("""
                SELECT 
                    DATE_TRUNC('hour', last_accessed) as hour,
                    COUNT(*) as access_count
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
                    AND last_accessed >= NOW() - INTERVAL '7 days'
                GROUP BY DATE_TRUNC('hour', last_accessed)
                ORDER BY hour
            """, tenant_id, project_id)
            
            # Learning effectiveness (based on strength improvements)
            learning_effectiveness = await db.fetchval("""
                SELECT 
                    AVG(
                        CASE 
                            WHEN access_count > 0 THEN strength * access_count
                            ELSE strength
                        END
                    ) as effectiveness_score
                FROM memories 
                WHERE tenant_id = $1 AND project_id = $2
            """, tenant_id, project_id)
            
            return {
                "growth_trend": [
                    {
                        "date": row['date'],
                        "count": row['count']
                    }
                    for row in growth_trend
                ],
                "type_distribution": {row['memory_type']: row['count'] for row in type_distribution},
                "strength_distribution": {row['strength_range']: row['count'] for row in strength_distribution},
                "tag_frequency": {row['tag']: row['frequency'] for row in tag_frequency},
                "access_patterns": [
                    {
                        "hour": row['hour'],
                        "access_count": row['access_count']
                    }
                    for row in access_patterns
                ],
                "learning_effectiveness": float(learning_effectiveness or 0)
            }
            
        except Exception as e:
            logger.error(f"Get memory analytics error: {e}")
            raise
    
    async def get_system_health(self, tenant_id: str) -> Dict[str, Any]:
        """Get memory system health metrics"""
        try:
            # Get basic health metrics
            health_stats = await db.fetchrow("""
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(strength) as avg_strength,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN last_accessed >= NOW() - INTERVAL '24 hours' THEN 1 END) as recent_accesses,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as recent_creations
                FROM memories 
                WHERE tenant_id = $1
            """, tenant_id)
            
            # Calculate health status
            total_memories = health_stats['total_memories'] or 0
            avg_strength = float(health_stats['avg_strength'] or 0)
            avg_confidence = float(health_stats['avg_confidence'] or 0)
            recent_accesses = health_stats['recent_accesses'] or 0
            
            # Determine health status
            issues = []
            if total_memories == 0:
                issues.append("No memories found")
            if avg_strength < 0.3:
                issues.append("Low average memory strength")
            if avg_confidence < 0.3:
                issues.append("Low average confidence")
            if recent_accesses == 0 and total_memories > 10:
                issues.append("No recent memory access activity")
            
            # Calculate access rate
            access_rate = recent_accesses / 24 if total_memories > 0 else 0
            
            # Determine overall status
            if len(issues) == 0:
                status = "healthy"
            elif len(issues) <= 2:
                status = "degraded"
            else:
                status = "unhealthy"
            
            # Generate recommendations
            recommendations = []
            if avg_strength < 0.5:
                recommendations.append("Consider providing more feedback to improve memory strength")
            if recent_accesses < total_memories * 0.1:
                recommendations.append("Increase memory usage through queries and interactions")
            if total_memories > 1000 and access_rate < 1:
                recommendations.append("Consider organizing memories into multiple projects")
            
            return {
                "status": status,
                "total_memories": total_memories,
                "avg_strength": avg_strength,
                "avg_confidence": avg_confidence,
                "access_rate_per_hour": access_rate,
                "learning_events_per_hour": recent_accesses / 24 if recent_accesses > 0 else 0,
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Get system health error: {e}")
            raise
    
    async def cleanup_old_memories(self, tenant_id: str, days_old: int = 365):
        """Clean up old, unused memories"""
        try:
            # Find memories that haven't been accessed and are old
            old_memories = await db.fetch("""
                SELECT id, pattern_signature, strength
                FROM memories 
                WHERE tenant_id = $1
                    AND last_accessed IS NULL
                    AND created_at <= NOW() - INTERVAL '%s days'
                    AND strength < 0.3
                ORDER BY strength ASC, created_at ASC
                LIMIT 1000
            """, tenant_id, days_old)
            
            deleted_count = 0
            for memory in old_memories:
                try:
                    # Delete memory
                    await db.execute(
                        "DELETE FROM memories WHERE id = $1 AND tenant_id = $2",
                        memory['id'],
                        tenant_id
                    )
                    
                    # Delete vector embedding
                    if self.vector_db_enabled:
                        await self.delete_embedding(memory['id'])
                    
                    deleted_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to delete memory {memory['id']}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old memories for tenant {tenant_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cleanup old memories error: {e}")
            raise
