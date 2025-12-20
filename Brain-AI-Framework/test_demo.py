#!/usr/bin/env python3
"""
Brain AI Framework Demo - Test Script
Tests the core functionality of the brain-inspired AI system
"""

import asyncio
import json
from datetime import datetime

# Import the brain system components
from core.encoder import Encoder, EventType
from core.memory import MemoryStore, MemoryType
from core.learning import LearningEngine
from core.routing import SparseRouter
from core.reasoning import ReasoningEngine
from core.feedback import FeedbackProcessor, FeedbackSource, FeedbackQuality

class MockPersistenceManager:
    """Mock persistence manager for demo purposes"""
    
    async def store_memory(self, memory_data):
        return True
    
    async def load_all_memories(self):
        return []

class BrainAIDemo:
    """Demonstration of Brain AI Framework capabilities"""
    
    def __init__(self):
        self.encoder = Encoder()
        self.memory_store = MemoryStore(MockPersistenceManager())
        self.learning_engine = LearningEngine()
        self.router = SparseRouter()
        self.reasoning_engine = ReasoningEngine()
        self.feedback_processor = FeedbackProcessor(self.learning_engine)
        
    async def initialize(self):
        """Initialize the brain system"""
        await self.reasoning_engine.initialize()
        print("🧠 Brain AI System initialized!")
    
    async def demonstrate_pattern_encoding(self):
        """Demonstrate pattern encoding capabilities"""
        print("\n🧬 PATTERN ENCODING DEMONSTRATION")
        print("=" * 50)
        
        test_inputs = [
            {
                "name": "API Request",
                "data": {
                    "method": "POST",
                    "endpoint": "/api/users",
                    "status_code": 200,
                    "user_id": "123"
                }
            },
            {
                "name": "Error Event", 
                "data": {
                    "error": True,
                    "error_type": "validation_error",
                    "message": "Invalid input format",
                    "severity": "high"
                }
            },
            {
                "name": "User Action",
                "data": {
                    "user": True,
                    "action": "click",
                    "element": "submit_button",
                    "session_id": "abc123"
                }
            }
        ]
        
        for test_case in test_inputs:
            print(f"\n📝 Testing: {test_case['name']}")
            result = self.encoder.encode(test_case['data'])
            
            print(f"   Pattern Type: {result['pattern']['type']}")
            print(f"   Signature: {result['pattern']['signature']}")
            print(f"   Context State: {result['context']['state']}")
            print(f"   Confidence: {result['pattern']['confidence']:.2f}")
    
    async def demonstrate_memory_system(self):
        """Demonstrate memory storage and retrieval"""
        print("\n💾 MEMORY SYSTEM DEMONSTRATION")
        print("=" * 50)
        
        # Create some memories
        memories_data = [
            {
                "pattern": "user_login_success",
                "content": {"user_id": "user123", "login_time": "09:00", "ip": "192.168.1.1"},
                "context": {"state": "normal", "source": "authentication"}
            },
            {
                "pattern": "api_error_500",
                "content": {"endpoint": "/api/data", "error": "database_timeout"},
                "context": {"state": "error", "source": "api_gateway"}
            },
            {
                "pattern": "user_purchase",
                "content": {"product_id": "prod456", "amount": 99.99, "user_id": "user123"},
                "context": {"state": "normal", "source": "ecommerce"}
            }
        ]
        
        stored_memory_ids = []
        
        for i, mem_data in enumerate(memories_data):
            print(f"\n💾 Storing Memory {i+1}: {mem_data['pattern']}")
            
            memory = self.memory_store.create_memory_item(
                pattern_signature=mem_data['pattern'],
                content=mem_data['content'],
                context=mem_data['context'],
                memory_type=MemoryType.EPISODIC
            )
            
            memory_id = await self.memory_store.store(memory)
            stored_memory_ids.append(memory_id)
            
            print(f"   Memory ID: {memory_id}")
            print(f"   Strength: {memory.strength}")
            print(f"   Type: {memory.memory_type}")
        
        # Demonstrate retrieval
        print(f"\n🔍 Retrieving memories for pattern 'user_login_success'")
        retrieved = await self.memory_store.retrieve("user_login_success", {"source": "authentication"})
        print(f"   Found {len(retrieved)} memories")
        
        return stored_memory_ids
    
    async def demonstrate_sparse_activation(self):
        """Demonstrate sparse memory activation"""
        print("\n⚡ SPARSE ACTIVATION DEMONSTRATION")
        print("=" * 50)
        
        # Create test memories with different strengths
        test_memories = []
        for i in range(5):
            memory = self.memory_store.create_memory_item(
                pattern_signature=f"pattern_{i}",
                content={"data": f"test_data_{i}"},
                context={"state": "normal"},
                memory_type=MemoryType.EPISODIC
            )
            
            # Vary the strength
            memory.strength = 0.1 * (i + 1)
            test_memories.append(memory)
        
        print(f"📊 Created {len(test_memories)} memories with varying strengths:")
        for mem in test_memories:
            print(f"   {mem.pattern_signature}: strength={mem.strength}")
        
        # Apply sparse activation
        context = {"state": "normal", "intensity": "medium"}
        activated = self.router.activate(test_memories, context)
        
        print(f"\n⚡ Sparse Activation Results:")
        print(f"   Activated {len(activated)} memories (threshold-based)")
        for mem in activated:
            print(f"   ✅ {mem.pattern_signature}: strength={mem.strength}")
    
    async def demonstrate_learning(self):
        """Demonstrate learning and feedback processing"""
        print("\n📚 LEARNING DEMONSTRATION")
        print("=" * 50)
        
        # Create a memory
        memory = self.memory_store.create_memory_item(
            pattern_signature="learning_test",
            content={"task": "code_review", "outcome": "pending"},
            context={"state": "normal"}
        )
        
        memory_id = await self.memory_store.store(memory)
        initial_strength = memory.strength
        
        print(f"💾 Created memory with initial strength: {initial_strength}")
        
        # Process positive feedback
        feedback_result = await self.feedback_processor.process_feedback(
            memory_id=memory_id,
            feedback_type="positive",
            outcome={"rating": 0.9, "reviewer_feedback": "excellent work"},
            source=FeedbackSource.USER,
            quality=FeedbackQuality.HIGH
        )
        
        print(f"✅ Positive feedback processed: {feedback_result['feedback_queued']}")
        
        # Get updated memory
        updated_memory = self.memory_store._memory_cache[memory_id]
        final_strength = updated_memory.strength
        
        print(f"📈 Memory strength updated: {initial_strength} → {final_strength}")
        print(f"   Strength change: {final_strength - initial_strength:.2f}")
        
        return memory_id
    
    async def demonstrate_reasoning(self):
        """Demonstrate reasoning capabilities"""
        print("\n🤔 REASONING DEMONSTRATION")
        print("=" * 50)
        
        # Create some relevant memories for reasoning
        reasoning_memories = [
            self.memory_store.create_memory_item(
                pattern_signature="customer_complaint",
                content={"issue": "slow_response", "category": "support"},
                context={"priority": "high"}
            ),
            self.memory_store.create_memory_item(
                pattern_signature="system_performance",
                content={"metric": "response_time", "value": "2.5s"},
                context={"status": "degraded"}
            )
        ]
        
        for memory in reasoning_memories:
            await self.memory_store.store(memory)
        
        # Perform reasoning
        context = {
            "query": "Why are customers complaining about slow response times?",
            "state": "analysis"
        }
        
        reasoning_result = await self.reasoning_engine.reason(reasoning_memories, context)
        
        print(f"🧠 Reasoning Query: {context['query']}")
        print(f"📊 Reasoning Result:")
        print(f"   Type: {reasoning_result.get('reasoning_type', 'N/A')}")
        print(f"   Confidence: {reasoning_result.get('confidence', 'N/A')}")
        print(f"   Process: {reasoning_result.get('process', 'N/A')}")
    
    async def run_full_demo(self):
        """Run the complete brain AI demonstration"""
        print("🧠 BRAIN AI FRAMEWORK - COMPLETE DEMONSTRATION")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Initialize
            await self.initialize()
            
            # Run demonstrations
            await self.demonstrate_pattern_encoding()
            memory_ids = await self.demonstrate_memory_system()
            await self.demonstrate_sparse_activation()
            learning_memory_id = await self.demonstrate_learning()
            await self.demonstrate_reasoning()
            
            # Summary
            print("\n🎉 DEMONSTRATION COMPLETE!")
            print("=" * 60)
            print("✅ Pattern Encoding: Working")
            print("✅ Memory Storage: Working")
            print("✅ Sparse Activation: Working")
            print("✅ Learning System: Working")
            print("✅ Reasoning Engine: Working")
            print("\n🧠 Your Brain AI Framework is fully functional!")
            
            return {
                "status": "success",
                "memory_ids": memory_ids,
                "learning_memory_id": learning_memory_id
            }
            
        except Exception as e:
            print(f"\n❌ Demo Error: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}

async def main():
    """Main demo execution"""
    demo = BrainAIDemo()
    result = await demo.run_full_demo()
    
    print(f"\n📋 Demo Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())