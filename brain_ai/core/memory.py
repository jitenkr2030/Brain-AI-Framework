"""
Long-term Memory System
Persistent, experience-based memory system for the brain-inspired AI framework.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import asyncio
from loguru import logger

from core.learning import LearningEngine
from storage.persistence import PersistenceManager


class MemoryType(Enum):
    """Types of memories"""
    EPISODIC = "episodic"  # Specific experiences/events
    SEMANTIC = "semantic"   # General knowledge
    PROCEDURAL = "procedural"  # How-to knowledge
    WORKING = "working"     # Temporary working memory
    ASSOCIATIVE = "associative"  # Linked memories


class MemoryStrength(Enum):
    """Memory strength levels"""
    WEAK = 0.2
    MODERATE = 0.5
    STRONG = 0.8
    VERY_STRONG = 1.0


@dataclass
class MemoryItem:
    """Represents a single memory item"""
    id: str
    pattern_signature: str
    memory_type: MemoryType
    content: Dict[str, Any]
    context: Dict[str, Any]
    strength: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    associations: List[str]  # IDs of associated memories
    tags: List[str]
    confidence: float
    decay_rate: float = 0.001
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pattern_signature": self.pattern_signature,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "context": self.context,
            "strength": self.strength,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "created_at": self.created_at.isoformat(),
            "associations": self.associations,
            "tags": self.tags,
            "confidence": self.confidence,
            "decay_rate": self.decay_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        return cls(
            id=data["id"],
            pattern_signature=data["pattern_signature"],
            memory_type=MemoryType(data["memory_type"]),
            content=data["content"],
            context=data["context"],
            strength=data["strength"],
            access_count=data["access_count"],
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            associations=data["associations"],
            tags=data["tags"],
            confidence=data["confidence"],
            decay_rate=data.get("decay_rate", 0.001)
        )
    
    def access(self):
        """Record memory access and update strength"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        # Increase strength slightly with each access
        self.strength = min(1.0, self.strength + 0.01)
    
    def decay(self, days_passed: int):
        """Apply time-based decay to memory strength"""
        decay_amount = self.decay_rate * days_passed
        self.strength = max(0.0, self.strength - decay_amount)


@dataclass
class MemoryQuery:
    """Query for memory retrieval"""
    pattern_signature: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    context: Optional[Dict[str, Any]] = None
    min_strength: float = 0.1
    tags: Optional[List[str]] = None
    limit: int = 10
    include_associations: bool = True


