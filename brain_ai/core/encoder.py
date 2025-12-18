"""
Pattern & Event Encoding Module
Transforms raw input into meaningful patterns and contextual information.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re
from datetime import datetime


class EventType(Enum):
    """Types of events that can be encoded"""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    LEARNING = "learning"
    MEMORY_ACCESS = "memory_access"
    REASONING = "reasoning"
    FEEDBACK = "feedback"
    SYSTEM = "system"
    USER_ACTION = "user_action"
    DATA_INPUT = "data_input"


class ContextState(Enum):
    """Contextual states"""
    NORMAL = "normal"
    ERROR = "error"
    LEARNING = "learning"
    HIGH_ACTIVITY = "high_activity"
    LOW_ACTIVITY = "low_activity"
    PROCESSING = "processing"
    IDLE = "idle"


class IntensityLevel(Enum):
    """Event intensity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Pattern:
    """Represents a recognized pattern"""
    type: EventType
    signature: str
    features: List[str]
    confidence: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "signature": self.signature,
            "features": self.features,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Context:
    """Contextual information for events"""
    state: ContextState
    intensity: IntensityLevel
    source: str
    metadata: Dict[str, Any]
    history_context: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "intensity": self.intensity.value,
            "source": self.source,
            "metadata": self.metadata,
            "history_context": self.history_context or []
        }


