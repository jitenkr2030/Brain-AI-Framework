"""
Experience Processing and Feedback Module
Closes the learning loop by processing feedback and updating memory strength.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
from loguru import logger

from core.learning import LearningEngine, FeedbackType


class FeedbackSource(Enum):
    """Sources of feedback"""
    USER = "user"                    # User-provided feedback
    SYSTEM = "system"               # System-generated feedback
    OUTCOME = "outcome"             # Outcome-based feedback
    PERFORMANCE = "performance"     # Performance metrics feedback
    EXTERNAL = "external"           # External system feedback
    SIMULATION = "simulation"       # Simulation-based feedback


class FeedbackQuality(Enum):
    """Quality levels of feedback"""
    HIGH = "high"     # Explicit, clear feedback
    MEDIUM = "medium" # Implicit feedback with some clarity
    LOW = "low"       # Ambiguous or weak feedback
    NOISE = "noise"   # Potentially noisy feedback


@dataclass
class FeedbackEvent:
    """Represents a feedback event"""
    memory_id: str
    source: FeedbackSource
    feedback_type: FeedbackType
    quality: FeedbackQuality
    content: Dict[str, Any]
    timestamp: datetime
    confidence: float
    context: Dict[str, Any]
    outcome_value: Optional[float] = None


@dataclass
class LearningUpdate:
    """Represents a learning update to be applied"""
    memory_id: str
    strength_change: float
    confidence: float
    learning_rule: str
    reasoning: str
    timestamp: datetime


class FeedbackProcessor:
    """
    Feedback Processor
    
    Processes feedback from various sources and updates memory through the learning engine:
    - Handles user feedback
    - Processes system outcomes
    - Learns from performance metrics
    - Manages feedback quality
    - Applies learning updates
    """
    
    def __init__(self, learning_engine: LearningEngine):
        self.learning_engine = learning_engine
        self.memory_store = None  # Will be set later
        
        # Feedback processing pipeline
        self.feedback_queue: List[FeedbackEvent] = []
        self.processed_feedback: List[FeedbackEvent] = []
        
        # Feedback quality assessment
        self.quality_weights = {
            FeedbackQuality.HIGH: 1.0,
            FeedbackQuality.MEDIUM: 0.7,
            FeedbackQuality.LOW: 0.4,
            FeedbackQuality.NOISE: 0.1
        }
        
        # Statistics
        self.stats = {
            "total_feedback_events": 0,
            "processed_feedback": 0,
            "learning_updates_applied": 0,
            "feedback_by_source": {},
            "feedback_by_quality": {},
            "average_feedback_confidence": 0.0,
            "learning_effectiveness": 0.0
        }
        
        # Feedback patterns for learning
        self.feedback_patterns: Dict[str, List[FeedbackEvent]] = {}
        
        # Processing configuration
        self.batch_size = 10
        self.processing_interval = 1.0  # seconds
        self.max_queue_size = 1000
    
    def set_memory_store(self, memory_store):
        """Set the memory store reference"""
        self.memory_store = memory_store
    
    async def process_feedback(
        self,
        memory_id: str,
        feedback_type: str,
        outcome: Dict[str, Any],
        source: FeedbackSource = FeedbackSource.SYSTEM,
        quality: FeedbackQuality = FeedbackQuality.MEDIUM,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process feedback for a memory
        
        Args:
            memory_id: ID of memory to update
            feedback_type: Type of feedback (positive, negative, etc.)
            outcome: Outcome information
            source: Source of the feedback
            quality: Quality of the feedback
            context: Additional context
            
        Returns:
            Learning update information
        """
        try:
            # Create feedback event
            feedback_event = FeedbackEvent(
                memory_id=memory_id,
                source=source,
                feedback_type=FeedbackType(feedback_type),
                quality=quality,
                content=outcome,
                timestamp=datetime.now(),
                confidence=outcome.get("confidence", 0.5),
                context=context or {},
                outcome_value=outcome.get("value")
            )
            
            # Add to processing queue
            await self._queue_feedback(feedback_event)
            
            # Process immediately if queue is getting full
            if len(self.feedback_queue) >= self.batch_size:
                await self._process_feedback_batch()
            
            # Update statistics
            self._update_feedback_stats(feedback_event)
            
            logger.debug(f"Queued feedback for memory {memory_id}: {feedback_type} from {source.value}")
            
            return {
                "feedback_queued": True,
                "memory_id": memory_id,
                "feedback_type": feedback_type,
                "source": source.value,
                "quality": quality.value,
                "queue_size": len(self.feedback_queue)
            }
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            raise
    
    async def process_outcome_feedback(
        self,
        memory_id: str,
        expected_outcome: Dict[str, Any],
        actual_outcome: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process outcome-based feedback (expected vs actual)
        
        Args:
            memory_id: ID of memory
            expected_outcome: What was expected to happen
            actual_outcome: What actually happened
            context: Additional context
            
        Returns:
            Learning update information
        """
        try:
            # Calculate outcome quality
            outcome_quality = self._assess_outcome_quality(expected_outcome, actual_outcome)
            
            # Determine feedback type based on outcome
            feedback_type = self._determine_outcome_feedback_type(expected_outcome, actual_outcome)
            
            # Create comprehensive outcome information
            outcome_info = {
                "expected": expected_outcome,
                "actual": actual_outcome,
                "quality": outcome_quality,
                "discrepancy": self._calculate_outcome_discrepancy(expected_outcome, actual_outcome),
                "confidence": outcome_quality
            }
            
            return await self.process_feedback(
                memory_id=memory_id,
                feedback_type=feedback_type,
                outcome=outcome_info,
                source=FeedbackSource.OUTCOME,
                quality=self._map_quality_to_enum(outcome_quality),
                context=context
            )
            
        except Exception as e:
            logger.error(f"Error processing outcome feedback: {e}")
            raise
    
    async def process_user_feedback(
        self,
        memory_id: str,
        user_rating: float,
        user_comment: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user-provided feedback
        
        Args:
            memory_id: ID of memory
            user_rating: User rating (0.0 to 1.0)
            user_comment: Optional user comment
            context: Additional context
            
        Returns:
            Learning update information
        """
        try:
            # Determine feedback type from rating
            if user_rating >= 0.7:
                feedback_type = "positive"
                quality = FeedbackQuality.HIGH
            elif user_rating <= 0.3:
                feedback_type = "negative"
                quality = FeedbackQuality.HIGH
            else:
                feedback_type = "neutral"
                quality = FeedbackQuality.MEDIUM
            
            # Create user feedback content
            feedback_content = {
                "rating": user_rating,
                "comment": user_comment,
                "user_satisfaction": user_rating
            }
            
            return await self.process_feedback(
                memory_id=memory_id,
                feedback_type=feedback_type,
                outcome=feedback_content,
                source=FeedbackSource.USER,
                quality=quality,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Error processing user feedback: {e}")
            raise
    
    async def process_performance_feedback(
        self,
        memory_id: str,
        performance_metrics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process performance-based feedback
        
        Args:
            memory_id: ID of memory
            performance_metrics: Performance metrics (accuracy, speed, etc.)
            context: Additional context
            
        Returns:
            Learning update information
        """
        try:
            # Calculate overall performance score
            overall_performance = sum(performance_metrics.values()) / len(performance_metrics)
            
            # Determine feedback type and quality
            if overall_performance >= 0.8:
                feedback_type = "positive"
                quality = FeedbackQuality.HIGH
            elif overall_performance <= 0.4:
                feedback_type = "negative"
                quality = FeedbackQuality.MEDIUM
            else:
                feedback_type = "neutral"
                quality = FeedbackQuality.MEDIUM
            
            feedback_content = {
                "performance_metrics": performance_metrics,
                "overall_score": overall_performance,
                "performance_context": "system_performance"
            }
            
            return await self.process_feedback(
                memory_id=memory_id,
                feedback_type=feedback_type,
                outcome=feedback_content,
                source=FeedbackSource.PERFORMANCE,
                quality=quality,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Error processing performance feedback: {e}")
            raise
    
    async def start_processing(self):
        """Start the feedback processing background task"""
        asyncio.create_task(self._feedback_processing_loop())
        logger.info("🚀 Started feedback processing loop")
    
    async def stop_processing(self):
        """Stop the feedback processing background task"""
        # Process any remaining feedback
        if self.feedback_queue:
            await self._process_feedback_batch()
        logger.info("🛑 Stopped feedback processing loop")
    
    async def _feedback_processing_loop(self):
        """Background loop for processing feedback"""
        while True:
            try:
                if self.feedback_queue:
                    await self._process_feedback_batch()
                
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Error in feedback processing loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_feedback_batch(self):
        """Process a batch of feedback events"""
        if not self.feedback_queue:
            return
        
        try:
            # Get batch of feedback
            batch = self.feedback_queue[:self.batch_size]
            self.feedback_queue = self.feedback_queue[self.batch_size:]
            
            learning_updates = []
            
            for feedback_event in batch:
                try:
                    # Process individual feedback event
                    learning_update = await self._process_single_feedback(feedback_event)
                    
                    if learning_update:
                        learning_updates.append(learning_update)
                    
                    # Move to processed feedback
                    self.processed_feedback.append(feedback_event)
                    
                except Exception as e:
                    logger.error(f"Error processing feedback event: {e}")
            
            # Apply learning updates
            if learning_updates and self.memory_store:
                await self._apply_learning_updates(learning_updates)
            
            # Keep processed feedback history manageable
            if len(self.processed_feedback) > 10000:
                self.processed_feedback = self.processed_feedback[-5000:]
            
            self.stats["processed_feedback"] += len(batch)
            
        except Exception as e:
            logger.error(f"Error processing feedback batch: {e}")
            # Put processed items back in queue for retry
            self.feedback_queue = batch + self.feedback_queue
    
    async def _process_single_feedback(self, feedback_event: FeedbackEvent) -> Optional[LearningUpdate]:
        """Process a single feedback event"""
        
        try:
            # Apply feedback quality weighting
            quality_weight = self.quality_weights[feedback_event.quality]
            weighted_confidence = feedback_event.confidence * quality_weight
            
            # Create outcome information for learning engine
            outcome = {
                **feedback_event.content,
                "confidence": weighted_confidence,
                "source": feedback_event.source.value,
                "quality": feedback_event.quality.value
            }
            
            # Get learning update from learning engine
            learning_result = self.learning_engine.process_feedback(
                memory_id=feedback_event.memory_id,
                feedback_type=feedback_event.feedback_type,
                outcome=outcome,
                context=feedback_event.context
            )
            
            if learning_result and learning_result.get("strength_change", 0) != 0:
                return LearningUpdate(
                    memory_id=feedback_event.memory_id,
                    strength_change=learning_result["strength_change"],
                    confidence=weighted_confidence,
                    learning_rule="feedback_processing",
                    reasoning=f"Applied {feedback_event.feedback_type.value} feedback from {feedback_event.source.value}",
                    timestamp=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing single feedback: {e}")
            return None
    
    async def _apply_learning_updates(self, learning_updates: List[LearningUpdate]):
        """Apply learning updates to memory store"""
        
        try:
            for update in learning_updates:
                if self.memory_store:
                    await self.memory_store.update_strength(
                        memory_id=update.memory_id,
                        strength_change=update.strength_change
                    )
            
            self.stats["learning_updates_applied"] += len(learning_updates)
            
        except Exception as e:
            logger.error(f"Error applying learning updates: {e}")
            raise
    
    async def _queue_feedback(self, feedback_event: FeedbackEvent):
        """Queue feedback for processing"""
        
        # Add quality weight to confidence
        quality_weight = self.quality_weights[feedback_event.quality]
        feedback_event.confidence *= quality_weight
        
        # Add to queue
        self.feedback_queue.append(feedback_event)
        
        # Limit queue size
        if len(self.feedback_queue) > self.max_queue_size:
            # Remove oldest feedback
            self.feedback_queue = self.feedback_queue[-self.max_queue_size:]
    
    def _assess_outcome_quality(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> float:
        """Assess the quality of an outcome"""
        
        if not expected or not actual:
            return 0.5
        
        # Simple quality assessment based on outcome similarity
        matching_keys = 0
        total_keys = len(expected)
        
        for key, expected_value in expected.items():
            if key in actual:
                if self._values_match(expected_value, actual[key]):
                    matching_keys += 1
        
        if total_keys == 0:
            return 0.5
        
        return matching_keys / total_keys
    
    def _values_match(self, expected: Any, actual: Any) -> bool:
        """Check if expected and actual values match"""
        
        # Handle different data types
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            # Allow some tolerance for numeric values
            tolerance = 0.1
            return abs(expected - actual) <= tolerance
        elif isinstance(expected, str) and isinstance(actual, str):
            # Simple string matching (could be improved with fuzzy matching)
            return expected.lower() == actual.lower()
        else:
            # For complex types, do direct comparison
            return expected == actual
    
    def _calculate_outcome_discrepancy(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> float:
        """Calculate discrepancy between expected and actual outcomes"""
        
        if not expected or not actual:
            return 1.0
        
        discrepancies = []
        
        for key, expected_value in expected.items():
            if key in actual:
                if isinstance(expected_value, (int, float)) and isinstance(actual[key], (int, float)):
                    # Numeric discrepancy
                    max_val = max(abs(expected_value), abs(actual[key]), 1.0)
                    discrepancy = abs(expected_value - actual[key]) / max_val
                    discrepancies.append(discrepancy)
                elif isinstance(expected_value, str) and isinstance(actual[key], str):
                    # String discrepancy (simple)
                    discrepancy = 0.0 if expected_value.lower() == actual[key].lower() else 1.0
                    discrepancies.append(discrepancy)
                else:
                    # Complex type discrepancy
                    discrepancy = 0.0 if expected_value == actual[key] else 1.0
                    discrepancies.append(discrepancy)
        
        return sum(discrepancies) / len(discrepancies) if discrepancies else 1.0
    
    def _determine_outcome_feedback_type(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> str:
        """Determine feedback type from outcome comparison"""
        
        discrepancy = self._calculate_outcome_discrepancy(expected, actual)
        
        if discrepancy <= 0.2:
            return "positive"
        elif discrepancy >= 0.8:
            return "negative"
        else:
            return "neutral"
    
    def _map_quality_to_enum(self, quality_score: float) -> FeedbackQuality:
        """Map numeric quality score to FeedbackQuality enum"""
        
        if quality_score >= 0.8:
            return FeedbackQuality.HIGH
        elif quality_score >= 0.5:
            return FeedbackQuality.MEDIUM
        elif quality_score >= 0.2:
            return FeedbackQuality.LOW
        else:
            return FeedbackQuality.NOISE
    
    def _update_feedback_stats(self, feedback_event: FeedbackEvent):
        """Update feedback statistics"""
        
        self.stats["total_feedback_events"] += 1
        
        # Update source counts
        source = feedback_event.source.value
        self.stats["feedback_by_source"][source] = (
            self.stats["feedback_by_source"].get(source, 0) + 1
        )
        
        # Update quality counts
        quality = feedback_event.quality.value
        self.stats["feedback_by_quality"][quality] = (
            self.stats["feedback_by_quality"].get(quality, 0) + 1
        )
        
        # Update average confidence
        total_events = self.stats["total_feedback_events"]
        current_avg = self.stats["average_feedback_confidence"]
        self.stats["average_feedback_confidence"] = (
            (current_avg * (total_events - 1) + feedback_event.confidence) / total_events
        )
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback processor statistics"""
        
        return {
            **self.stats,
            "queue_size": len(self.feedback_queue),
            "processing_rate": (
                self.stats["processed_feedback"] / max(1, self.stats["total_feedback_events"])
            ) * 100,
            "learning_effectiveness": (
                self.stats["learning_updates_applied"] / max(1, self.stats["processed_feedback"])
            ) * 100 if self.stats["processed_feedback"] > 0 else 0,
            "feedback_patterns_count": len(self.feedback_patterns)
        }
    
    def get_recent_feedback_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of recent feedback"""
        
        cutoff_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_time = cutoff_time.replace(hour=23)  # Approximate 24 hours ago
        
        recent_feedback = [
            fb for fb in self.processed_feedback 
            if fb.timestamp >= cutoff_time
        ]
        
        if not recent_feedback:
            return {"message": "No recent feedback"}
        
        # Aggregate by source
        source_summary = {}
        for fb in recent_feedback:
            source = fb.source.value
            if source not in source_summary:
                source_summary[source] = {"count": 0, "avg_confidence": 0, "quality_dist": {}}
            
            source_summary[source]["count"] += 1
            source_summary[source]["avg_confidence"] += fb.confidence
            
            quality = fb.quality.value
            source_summary[source]["quality_dist"][quality] = (
                source_summary[source]["quality_dist"].get(quality, 0) + 1
            )
        
        # Calculate averages
        for source_data in source_summary.values():
            source_data["avg_confidence"] /= source_data["count"]
        
        return {
            "total_recent_feedback": len(recent_feedback),
            "source_summary": source_summary,
            "time_range_hours": hours
        }