class MemoryStore:
    """
    Long-term Memory System
    
    Provides persistent storage and retrieval of memories with:
    - Pattern-based retrieval
    - Contextual association
    - Strength-based activation
    - Time-based decay
    - Incremental learning
    """
    
    def __init__(self, persistence_manager: PersistenceManager):
        self.persistence_manager = persistence_manager
        self.learning_engine: Optional[LearningEngine] = None
        
        # In-memory cache for fast access
        self._memory_cache: Dict[str, MemoryItem] = {}
        self._pattern_index: Dict[str, List[str]] = {}
        self._association_graph: Dict[str, List[str]] = {}
        
        # Statistics
        self.stats = {
            "total_memories": 0,
            "retrieval_operations": 0,
            "storage_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def set_learning_engine(self, learning_engine: LearningEngine):
        """Set the learning engine for memory updates"""
        self.learning_engine = learning_engine
    
    async def initialize(self):
        """Initialize the memory store"""
        logger.info("🧠 Initializing memory store...")
        
        # Load existing memories from persistent storage
        await self._load_memories()
        
        # Build indices
        await self._build_indices()
        
        logger.info(f"✅ Memory store initialized with {self.stats['total_memories']} memories")
    
    async def store(self, memory_item: MemoryItem) -> str:
        """
        Store a memory item
        
        Args:
            memory_item: Memory item to store
            
        Returns:
            Memory ID
        """
        try:
            # Add to cache
            self._memory_cache[memory_item.id] = memory_item
            
            # Update pattern index
            if memory_item.pattern_signature not in self._pattern_index:
                self._pattern_index[memory_item.pattern_signature] = []
            if memory_item.id not in self._pattern_index[memory_item.pattern_signature]:
                self._pattern_index[memory_item.pattern_signature].append(memory_item.id)
            
            # Update association graph
            if memory_item.id not in self._association_graph:
                self._association_graph[memory_item.id] = []
            
            # Persist to storage
            await self.persistence_manager.store_memory(memory_item.to_dict())
            
            self.stats["storage_operations"] += 1
            self.stats["total_memories"] += 1
            
            logger.debug(f"Stored memory {memory_item.id} with pattern {memory_item.pattern_signature}")
            return memory_item.id
            
        except Exception as e:
            logger.error(f"Error storing memory {memory_item.id}: {e}")
            raise
    
    async def retrieve(self, pattern: str, context: Dict[str, Any]) -> List[MemoryItem]:
        """
        Retrieve memories based on pattern and context
        
        Args:
            pattern: Pattern signature to match
            context: Contextual information
            
        Returns:
            List of matching memory items
        """
        query = MemoryQuery(
            pattern_signature=pattern,
            context=context,
            min_strength=0.1,
            limit=20
        )
        
        return await self.retrieve_by_query(query)
    
    async def retrieve_by_query(self, query: MemoryQuery) -> List[MemoryItem]:
        """
        Retrieve memories using a complex query
        
        Args:
            query: Memory query object
            
        Returns:
            List of matching memory items
        """
        try:
            self.stats["retrieval_operations"] += 1
            candidates = []
            
            # Find candidates based on pattern signature
            if query.pattern_signature:
                pattern_ids = self._pattern_index.get(query.pattern_signature, [])
                for memory_id in pattern_ids:
                    if memory_id in self._memory_cache:
                        candidates.append(self._memory_cache[memory_id])
            
            # If no pattern specified, search all memories
            if not query.pattern_signature:
                candidates = list(self._memory_cache.values())
            
            # Filter by criteria
            filtered_memories = []
            for memory in candidates:
                # Check strength threshold
                if memory.strength < query.min_strength:
                    continue
                
                # Check memory type
                if query.memory_type and memory.memory_type != query.memory_type:
                    continue
                
                # Check tags
                if query.tags and not any(tag in memory.tags for tag in query.tags):
                    continue
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(memory, query)
                
                if relevance_score > 0:
                    memory_item = memory
                    memory_item.relevance_score = relevance_score
                    filtered_memories.append(memory_item)
            
            # Sort by relevance and strength
            filtered_memories.sort(
                key=lambda m: (m.relevance_score, m.strength), 
                reverse=True
            )
            
            # Limit results
            result = filtered_memories[:query.limit]
            
            # Record access for retrieved memories
            for memory in result:
                memory.access()
                # Persist the updated memory
                await self.persistence_manager.store_memory(memory.to_dict())
            
            logger.debug(f"Retrieved {len(result)} memories for query")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            raise
    
    async def update_strength(self, memory_id: str, strength_change: float):
        """
        Update memory strength (called by learning engine)
        
        Args:
            memory_id: ID of memory to update
            strength_change: Change in strength (-1.0 to 1.0)
        """
        try:
            if memory_id in self._memory_cache:
                memory = self._memory_cache[memory_id]
                old_strength = memory.strength
                memory.strength = max(0.0, min(1.0, memory.strength + strength_change))
                
                # Persist the update
                await self.persistence_manager.store_memory(memory.to_dict())
                
                logger.debug(f"Updated memory {memory_id} strength: {old_strength} -> {memory.strength}")
            
        except Exception as e:
            logger.error(f"Error updating memory strength: {e}")
            raise
    
    async def create_association(self, memory_id_1: str, memory_id_2: str, strength: float = 0.5):
        """
        Create association between two memories
        
        Args:
            memory_id_1: First memory ID
            memory_id_2: Second memory ID
            strength: Association strength
        """
        try:
            if memory_id_1 in self._memory_cache and memory_id_2 in self._memory_cache:
                memory1 = self._memory_cache[memory_id_1]
                memory2 = self._memory_cache[memory_id_2]
                
                # Add association
                if memory_id_2 not in memory1.associations:
                    memory1.associations.append(memory_id_2)
                if memory_id_1 not in memory2.associations:
                    memory2.associations.append(memory_id_1)
                
                # Update association graph
                if memory_id_1 not in self._association_graph:
                    self._association_graph[memory_id_1] = []
                if memory_id_2 not in self._association_graph[memory_id_1]:
                    self._association_graph[memory_id_1].append(memory_id_2)
                
                # Persist changes
                await self.persistence_manager.store_memory(memory1.to_dict())
                await self.persistence_manager.store_memory(memory2.to_dict())
                
                logger.debug(f"Created association between {memory_id_1} and {memory_id_2}")
            
        except Exception as e:
            logger.error(f"Error creating association: {e}")
            raise
    
    async def get_associated_memories(self, memory_id: str) -> List[MemoryItem]:
        """
        Get memories associated with a given memory
        
        Args:
            memory_id: Memory ID to find associations for
            
        Returns:
            List of associated memories
        """
        try:
            if memory_id not in self._association_graph:
                return []
            
            associated_ids = self._association_graph[memory_id]
            associated_memories = []
            
            for assoc_id in associated_ids:
                if assoc_id in self._memory_cache:
                    associated_memories.append(self._memory_cache[assoc_id])
            
            return associated_memories
            
        except Exception as e:
            logger.error(f"Error getting associated memories: {e}")
            raise
    
    async def apply_time_decay(self):
        """Apply time-based decay to all memories"""
        try:
            current_time = datetime.now()
            decayed_memories = []
            
            for memory in self._memory_cache.values():
                days_passed = (current_time - memory.last_accessed).days
                if days_passed > 0:
                    old_strength = memory.strength
                    memory.decay(days_passed)
                    
                    if memory.strength != old_strength:
                        decayed_memories.append(memory)
                        await self.persistence_manager.store_memory(memory.to_dict())
            
            if decayed_memories:
                logger.info(f"Applied decay to {len(decayed_memories)} memories")
            
        except Exception as e:
            logger.error(f"Error applying time decay: {e}")
            raise
    
    def _calculate_relevance(self, memory: MemoryItem, query: MemoryQuery) -> float:
        """
        Calculate relevance score between memory and query
        
        Args:
            memory: Memory item
            query: Query object
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        relevance = 0.0
        
        # Pattern signature match
        if query.pattern_signature == memory.pattern_signature:
            relevance += 0.4
        
        # Context similarity
        if query.context:
            context_overlap = self._calculate_context_overlap(memory.context, query.context)
            relevance += context_overlap * 0.3
        
        # Tag overlap
        if query.tags:
            tag_overlap = len(set(memory.tags) & set(query.tags)) / len(query.tags)
            relevance += tag_overlap * 0.2
        
        # Memory type preference
        if query.memory_type == memory.memory_type:
            relevance += 0.1
        
        return min(1.0, relevance)
    
    def _calculate_context_overlap(self, memory_context: Dict[str, Any], query_context: Dict[str, Any]) -> float:
        """Calculate overlap between memory context and query context"""
        if not memory_context or not query_context:
            return 0.0
        
        common_keys = set(memory_context.keys()) & set(query_context.keys())
        if not common_keys:
            return 0.0
        
        matches = 0
        for key in common_keys:
            if memory_context[key] == query_context[key]:
                matches += 1
        
        return matches / len(common_keys)
    
    async def _load_memories(self):
        """Load memories from persistent storage"""
        try:
            memories_data = await self.persistence_manager.load_all_memories()
            
            for memory_data in memories_data:
                memory_item = MemoryItem.from_dict(memory_data)
                self._memory_cache[memory_item.id] = memory_item
            
            logger.info(f"Loaded {len(memories_data)} memories from storage")
            
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            raise
    
    async def _build_indices(self):
        """Build search indices"""
        try:
            # Build pattern index
            for memory_id, memory in self._memory_cache.items():
                if memory.pattern_signature not in self._pattern_index:
                    self._pattern_index[memory.pattern_signature] = []
                self._pattern_index[memory.pattern_signature].append(memory_id)
            
            # Build association graph
            for memory_id, memory in self._memory_cache.items():
                self._association_graph[memory_id] = memory.associations.copy()
            
            logger.info("Built search indices")
            
        except Exception as e:
            logger.error(f"Error building indices: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        memory_types = {}
        for memory in self._memory_cache.values():
            memory_type = memory.memory_type.value
            memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
        
        return {
            "total_memories": len(self._memory_cache),
            "memory_types": memory_types,
            "pattern_index_size": len(self._pattern_index),
            "association_count": sum(len(assocs) for assocs in self._association_graph.values()),
            "average_strength": sum(m.strength for m in self._memory_cache.values()) / len(self._memory_cache),
            "stats": self.stats.copy()
        }
    
    def create_memory_item(
        self,
        pattern_signature: str,
        content: Dict[str, Any],
        context: Dict[str, Any],
        memory_type: MemoryType = MemoryType.EPISODIC,
        tags: Optional[List[str]] = None,
        strength: float = 0.5,
        confidence: float = 0.5
    ) -> MemoryItem:
        """Create a new memory item"""
        return MemoryItem(
            id=str(uuid.uuid4()),
            pattern_signature=pattern_signature,
            memory_type=memory_type,
            content=content,
            context=context,
            strength=strength,
            access_count=0,
            last_accessed=datetime.now(),
            created_at=datetime.now(),
            associations=[],
            tags=tags or [],
            confidence=confidence
        )