class Encoder:
    """
    Pattern & Event Encoder
    
    Transforms raw input into meaningful patterns that can be stored in memory
    and processed by the brain-inspired AI system.
    """
    
    def __init__(self):
        self.pattern_registry: Dict[str, Pattern] = {}
        self.feature_extractors = self._initialize_extractors()
        self.intensity_analyzer = self._initialize_intensity_analyzer()
    
    def encode(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode raw input into pattern and context
        
        Args:
            raw_input: Raw input data (events, signals, observations)
            
        Returns:
            Dictionary containing pattern and context information
        """
        try:
            # Extract basic information
            event_type = self._detect_event_type(raw_input)
            pattern = self._extract_pattern(raw_input, event_type)
            context = self._extract_context(raw_input, event_type)
            
            # Store pattern for learning
            self._register_pattern(pattern)
            
            return {
                "pattern": pattern.to_dict(),
                "context": context.to_dict(),
                "encoded_at": datetime.now().isoformat(),
                "raw_input_summary": self._summarize_raw_input(raw_input)
            }
            
        except Exception as e:
            # Fallback encoding for errors
            return self._fallback_encoding(raw_input, str(e))
    
    def _detect_event_type(self, raw_input: Dict[str, Any]) -> EventType:
        """Detect the type of event from raw input"""
        
        # Check for specific keys that indicate event type
        if "error" in raw_input or "exception" in raw_input:
            return EventType.ERROR
        
        if "request" in raw_input or "api_call" in raw_input:
            return EventType.REQUEST
        
        if "response" in raw_input or "result" in raw_input:
            return EventType.RESPONSE
        
        if "feedback" in raw_input or "rating" in raw_input:
            return EventType.FEEDBACK
        
        if "learning" in raw_input or "training" in raw_input:
            return EventType.LEARNING
        
        if "reasoning" in raw_input or "analysis" in raw_input:
            return EventType.REASONING
        
        if "user" in raw_input or "action" in raw_input:
            return EventType.USER_ACTION
        
        if "memory" in raw_input or "retrieval" in raw_input:
            return EventType.MEMORY_ACCESS
        
        # Default to data input
        return EventType.DATA_INPUT
    
    def _extract_pattern(self, raw_input: Dict[str, Any], event_type: EventType) -> Pattern:
        """Extract pattern signature and features"""
        
        # Generate signature based on event type
        signature = self._generate_signature(raw_input, event_type)
        
        # Extract features
        features = self._extract_features(raw_input, event_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(raw_input, features)
        
        return Pattern(
            type=event_type,
            signature=signature,
            features=features,
            confidence=confidence,
            timestamp=datetime.now()
        )
    
    def _extract_context(self, raw_input: Dict[str, Any], event_type: EventType) -> Context:
        """Extract contextual information"""
        
        # Detect state
        state = self._detect_state(raw_input, event_type)
        
        # Detect intensity
        intensity = self._detect_intensity(raw_input, event_type)
        
        # Extract source
        source = raw_input.get("source", "unknown")
        
        # Extract metadata
        metadata = self._extract_metadata(raw_input)
        
        return Context(
            state=state,
            intensity=intensity,
            source=source,
            metadata=metadata
        )
    
    def _generate_signature(self, raw_input: Dict[str, Any], event_type: EventType) -> str:
        """Generate a unique signature for the pattern"""
        
        # Use type-specific signature generation
        if event_type == EventType.ERROR:
            error_type = raw_input.get("error_type", "unknown")
            return f"error:{error_type}"
        
        elif event_type == EventType.REQUEST:
            endpoint = raw_input.get("endpoint", "unknown")
            method = raw_input.get("method", "unknown")
            return f"request:{method}:{endpoint}"
        
        elif event_type == EventType.RESPONSE:
            status = raw_input.get("status_code", "unknown")
            return f"response:status:{status}"
        
        elif event_type == EventType.USER_ACTION:
            action = raw_input.get("action", "unknown")
            return f"action:{action}"
        
        else:
            # Generic signature based on content
            content_hash = hash(str(raw_input))
            return f"{event_type.value}:{content_hash}"
    
    def _extract_features(self, raw_input: Dict[str, Any], event_type: EventType) -> List[str]:
        """Extract relevant features from input"""
        features = []
        
        # Common features
        if "timestamp" in raw_input:
            features.append("has_timestamp")
        
        if "metadata" in raw_input:
            features.append("has_metadata")
        
        # Type-specific features
        if event_type == EventType.ERROR:
            if raw_input.get("error_type"):
                features.append(f"error_type_{raw_input['error_type']}")
            if raw_input.get("stack_trace"):
                features.append("has_stack_trace")
        
        elif event_type == EventType.REQUEST:
            features.append(f"method_{raw_input.get('method', 'unknown')}")
            if raw_input.get("headers"):
                features.append("has_headers")
        
        elif event_type == EventType.RESPONSE:
            status = raw_input.get("status_code", 0)
            if status >= 500:
                features.append("server_error")
            elif status >= 400:
                features.append("client_error")
            else:
                features.append("success")
        
        # Size-based features
        content_size = len(str(raw_input))
        if content_size < 100:
            features.append("small")
        elif content_size < 1000:
            features.append("medium")
        else:
            features.append("large")
        
        return features
    
    def _calculate_confidence(self, raw_input: Dict[str, Any], features: List[str]) -> float:
        """Calculate confidence score for the pattern detection"""
        
        base_confidence = 0.5
        
        # Increase confidence based on feature richness
        feature_bonus = min(len(features) * 0.1, 0.3)
        
        # Increase confidence if input has expected structure
        structure_bonus = 0.0
        expected_keys = ["timestamp", "source", "type"]
        found_keys = sum(1 for key in expected_keys if key in raw_input)
        structure_bonus = found_keys * 0.1
        
        # Decrease confidence if input is too large (potential noise)
        size_penalty = 0.0
        if len(str(raw_input)) > 10000:
            size_penalty = 0.2
        
        confidence = base_confidence + feature_bonus + structure_bonus - size_penalty
        return max(0.0, min(1.0, confidence))
    
    def _detect_state(self, raw_input: Dict[str, Any], event_type: EventType) -> ContextState:
        """Detect the current system state"""
        
        if event_type == EventType.ERROR:
            return ContextState.ERROR
        
        if "processing" in raw_input.get("status", "").lower():
            return ContextState.PROCESSING
        
        if "learning" in raw_input:
            return ContextState.LEARNING
        
        if raw_input.get("activity_level", "medium") == "high":
            return ContextState.HIGH_ACTIVITY
        
        return ContextState.NORMAL
    
    def _detect_intensity(self, raw_input: Dict[str, Any], event_type: EventType) -> IntensityLevel:
        """Detect event intensity level"""
        
        # Error events are typically high intensity
        if event_type == EventType.ERROR:
            return IntensityLevel.HIGH
        
        # Check for intensity indicators
        priority = raw_input.get("priority", "medium").lower()
        if priority == "high":
            return IntensityLevel.HIGH
        elif priority == "critical":
            return IntensityLevel.CRITICAL
        elif priority == "low":
            return IntensityLevel.LOW
        
        # Default to medium
        return IntensityLevel.MEDIUM
    
    def _extract_metadata(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata"""
        metadata = {}
        
        # Copy relevant metadata fields
        relevant_keys = ["user_id", "session_id", "version", "environment", "tags"]
        for key in relevant_keys:
            if key in raw_input:
                metadata[key] = raw_input[key]
        
        return metadata
    
    def _summarize_raw_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the raw input for logging/debugging"""
        return {
            "keys": list(raw_input.keys()),
            "size": len(str(raw_input)),
            "types": {k: type(v).__name__ for k, v in raw_input.items()}
        }
    
    def _register_pattern(self, pattern: Pattern):
        """Register pattern for learning and future recognition"""
        self.pattern_registry[pattern.signature] = pattern
    
    def _initialize_extractors(self) -> Dict[str, callable]:
        """Initialize custom feature extractors"""
        return {}
    
    def _initialize_intensity_analyzer(self) -> callable:
        """Initialize intensity analysis logic"""
        return lambda x: IntensityLevel.MEDIUM
    
    def _fallback_encoding(self, raw_input: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fallback encoding when normal encoding fails"""
        return {
            "pattern": {
                "type": "unknown",
                "signature": f"fallback_{hash(str(raw_input))}",
                "features": ["fallback"],
                "confidence": 0.1,
                "timestamp": datetime.now().isoformat()
            },
            "context": {
                "state": "error",
                "intensity": "medium",
                "source": "fallback",
                "metadata": {"encoding_error": error},
                "history_context": []
            },
            "encoded_at": datetime.now().isoformat(),
            "raw_input_summary": self._summarize_raw_input(raw_input)
        }
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about registered patterns"""
        pattern_counts = {}
        for pattern in self.pattern_registry.values():
            pattern_type = pattern.type.value
            pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        return {
            "total_patterns": len(self.pattern_registry),
            "pattern_types": pattern_counts,
            "avg_confidence": sum(p.confidence for p in self.pattern_registry.values()) / len(self.pattern_registry)
            if self.pattern_registry else 0
        }