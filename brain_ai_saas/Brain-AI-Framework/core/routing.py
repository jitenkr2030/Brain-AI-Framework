"""
Sparse Activation Logic
Activates only relevant memories using sparse neural network principles.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import random
from enum import Enum
from loguru import logger

from core.memory import MemoryItem


class ActivationMethod(Enum):
    """Methods for memory activation"""
    THRESHOLD = "threshold"           # Strength-based threshold
    WINNER_TAKES_ALL = "winner_takes_all"  # Top K activation
    SPARSITY_CONSTRAINT = "sparsity"  # Maximum active memories
    ADAPTIVE = "adaptive"             # Adaptive activation
    COMPETITIVE = "competitive"       # Competitive activation


class ActivationState(Enum):
    """States of memory activation"""
    DORMANT = "dormant"
    WEAKLY_ACTIVE = "weakly_active"
    ACTIVE = "active"
    STRONGLY_ACTIVE = "strongly_active"
    OVERLOAD = "overload"


@dataclass
class ActivationContext:
    """Context for memory activation"""
    input_intensity: float = 1.0
    available_activation_budget: float = 1.0
    target_activation_count: int = 5
    activation_method: ActivationMethod = ActivationMethod.THRESHOLD
    quality_threshold: float = 0.1
    time_bonus: float = 0.0
    recency_weight: float = 0.1


@dataclass
class ActivationResult:
    """Result of memory activation"""
    active_memories: List[MemoryItem]
    activation_scores: Dict[str, float]
    total_activation_budget_used: float
    activation_method_used: ActivationMethod
    activation_state: ActivationState
    activation_timestamp: datetime


class SparseRouter:
    """
    Sparse Activation Router
    
    Implements brain-inspired sparse activation:
    - Only a small fraction of memories activate at once
    - Competitive activation mechanisms
    - Adaptive threshold management
    - Activation budget constraints
    - Winner-takes-all dynamics
    """
    
    def __init__(self):
        # Activation parameters
        self.global_activation_threshold = 0.1
        self.max_active_memories = 10
        self.activation_decay_rate = 0.95
        
        # Adaptive parameters
        self.adaptation_rate = 0.01
        self.target_sparsity = 0.05  # 5% of memories should be active
        
        # Activation history for learning
        self.activation_history: List[ActivationResult] = []
        self.recent_activations: Dict[str, List[datetime]] = {}
        
        # Performance metrics
        self.stats = {
            "total_activations": 0,
            "average_active_memories": 0,
            "threshold_adjustments": 0,
            "overload_events": 0,
            "sparsity_violations": 0
        }
    
    def activate(
        self, 
        memories: List[MemoryItem], 
        context: Dict[str, Any]
    ) -> List[MemoryItem]:
        """
        Activate relevant memories using sparse activation
        
        Args:
            memories: Candidate memories to activate
            context: Contextual information for activation
            
        Returns:
            List of activated memories
        """
        try:
            # Create activation context
            activation_context = self._create_activation_context(context, len(memories))
            
            # Calculate activation scores
            activation_scores = self._calculate_activation_scores(memories, activation_context)
            
            # Apply activation method
            activated_memories = self._apply_activation_method(
                memories, activation_scores, activation_context
            )
            
            # Record activation
            result = ActivationResult(
                active_memories=activated_memories,
                activation_scores=activation_scores,
                total_activation_budget_used=self._calculate_budget_usage(activated_memories),
                activation_method_used=activation_context.activation_method,
                activation_state=self._determine_activation_state(activated_memories, activation_context),
                activation_timestamp=datetime.now()
            )
            
            self._record_activation(result, memories)
            self._adapt_parameters(result, len(memories))
            
            logger.debug(f"Activated {len(activated_memories)} memories from {len(memories)} candidates")
            
            return activated_memories
            
        except Exception as e:
            logger.error(f"Error in sparse activation: {e}")
            # Fallback to simple threshold activation
            return [m for m in memories if m.strength > self.global_activation_threshold]
    
    def _create_activation_context(
        self, 
        context: Dict[str, Any], 
        candidate_count: int
    ) -> ActivationContext:
        """Create activation context from input context"""
        
        # Extract relevant parameters
        input_intensity = context.get("intensity", "medium")
        if isinstance(input_intensity, str):
            intensity_map = {"low": 0.5, "medium": 1.0, "high": 1.5, "critical": 2.0}
            input_intensity = intensity_map.get(input_intensity, 1.0)
        
        # Determine target activation count based on candidate count
        target_activation = min(
            max(1, int(candidate_count * self.target_sparsity)),
            self.max_active_memories
        )
        
        # Choose activation method based on context
        activation_method = ActivationMethod.THRESHOLD
        if context.get("method"):
            try:
                activation_method = ActivationMethod(context["method"])
            except ValueError:
                pass
        
        return ActivationContext(
            input_intensity=input_intensity,
            target_activation_count=target_activation,
            activation_method=activation_method,
            quality_threshold=self.global_activation_threshold,
            time_bonus=self._calculate_time_bonus(context),
            recency_weight=context.get("recency_weight", 0.1)
        )
    
    def _calculate_activation_scores(
        self, 
        memories: List[MemoryItem], 
        context: ActivationContext
    ) -> Dict[str, float]:
        """Calculate activation scores for all memories"""
        
        scores = {}
        current_time = datetime.now()
        
        for memory in memories:
            # Base score from memory strength
            base_score = memory.strength
            
            # Context relevance bonus
            context_bonus = self._calculate_context_relevance(memory, context)
            
            # Recency bonus (recently accessed memories get boost)
            recency_bonus = self._calculate_recency_bonus(memory, current_time, context)
            
            # Input intensity scaling
            intensity_bonus = context.input_intensity - 1.0
            
            # Competition factor (prevent too many high-scoring memories)
            competition_factor = self._calculate_competition_factor(memory, memories)
            
            # Calculate final score
            final_score = (
                base_score * 0.4 +
                context_bonus * 0.3 +
                recency_bonus * 0.2 +
                intensity_bonus * 0.1
            ) * competition_factor
            
            # Apply minimum threshold
            final_score = max(0.0, final_score)
            
            scores[memory.id] = final_score
        
        return scores
    
    def _apply_activation_method(
        self, 
        memories: List[MemoryItem], 
        scores: Dict[str, float], 
        context: ActivationContext
    ) -> List[MemoryItem]:
        """Apply specific activation method"""
        
        method = context.activation_method
        
        if method == ActivationMethod.THRESHOLD:
            return self._threshold_activation(memories, scores, context)
        elif method == ActivationMethod.WINNER_TAKES_ALL:
            return self._winner_takes_all_activation(memories, scores, context)
        elif method == ActivationMethod.SPARSITY_CONSTRAINT:
            return self._sparsity_activation(memories, scores, context)
        elif method == ActivationMethod.ADAPTIVE:
            return self._adaptive_activation(memories, scores, context)
        elif method == ActivationMethod.COMPETITIVE:
            return self._competitive_activation(memories, scores, context)
        else:
            # Default to threshold
            return self._threshold_activation(memories, scores, context)
    
    def _threshold_activation(
        self, 
        memories: List[MemoryItem], 
        scores: Dict[str, float], 
        context: ActivationContext
    ) -> List[MemoryItem]:
        """Threshold-based activation"""
        
        threshold = max(context.quality_threshold, self.global_activation_threshold)
        activated = []
        
        for memory in memories:
            score = scores[memory.id]
            if score >= threshold:
                activated.append(memory)
            
            # Respect budget constraint
            if len(activated) >= context.target_activation_count:
                break
        
        return activated
    
    def _winner_takes_all_activation(
        self, 
        memories: List[MemoryItem], 
        scores: Dict[str, float], 
        context: ActivationContext
    ) -> List[MemoryItem]:
        """Winner-takes-all activation (top K)"""
        
        # Sort memories by score
        sorted_memories = sorted(
            memories, 
            key=lambda m: scores[m.id], 
            reverse=True
        )
        
        # Take top K memories
        k = min(context.target_activation_count, len(sorted_memories))
        return sorted_memories[:k]
    
    def _sparsity_activation(
        self, 
        memories: List[MemoryItem], 
        scores: Dict[str, float], 
        context: ActivationContext
    ) -> List[MemoryItem]:
        """Sparsity-constrained activation"""
        
        # Calculate dynamic threshold to achieve target sparsity
        total_memories = len(memories)
        target_active = max(1, int(total_memories * self.target_sparsity))
        
        # Sort by score and take top target
        sorted_memories = sorted(
            memories, 
            key=lambda m: scores[m.id], 
            reverse=True
        )
        
        return sorted_memories[:target_active]
    
    def _adaptive_activation(
        self, 
        memories: List[MemoryItem], 
        scores: Dict[str, float], 
        context: ActivationContext
    ) -> List[MemoryItem]:
        """Adaptive activation that adjusts to context"""
        
        # Analyze score distribution
        score_values = list(scores.values())
        if not score_values:
            return []
        
        mean_score = sum(score_values) / len(score_values)
        std_score = math.sqrt(sum((s - mean_score) ** 2 for s in score_values) / len(score_values))
        
        # Adaptive threshold based on distribution
        if std_score > 0:
            threshold = mean_score + 0.5 * std_score
        else:
            threshold = mean_score * 0.8
        
        # Apply threshold and limit by target count
        activated = [
            memory for memory in memories 
            if scores[memory.id] >= threshold
        ][:context.target_activation_count]
        
        return activated
    
    def _competitive_activation(
        self, 
        memories: List[MemoryItem], 
        scores: Dict[str, float], 
        context: ActivationContext
    ) -> List[MemoryItem]:
        """Competitive activation with lateral inhibition"""
        
        activated = []
        remaining_budget = context.available_activation_budget
        
        # Sort by score
        sorted_memories = sorted(
            memories, 
            key=lambda m: scores[m.id], 
            reverse=True
        )
        
        for memory in sorted_memories:
            score = scores[memory.id]
            
            # Check if we have budget for this memory
            activation_cost = self._calculate_activation_cost(memory, score)
            
            if activation_cost <= remaining_budget:
                activated.append(memory)
                remaining_budget -= activation_cost
                
                # Apply lateral inhibition to remaining memories
                self._apply_lateral_inhibition(sorted_memories, memory, score)
            
            if len(activated) >= context.target_activation_count:
                break
        
        return activated
    
    def _calculate_context_relevance(self, memory: MemoryItem, context: ActivationContext) -> float:
        """Calculate context relevance score"""
        
        relevance = 0.0
        
        # Check context state match
        memory_state = memory.context.get("state", "unknown")
        input_state = context.__dict__.get("state", "normal")
        
        if memory_state == input_state:
            relevance += 0.3
        
        # Check intensity match
        memory_intensity = memory.context.get("intensity", "medium")
        if isinstance(memory_intensity, str):
            intensity_map = {"low": 0.5, "medium": 1.0, "high": 1.5, "critical": 2.0}
            memory_intensity = intensity_map.get(memory_intensity, 1.0)
        
        intensity_diff = abs(memory_intensity - context.input_intensity)
        if intensity_diff < 0.5:
            relevance += 0.2
        
        # Check tag overlap
        context_tags = context.__dict__.get("tags", [])
        tag_overlap = len(set(memory.tags) & set(context_tags))
        if tag_overlap > 0:
            relevance += 0.2 * min(1.0, tag_overlap / 3.0)
        
        return min(1.0, relevance)
    
    def _calculate_recency_bonus(
        self, 
        memory: MemoryItem, 
        current_time: datetime, 
        context: ActivationContext
    ) -> float:
        """Calculate recency bonus for recently accessed memories"""
        
        time_since_access = current_time - memory.last_accessed
        days_since = time_since_access.days
        
        # Exponential decay for recency bonus
        if days_since == 0:
            return 0.5  # Accessed today
        elif days_since < 7:
            return 0.3 * math.exp(-days_since / 7)  # Recent access
        elif days_since < 30:
            return 0.1 * math.exp(-days_since / 30)  # Less recent
        else:
            return 0.0  # No recency bonus
    
    def _calculate_time_bonus(self, context: Dict[str, Any]) -> float:
        """Calculate time-based bonus"""
        
        # This could be enhanced with time-of-day, day-of-week patterns
        return 0.0
    
    def _calculate_competition_factor(
        self, 
        memory: MemoryItem, 
        all_memories: List[MemoryItem]
    ) -> float:
        """Calculate competition factor to prevent activation of too many similar memories"""
        
        # Simple implementation: reduce score if many memories have similar patterns
        similar_count = 0
        for other_memory in all_memories:
            if (other_memory.id != memory.id and 
                other_memory.pattern_signature == memory.pattern_signature):
                similar_count += 1
        
        # Reduce score based on competition
        competition_penalty = min(0.5, similar_count * 0.1)
        return 1.0 - competition_penalty
    
    def _calculate_budget_usage(self, activated_memories: List[MemoryItem]) -> float:
        """Calculate total activation budget used"""
        
        total_budget = 0.0
        for memory in activated_memories:
            # Higher strength memories cost more to activate
            total_budget += memory.strength * 0.1
        
        return total_budget
    
    def _determine_activation_state(
        self, 
        activated_memories: List[MemoryItem], 
        context: ActivationContext
    ) -> ActivationState:
        """Determine the current activation state"""
        
        if not activated_memories:
            return ActivationState.DORMANT
        
        avg_strength = sum(m.strength for m in activated_memories) / len(activated_memories)
        
        if len(activated_memories) == 0:
            return ActivationState.DORMANT
        elif len(activated_memories) <= 2 and avg_strength > 0.8:
            return ActivationState.STRONGLY_ACTIVE
        elif len(activated_memories) <= 5 and avg_strength > 0.5:
            return ActivationState.ACTIVE
        elif len(activated_memories) <= context.target_activation_count:
            return ActivationState.WEAKLY_ACTIVE
        else:
            return ActivationState.OVERLOAD
    
    def _calculate_activation_cost(self, memory: MemoryItem, score: float) -> float:
        """Calculate the cost of activating a memory"""
        
        # Higher strength and score memories cost more
        return (memory.strength * 0.05) + (score * 0.02)
    
    def _apply_lateral_inhibition(
        self, 
        memories: List[MemoryItem], 
        activated_memory: MemoryItem, 
        score: float
    ):
        """Apply lateral inhibition to competing memories"""
        
        # Reduce scores of competing memories
        for memory in memories:
            if (memory.id != activated_memory.id and 
                memory.pattern_signature == activated_memory.pattern_signature):
                # This would require access to the scores dictionary
                # In a full implementation, this would modify the scores
                pass
    
    def _record_activation(self, result: ActivationResult, candidate_memories: List[MemoryItem]):
        """Record activation for learning and adaptation"""
        
        self.activation_history.append(result)
        
        # Update recent activations
        for memory in result.active_memories:
            if memory.id not in self.recent_activations:
                self.recent_activations[memory.id] = []
            self.recent_activations[memory.id].append(result.activation_timestamp)
        
        # Keep history manageable
        if len(self.activation_history) > 1000:
            self.activation_history = self.activation_history[-500:]
        
        # Update statistics
        self.stats["total_activations"] += 1
        self.stats["average_active_memories"] = (
            (self.stats["average_active_memories"] * (self.stats["total_activations"] - 1) + 
             len(result.active_memories)) / self.stats["total_activations"]
        )
        
        if result.activation_state == ActivationState.OVERLOAD:
            self.stats["overload_events"] += 1
        
        # Check sparsity violations
        sparsity = len(result.active_memories) / max(1, len(candidate_memories))
        if sparsity > self.target_sparsity * 2:
            self.stats["sparsity_violations"] += 1
    
    def _adapt_parameters(self, result: ActivationResult, candidate_count: int):
        """Adapt activation parameters based on recent performance"""
        
        # Adapt threshold based on activation density
        current_sparsity = len(result.active_memories) / max(1, candidate_count)
        
        if current_sparsity > self.target_sparsity * 1.5:
            # Too many memories activated, increase threshold
            self.global_activation_threshold *= 1.1
            self.stats["threshold_adjustments"] += 1
        elif current_sparsity < self.target_sparsity * 0.5:
            # Too few memories activated, decrease threshold
            self.global_activation_threshold *= 0.9
            self.stats["threshold_adjustments"] += 1
        
        # Keep threshold within reasonable bounds
        self.global_activation_threshold = max(0.01, min(0.9, self.global_activation_threshold))
    
    def get_activation_statistics(self) -> Dict[str, Any]:
        """Get activation statistics and performance metrics"""
        
        if not self.activation_history:
            return self.stats
        
        recent_activations = self.activation_history[-100:]  # Last 100 activations
        
        activation_states = {}
        for result in recent_activations:
            state = result.activation_state.value
            activation_states[state] = activation_states.get(state, 0) + 1
        
        return {
            **self.stats,
            "global_activation_threshold": self.global_activation_threshold,
            "max_active_memories": self.max_active_memories,
            "target_sparsity": self.target_sparsity,
            "recent_activation_states": activation_states,
            "average_activation_budget_used": sum(
                r.total_activation_budget_used for r in recent_activations
            ) / len(recent_activations) if recent_activations else 0,
            "recent_memory_activation_frequency": {
                memory_id: len(timestamps) 
                for memory_id, timestamps in self.recent_activations.items()
                if len(timestamps) > 5  # Only show frequently activated memories
            }
        }