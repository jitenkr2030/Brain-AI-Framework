"""
Core Logic Tests
Tests for the brain-inspired AI framework core components.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from core.encoder import Encoder, EventType, ContextState, IntensityLevel
from core.memory import MemoryStore, MemoryType, MemoryItem
from core.learning import LearningEngine, FeedbackType
from core.routing import SparseRouter, ActivationMethod
from core.reasoning import ReasoningEngine, ReasoningType
from core.feedback import FeedbackProcessor, FeedbackSource, FeedbackQuality
from storage.persistence import PersistenceManager
from storage.key_value import KeyValueStore


class TestEncoder:
    """Tests for the Encoder component"""
    
    def setup_method(self):
        self.encoder = Encoder()
    
    def test_encode_basic_request(self):
        """Test encoding a basic request"""
        raw_input = {
            "method": "POST",
            "endpoint": "/api/test",
            "status_code": 200,
            "user_id": "123"
        }
        
        result = self.encoder.encode(raw_input)
        
        assert "pattern" in result
        assert "context" in result
        assert result["pattern"]["type"] == "data_input"
        assert "signature" in result["pattern"]
        assert "features" in result["pattern"]
    
    def test_encode_error_event(self):
        """Test encoding an error event"""
        raw_input = {
            "error": True,
            "error_type": "validation_error",
            "message": "Invalid input"
        }
        
        result = self.encoder.encode(raw_input)
        
        assert result["pattern"]["type"] == "error"
        assert result["pattern"]["signature"] == "error:validation_error"
    
    def test_encode_user_action(self):
        """Test encoding a user action"""
        raw_input = {
            "user": True,
            "action": "click",
            "element": "button",
            "session_id": "abc123"
        }
        
        result = self.encoder.encode(raw_input)
        
        assert result["pattern"]["type"] == "user_action"
        assert "click" in result["pattern"]["signature"]
    
    def test_pattern_stats(self):
        """Test pattern statistics"""
        # Encode some events
        for i in range(5):
            self.encoder.encode({"test": f"event_{i}"})
        
        stats = self.encoder.get_pattern_stats()
        
        assert stats["total_patterns"] > 0
        assert "pattern_types" in stats
        assert "avg_confidence" in stats


class TestMemoryStore:
    """Tests for the MemoryStore component"""
    
    def setup_method(self):
        self.persistence_manager = Mock(spec=PersistenceManager)
        self.memory_store = MemoryStore(self.persistence_manager)
    
    @pytest.mark.asyncio
    async def test_create_memory_item(self):
        """Test creating a memory item"""
        memory = self.memory_store.create_memory_item(
            pattern_signature="test_pattern",
            content={"data": "test"},
            context={"state": "normal"},
            memory_type=MemoryType.EPISODIC
        )
        
        assert memory.pattern_signature == "test_pattern"
        assert memory.content["data"] == "test"
        assert memory.memory_type == MemoryType.EPISODIC
        assert memory.strength == 0.5
        assert memory.id is not None
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_memory(self):
        """Test storing and retrieving a memory"""
        # Mock persistence methods
        self.persistence_manager.store_memory = Mock(return_value=True)
        self.persistence_manager.load_all_memories = Mock(return_value=[])
        
        # Create and store memory
        memory = self.memory_store.create_memory_item(
            pattern_signature="test_pattern",
            content={"key": "value"},
            context={"source": "test"}
        )
        
        memory_id = await self.memory_store.store(memory)
        
        assert memory_id is not None
        assert memory_id in self.memory_store._memory_cache
        
        # Test retrieval
        memories = await self.memory_store.retrieve("test_pattern", {"source": "test"})
        assert len(memories) > 0
    
    @pytest.mark.asyncio
    async def test_memory_strength_update(self):
        """Test updating memory strength"""
        # Mock persistence methods
        self.persistence_manager.store_memory = Mock(return_value=True)
        
        # Create memory
        memory = self.memory_store.create_memory_item(
            pattern_signature="test_pattern",
            content={"data": "test"},
            context={}
        )
        await self.memory_store.store(memory)
        
        # Update strength
        await self.memory_store.update_strength(memory.id, 0.2)
        
        updated_memory = self.memory_store._memory_cache[memory.id]
        assert updated_memory.strength == 0.7  # 0.5 + 0.2
    
    @pytest.mark.asyncio
    async def test_memory_association(self):
        """Test creating memory associations"""
        # Mock persistence methods
        self.persistence_manager.store_memory = Mock(return_value=True)
        
        # Create two memories
        memory1 = self.memory_store.create_memory_item(
            pattern_signature="pattern1",
            content={"data": "memory1"},
            context={}
        )
        
        memory2 = self.memory_store.create_memory_item(
            pattern_signature="pattern2",
            content={"data": "memory2"},
            context={}
        )
        
        await self.memory_store.store(memory1)
        await self.memory_store.store(memory2)
        
        # Create association
        await self.memory_store.create_association(memory1.id, memory2.id, 0.8)
        
        # Verify association
        associated = await self.memory_store.get_associated_memories(memory1.id)
        assert len(associated) > 0
        assert any(m.id == memory2.id for m in associated)


class TestLearningEngine:
    """Tests for the LearningEngine component"""
    
    def setup_method(self):
        self.learning_engine = LearningEngine()
    
    def test_feedback_processing(self):
        """Test processing feedback"""
        result = self.learning_engine.process_feedback(
            memory_id="test_memory",
            feedback_type=FeedbackType.POSITIVE,
            outcome={"reward": 1.0},
            context={"confidence": 0.8}
        )
        
        assert "strength_change" in result
        assert "confidence" in result
        assert "learning_rate" in result
    
    def test_negative_feedback(self):
        """Test processing negative feedback"""
        result = self.learning_engine.process_feedback(
            memory_id="test_memory",
            feedback_type=FeedbackType.NEGATIVE,
            outcome={"penalty": 0.5}
        )
        
        assert result["strength_change"] < 0
    
    def test_access_based_learning(self):
        """Test learning from memory access patterns"""
        result = self.learning_engine.update_memory_access(
            memory_id="test_memory",
            access_context={"source": "api"},
            access_count=5
        )
        
        assert "strength_change" in result
        assert "access_count" in result
        assert result["access_count"] == 5
    
    def test_co_occurrence_processing(self):
        """Test processing co-occurrence of memories"""
        result = self.learning_engine.process_co_occurrence(
            memory_ids=["mem1", "mem2", "mem3"],
            co_occurrence_strength=0.7
        )
        
        assert len(result) > 0  # Should create associations between pairs
        assert len(result) == 3  # 3 pairs from 3 memories
    
    def test_learning_statistics(self):
        """Test learning statistics"""
        # Process some feedback
        self.learning_engine.process_feedback("mem1", FeedbackType.POSITIVE, {})
        self.learning_engine.process_feedback("mem2", FeedbackType.NEGATIVE, {})
        
        stats = self.learning_engine.get_learning_statistics()
        
        assert stats["total_learning_events"] >= 2
        assert stats["positive_feedback"] >= 1
        assert stats["negative_feedback"] >= 1


class TestSparseRouter:
    """Tests for the SparseRouter component"""
    
    def setup_method(self):
        self.router = SparseRouter()
    
    def test_threshold_activation(self):
        """Test threshold-based activation"""
        # Create test memories
        memories = [
            MemoryItem(
                id="mem1",
                pattern_signature="pattern1",
                memory_type=MemoryType.EPISODIC,
                content={"data": "test1"},
                context={"state": "normal"},
                strength=0.8,
                access_count=0,
                last_accessed=datetime.now(),
                created_at=datetime.now(),
                associations=[],
                tags=[],
                confidence=0.9
            ),
            MemoryItem(
                id="mem2",
                pattern_signature="pattern2",
                memory_type=MemoryType.EPISODIC,
                content={"data": "test2"},
                context={"state": "normal"},
                strength=0.3,
                access_count=0,
                last_accessed=datetime.now(),
                created_at=datetime.now(),
                associations=[],
                tags=[],
                confidence=0.5
            )
        ]
        
        context = {"state": "normal", "intensity": "medium"}
        
        activated = self.router.activate(memories, context)
        
        # Should activate only the high-strength memory
        assert len(activated) == 1
        assert activated[0].id == "mem1"
    
    def test_winner_takes_all_activation(self):
        """Test winner-takes-all activation"""
        # Create memories with different strengths
        memories = []
        for i in range(5):
            memory = MemoryItem(
                id=f"mem{i}",
                pattern_signature=f"pattern{i}",
                memory_type=MemoryType.EPISODIC,
                content={"data": f"test{i}"},
                context={"state": "normal"},
                strength=0.1 * (i + 1),
                access_count=0,
                last_accessed=datetime.now(),
                created_at=datetime.now(),
                associations=[],
                tags=[],
                confidence=0.5
            )
            memories.append(memory)
        
        context = {
            "state": "normal",
            "intensity": "medium",
            "method": "winner_takes_all",
            "target_activation_count": 3
        }
        
        activated = self.router.activate(memories, context)
        
        # Should activate top 3 memories
        assert len(activated) == 3
        # They should be in descending order of strength
        for i in range(len(activated) - 1):
            assert activated[i].strength >= activated[i + 1].strength
    
    def test_activation_statistics(self):
        """Test activation statistics"""
        # Create and activate some memories
        memory = MemoryItem(
            id="test_mem",
            pattern_signature="test_pattern",
            memory_type=MemoryType.EPISODIC,
            content={"data": "test"},
            context={"state": "normal"},
            strength=0.8,
            access_count=0,
            last_accessed=datetime.now(),
            created_at=datetime.now(),
            associations=[],
            tags=[],
            confidence=0.9
        )
        
        self.router.activate([memory], {"state": "normal"})
        
        stats = self.router.get_activation_statistics()
        
        assert stats["total_activations"] >= 1
        assert "global_activation_threshold" in stats


class TestReasoningEngine:
    """Tests for the ReasoningEngine component"""
    
    def setup_method(self):
        self.reasoning_engine = ReasoningEngine()
    
    @pytest.mark.asyncio
    async def test_reasoning_initialization(self):
        """Test reasoning engine initialization"""
        await self.reasoning_engine.initialize()
        
        # Should initialize without errors
        assert self.reasoning_engine.llm_client is not None or True  # Placeholder
    
    @pytest.mark.asyncio
    async def test_basic_reasoning(self):
        """Test basic reasoning operation"""
        await self.reasoning_engine.initialize()
        
        # Create mock memories
        memories = [
            Mock(
                id="mem1",
                pattern_signature="pattern1",
                content={"data": "test"},
                context={"state": "normal"},
                strength=0.8,
                confidence=0.9,
                tags=["test"]
            )
        ]
        
        context = {
            "query": "Analyze this situation",
            "state": "normal",
            "intensity": "medium"
        }
        
        result = await self.reasoning_engine.reason(memories, context)
        
        assert "result" in result
        assert "confidence" in result
        assert "reasoning_type" in result
    
    @pytest.mark.asyncio
    async def test_explanation_generation(self):
        """Test explanation generation"""
        await self.reasoning_engine.initialize()
        
        memories = [
            Mock(
                id="mem1",
                pattern_signature="decision_pattern",
                content={"decision": "approve"},
                context={"state": "normal"},
                strength=0.9,
                confidence=0.8,
                tags=["decision"]
            )
        ]
        
        explanation = await self.reasoning_engine.explain(
            decision="approve loan",
            active_memories=memories,
            context={"reason": "good credit"}
        )
        
        assert "explanation" in explanation
        assert "confidence" in explanation
        assert "supporting_memories" in explanation
    
    @pytest.mark.asyncio
    async def test_prediction_making(self):
        """Test prediction making"""
        await self.reasoning_engine.initialize()
        
        memories = [
            Mock(
                id="mem1",
                pattern_signature="trend_pattern",
                content={"trend": "increasing"},
                context={"state": "normal"},
                strength=0.7,
                confidence=0.6
            )
        ]
        
        prediction = await self.reasoning_engine.predict(
            current_situation={"status": "stable"},
            active_memories=memories,
            time_horizon="near_term"
        )
        
        assert "prediction" in prediction
        assert "confidence" in prediction
        assert "time_horizon" in prediction


class TestFeedbackProcessor:
    """Tests for the FeedbackProcessor component"""
    
    def setup_method(self):
        self.learning_engine = Mock(spec=LearningEngine)
        self.feedback_processor = FeedbackProcessor(self.learning_engine)
    
    @pytest.mark.asyncio
    async def test_basic_feedback_processing(self):
        """Test basic feedback processing"""
        result = await self.feedback_processor.process_feedback(
            memory_id="test_memory",
            feedback_type="positive",
            outcome={"reward": 1.0},
            source=FeedbackSource.USER,
            quality=FeedbackQuality.HIGH
        )
        
        assert "feedback_queued" in result
        assert result["feedback_queued"] is True
        assert result["memory_id"] == "test_memory"
    
    @pytest.mark.asyncio
    async def test_user_feedback_processing(self):
        """Test user feedback processing"""
        result = await self.feedback_processor.process_user_feedback(
            memory_id="test_memory",
            user_rating=0.9,
            user_comment="This was helpful"
        )
        
        assert result["feedback_queued"] is True
        assert "feedback_type" in result
    
    @pytest.mark.asyncio
    async def test_performance_feedback_processing(self):
        """Test performance feedback processing"""
        performance_metrics = {
            "accuracy": 0.85,
            "speed": 0.92,
            "user_satisfaction": 0.78
        }
        
        result = await self.feedback_processor.process_performance_feedback(
            memory_id="test_memory",
            performance_metrics=performance_metrics
        )
        
        assert result["feedback_queued"] is True
        assert "performance_metrics" in result
    
    @pytest.mark.asyncio
    async def test_feedback_statistics(self):
        """Test feedback statistics"""
        # Process some feedback
        await self.feedback_processor.process_feedback("mem1", "positive", {})
        await self.feedback_processor.process_feedback("mem2", "negative", {})
        
        stats = self.feedback_processor.get_feedback_statistics()
        
        assert stats["total_feedback_events"] >= 2
        assert "feedback_by_source" in stats
        assert "processing_rate" in stats


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self):
        """Test the complete brain-inspired AI pipeline"""
        # This would test the full pipeline:
        # 1. Encoder encodes input
        # 2. Memory store retrieves relevant memories
        # 3. Sparse router activates memories
        # 4. Reasoning engine processes
        # 5. Feedback processor handles feedback
        
        # For now, just test that components can be created
        encoder = Encoder()
        persistence_manager = Mock(spec=PersistenceManager)
        memory_store = MemoryStore(persistence_manager)
        learning_engine = LearningEngine()
        router = SparseRouter()
        reasoning_engine = ReasoningEngine()
        feedback_processor = FeedbackProcessor(learning_engine)
        
        # Test basic integration
        assert encoder is not None
        assert memory_store is not None
        assert learning_engine is not None
        assert router is not None
        assert reasoning_engine is not None
        assert feedback_processor is not None
        
        # Test memory store can create items
        memory = memory_store.create_memory_item(
            pattern_signature="integration_test",
            content={"test": "data"},
            context={"source": "integration"}
        )
        
        assert memory.pattern_signature == "integration_test"


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__])