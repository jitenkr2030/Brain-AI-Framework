"""
Incremental Learning Engine
Local, incremental learning rules for memory strength updates.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import math
import random

from app.config import get_settings


class LearningMode(Enum):
    """Types of learning modes"""
    REINFORCEMENT = "reinforcement"  # Positive/negative feedback
    DISCOVERY = "discovery"         # Pattern discovery
    CONSOLIDATION = "consolidation"  # Memory strengthening
    FORGETTING = "forgetting"       # Memory weakening
    ASSOCIATION = "association"     # Creating associations


class FeedbackType(Enum):
    """Types of feedback"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"
    CONFIRMATION = "confirmation"


@dataclass
class LearningRule:
    """Represents a learning rule"""
    name: str
    description: str
    condition: str
    action: str
    weight: float
    enabled: bool = True


@dataclass
class LearningEvent:
    """Represents a learning event"""
    memory_id: str
    event_type: str
    feedback_type: FeedbackType
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    timestamp: datetime
    confidence: float = 1.0


class LearningEngine:
    """
    Incremental Learning Engine
    
    Provides local, incremental learning without global updates:
    - Reinforcement learning based on feedback
    - Pattern discovery and consolidation
    - Association formation
    - Memory forgetting and strengthening
    - No gradient descent or batch retraining
    """
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        
        # Learning rules registry
        self.learning_rules: List[LearningRule] = []
        self._initialize_learning_rules()
        
        # Learning statistics
        self.stats = {
            "total_learning_events": 0,
            "positive_feedback": 0,
            "negative_feedback": 0,
            "association_formed": 0,
            "memories_strengthened": 0,
            "memories_weakened": 0
        }
        
        # Learning history for analysis
        self.learning_history: List[LearningEvent] = []
        
        # Adaptive learning parameters
        self.learning_rate = self.settings.LEARNING_RATE
        self.forgetting_rate = self.settings.FORGETTING_RATE
    
    def _initialize_learning_rules(self):
        """Initialize default learning rules"""
        
        # Basic reinforcement learning rule
        self.learning_rules.append(LearningRule(
            name="basic_reinforcement",
            description="Basic positive/negative reinforcement",
            condition="feedback_received",
            action="update_strength",
            weight=1.0
        ))
        
        # Frequency-based strengthening
        self.learning_rules.append(LearningRule(
            name="frequency_strengthening",
            description="Strengthen frequently accessed memories",
            condition="high_access_count",
            action="gradual_strengthening",
            weight=0.5
        ))
        
        # Contextual reinforcement
        self.learning_rules.append(LearningRule(
            name="contextual_reinforcement",
            description="Strengthen memories with similar context",
            condition="similar_context",
            action="context_strengthening",
            weight=0.3
        ))
        
        # Association formation
        self.learning_rules.append(LearningRule(
            name="association_formation",
            description="Form associations between co-occurring memories",
            condition="co_occurrence",
            action="create_association",
            weight=0.4
        ))
        
        # Time-based forgetting
        self.learning_rules.append(LearningRule(
            name="time_forgetting",
            description="Gradual forgetting of unused memories",
            condition="time_decay",
            action="apply_decay",
            weight=0.2
        ))
    
    def process_feedback(
        self, 
        memory_id: str, 
        feedback_type: FeedbackType, 
        outcome: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Process feedback and update memory strength
        
        Args:
            memory_id: ID of memory to update
            feedback_type: Type of feedback received
            outcome: Outcome information
            context: Additional context
            
        Returns:
            Dictionary with strength change information
        """
        try:
            # Create learning event
            learning_event = LearningEvent(
                memory_id=memory_id,
                event_type="feedback",
                feedback_type=feedback_type,
                context=context or {},
                outcome=outcome,
                timestamp=datetime.now(),
                confidence=outcome.get("confidence", 1.0)
            )
            
            # Calculate strength change
            strength_change = self._calculate_feedback_strength_change(
                feedback_type, outcome, context
            )
            
            # Apply learning rules
            total_change = 0.0
            rule_contributions = {}
            
            for rule in self.learning_rules:
                if not rule.enabled:
                    continue
                
                rule_change = self._apply_learning_rule(
                    rule, learning_event, strength_change
                )
                
                if rule_change != 0:
                    total_change += rule_change * rule.weight
                    rule_contributions[rule.name] = rule_change
            
            # Update statistics
            self._update_learning_stats(feedback_type, total_change)
            
            # Store learning event
            self.learning_history.append(learning_event)
            
            # Keep history size manageable
            if len(self.learning_history) > 10000:
                self.learning_history = self.learning_history[-5000:]
            
            logger.debug(f"Learning: memory {memory_id}, feedback {feedback_type.value}, change {total_change}")
            
            return {
                "strength_change": total_change,
                "rule_contributions": rule_contributions,
                "confidence": learning_event.confidence,
                "learning_rate": self.learning_rate
            }
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            raise
    
    def update_memory_access(
        self, 
        memory_id: str, 
        access_context: Dict[str, Any],
        access_count: int
    ) -> Dict[str, float]:
        """
        Update memory strength based on access patterns
        
        Args:
            memory_id: ID of accessed memory
            access_context: Context of the access
            access_count: Total access count
            
        Returns:
            Dictionary with strength change information
        """
        try:
            # Create learning event for access
            learning_event = LearningEvent(
                memory_id=memory_id,
                event_type="access",
                feedback_type=FeedbackType.NEUTRAL,
                context=access_context,
                outcome={"access_count": access_count},
                timestamp=datetime.now()
            )
            
            # Calculate access-based strengthening
            strength_change = self._calculate_access_strength_change(access_count)
            
            # Apply frequency-based learning rule
            frequency_rule = next(
                (rule for rule in self.learning_rules if rule.name == "frequency_strengthening"),
                None
            )
            
            total_change = 0.0
            if frequency_rule and frequency_rule.enabled:
                total_change = self._apply_learning_rule(frequency_rule, learning_event, strength_change)
            
            # Update statistics
            if total_change > 0:
                self.stats["memories_strengthened"] += 1
            elif total_change < 0:
                self.stats["memories_weakened"] += 1
            
            return {
                "strength_change": total_change,
                "access_count": access_count,
                "frequency_bonus": strength_change
            }
            
        except Exception as e:
            logger.error(f"Error updating memory access: {e}")
            raise
    
    def process_co_occurrence(
        self, 
        memory_ids: List[str], 
        co_occurrence_strength: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Process co-occurrence of memories and form associations
        
        Args:
            memory_ids: List of memory IDs that co-occurred
            co_occurrence_strength: Strength of the co-occurrence
            
        Returns:
            List of association updates
        """
        try:
            association_updates = []
            
            # Form associations between all pairs
            for i, memory_id_1 in enumerate(memory_ids):
                for memory_id_2 in memory_ids[i+1:]:
                    # Create learning event for association
                    learning_event = LearningEvent(
                        memory_id=memory_id_1,
                        event_type="association",
                        feedback_type=FeedbackType.POSITIVE,
                        context={"associated_memory": memory_id_2},
                        outcome={"co_occurrence_strength": co_occurrence_strength},
                        timestamp=datetime.now()
                    )
                    
                    # Apply association learning rule
                    association_rule = next(
                        (rule for rule in self.learning_rules if rule.name == "association_formation"),
                        None
                    )
                    
                    if association_rule and association_rule.enabled:
                        strength_change = self._apply_learning_rule(
                            association_rule, learning_event, co_occurrence_strength
                        )
                        
                        association_updates.append({
                            "memory_id_1": memory_id_1,
                            "memory_id_2": memory_id_2,
                            "strength_change": strength_change,
                            "co_occurrence_strength": co_occurrence_strength
                        })
            
            # Update statistics
            self.stats["association_formed"] += len(association_updates)
            
            logger.debug(f"Formed {len(association_updates)} associations")
            
            return association_updates
            
        except Exception as e:
            logger.error(f"Error processing co-occurrence: {e}")
            raise
    
    def apply_time_decay(self, days_passed: float) -> Dict[str, float]:
        """
        Apply time-based decay to memory strengths
        
        Args:
            days_passed: Number of days passed since last update
            
        Returns:
            Decay parameters
        """
        try:
            # Calculate decay factor
            decay_factor = math.exp(-self.forgetting_rate * days_passed)
            
            # Update adaptive learning rate based on decay
            if decay_factor < 0.5:
                # Increase learning rate when memories are decaying fast
                self.learning_rate = min(0.1, self.learning_rate * 1.1)
            else:
                # Decrease learning rate when memories are stable
                self.learning_rate = max(0.001, self.learning_rate * 0.95)
            
            return {
                "decay_factor": decay_factor,
                "forgetting_rate": self.forgetting_rate,
                "adjusted_learning_rate": self.learning_rate
            }
            
        except Exception as e:
            logger.error(f"Error applying time decay: {e}")
            raise
    
    def _calculate_feedback_strength_change(
        self, 
        feedback_type: FeedbackType, 
        outcome: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate strength change based on feedback type"""
        
        base_change = self.learning_rate
        
        # Feedback-specific adjustments
        if feedback_type == FeedbackType.POSITIVE:
            change = base_change * outcome.get("reward", 1.0)
        elif feedback_type == FeedbackType.NEGATIVE:
            change = -base_change * outcome.get("penalty", 1.0)
        elif feedback_type == FeedbackType.CORRECTION:
            change = base_change * 0.5  # Smaller correction
        elif feedback_type == FeedbackType.CONFIRMATION:
            change = base_change * 0.3  # Even smaller confirmation
        else:  # NEUTRAL
            change = 0.0
        
        # Context-based adjustment
        if context:
            confidence_boost = context.get("confidence", 1.0)
            change *= confidence_boost
        
        return change
    
    def _calculate_access_strength_change(self, access_count: int) -> float:
        """Calculate strength change based on access frequency"""
        
        # Diminishing returns for access count
        if access_count <= 1:
            return 0.01
        
        # Logarithmic growth for access-based strengthening
        return 0.01 * math.log(access_count + 1)
    
    def _apply_learning_rule(
        self, 
        rule: LearningRule, 
        learning_event: LearningEvent, 
        base_change: float
    ) -> float:
        """Apply a specific learning rule"""
        
        try:
            if rule.name == "basic_reinforcement":
                return base_change
            
            elif rule.name == "frequency_strengthening":
                if learning_event.event_type == "access":
                    access_count = learning_event.outcome.get("access_count", 0)
                    return self._calculate_access_strength_change(access_count)
            
            elif rule.name == "contextual_reinforcement":
                # Strengthen if similar context patterns
                context_similarity = self._calculate_context_similarity(
                    learning_event.context
                )
                return base_change * context_similarity
            
            elif rule.name == "association_formation":
                if learning_event.event_type == "association":
                    co_occurrence = learning_event.outcome.get("co_occurrence_strength", 0.5)
                    return co_occurrence * 0.1  # Small association boost
            
            elif rule.name == "time_forgetting":
                if learning_event.event_type == "decay":
                    decay_factor = learning_event.outcome.get("decay_factor", 1.0)
                    return (decay_factor - 1.0) * 0.1  # Negative for decay
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error applying learning rule {rule.name}: {e}")
            return 0.0
    
    def _calculate_context_similarity(self, context: Dict[str, Any]) -> float:
        """Calculate similarity score for context patterns"""
        
        if not context:
            return 0.0
        
        # Simple context similarity based on common keys
        # In a real implementation, this would be more sophisticated
        similarity_scores = []
        
        for event in self.learning_history[-100:]:  # Look at recent history
            if event.context:
                common_keys = set(context.keys()) & set(event.context.keys())
                if common_keys:
                    matches = sum(1 for key in common_keys if context[key] == event.context[key])
                    similarity = matches / len(common_keys)
                    similarity_scores.append(similarity)
        
        return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
    
    def _update_learning_stats(self, feedback_type: FeedbackType, strength_change: float):
        """Update learning statistics"""
        
        self.stats["total_learning_events"] += 1
        
        if feedback_type == FeedbackType.POSITIVE:
            self.stats["positive_feedback"] += 1
        elif feedback_type == FeedbackType.NEGATIVE:
            self.stats["negative_feedback"] += 1
        
        if strength_change > 0:
            self.stats["memories_strengthened"] += 1
        elif strength_change < 0:
            self.stats["memories_weakened"] += 1
    
    def enable_learning_rule(self, rule_name: str):
        """Enable a specific learning rule"""
        for rule in self.learning_rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"Enabled learning rule: {rule_name}")
                break
    
    def disable_learning_rule(self, rule_name: str):
        """Disable a specific learning rule"""
        for rule in self.learning_rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"Disabled learning rule: {rule_name}")
                break
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning engine statistics"""
        
        recent_events = [
            event for event in self.learning_history 
            if (datetime.now() - event.timestamp).days <= 1
        ]
        
        return {
            "total_learning_events": self.stats["total_learning_events"],
            "positive_feedback": self.stats["positive_feedback"],
            "negative_feedback": self.stats["negative_feedback"],
            "association_formed": self.stats["association_formed"],
            "memories_strengthened": self.stats["memories_strengthened"],
            "memories_weakened": self.stats["memories_weakened"],
            "recent_events": len(recent_events),
            "active_rules": len([rule for rule in self.learning_rules if rule.enabled]),
            "learning_rate": self.learning_rate,
            "forgetting_rate": self.forgetting_rate,
            "learning_rules": [
                {"name": rule.name, "enabled": rule.enabled, "weight": rule.weight}
                for rule in self.learning_rules
            ]
        }
    
    def adapt_learning_parameters(self, performance_metrics: Dict[str, float]):
        """
        Adapt learning parameters based on performance metrics
        
        Args:
            performance_metrics: Dictionary with performance metrics
        """
        try:
            # Adjust learning rate based on performance
            accuracy = performance_metrics.get("accuracy", 0.5)
            stability = performance_metrics.get("stability", 0.5)
            
            # If accuracy is low, increase learning rate
            if accuracy < 0.5:
                self.learning_rate = min(0.1, self.learning_rate * 1.2)
            # If accuracy is high, decrease learning rate for stability
            elif accuracy > 0.8:
                self.learning_rate = max(0.001, self.learning_rate * 0.9)
            
            # Adjust forgetting rate based on stability
            if stability < 0.3:
                self.forgetting_rate = max(0.0001, self.forgetting_rate * 0.9)
            elif stability > 0.8:
                self.forgetting_rate = min(0.01, self.forgetting_rate * 1.1)
            
            logger.debug(f"Adapted learning parameters: rate={self.learning_rate}, decay={self.forgetting_rate}")
            
        except Exception as e:
            logger.error(f"Error adapting learning parameters: {e}")
            raise