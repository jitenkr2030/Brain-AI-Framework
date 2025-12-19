#!/usr/bin/env python3
"""
Brain AI Integration Module
Shared utilities for integrating Brain AI Framework with example applications
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from loguru import logger

# Import Brain AI components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.encoder import Encoder, EventType, ContextState
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


class BrainAIWrapper:
    """
    Simplified Brain AI wrapper for example applications
    Provides a clean interface for integrating Brain AI capabilities
    """
    
    def __init__(self, application_name: str = "BrainAIApp"):
        self.application_name = application_name
        self.encoder = Encoder()
        self.memory_store = MemoryStore(MockPersistenceManager())
        self.learning_engine = LearningEngine()
        self.router = SparseRouter()
        self.reasoning_engine = ReasoningEngine()
        self.feedback_processor = FeedbackProcessor(self.learning_engine)
        self.initialized = False
        
        logger.info(f"🧠 {application_name} Brain AI Wrapper initialized")
    
    async def initialize(self):
        """Initialize the Brain AI system"""
        try:
            await self.reasoning_engine.initialize()
            self.initialized = True
            logger.info(f"✅ {self.application_name} Brain AI system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize {self.application_name} Brain AI: {e}")
            raise
    
    async def process_input(self, data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process input through the Brain AI pipeline
        
        Args:
            data: Input data to process
            context: Additional context information
            
        Returns:
            Dict containing processing results and insights
        """
        if not self.initialized:
            await self.initialize()
        
        context = context or {}
        
        try:
            # Step 1: Encode input into patterns
            encoded = self.encoder.encode(data)
            pattern = encoded["pattern"]
            context_info = encoded["context"]
            
            # Add application context
            context_info["application"] = self.application_name
            context_info.update(context)
            
            logger.debug(f"Processing {pattern['type']} pattern: {pattern['signature']}")
            
            # Step 2: Create memory from pattern
            memory = self.memory_store.create_memory_item(
                pattern_signature=pattern["signature"],
                content={"data": data, "pattern": pattern, "application": self.application_name},
                context=context_info,
                memory_type=MemoryType.EPISODIC
            )
            
            # Store memory
            memory_id = await self.memory_store.store(memory)
            
            # Step 3: Retrieve relevant memories
            relevant_memories = await self.memory_store.retrieve(
                pattern["signature"], 
                context_info
            )
            
            # Step 4: Apply sparse activation
            active_memories = self.router.activate(
                relevant_memories, 
                context_info
            )
            
            # Step 5: Generate insights through reasoning
            reasoning_result = await self.reasoning_engine.reason(
                active_memories, 
                {**context_info, "query": f"Analyze {self.application_name} data: {str(data)[:100]}"}
            )
            
            return {
                "success": True,
                "memory_id": memory_id,
                "pattern": pattern,
                "context": context_info,
                "active_memories": [mem.to_dict() for mem in active_memories],
                "reasoning_result": reasoning_result,
                "total_memories": len(relevant_memories),
                "insights": self._generate_insights(reasoning_result, pattern, active_memories),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing input in {self.application_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_insights(self, reasoning_result: Dict[str, Any], pattern: Dict[str, Any], 
                          active_memories: List) -> List[str]:
        """Generate human-readable insights from Brain AI results"""
        insights = []
        
        # Pattern-based insights
        if pattern["type"] == "error":
            insights.append("⚠️ Error pattern detected - consider investigation")
        elif pattern["type"] == "user_action":
            insights.append("👤 User interaction recorded - learning from behavior")
        elif pattern["confidence"] > 0.7:
            insights.append(f"🎯 High confidence pattern ({pattern['confidence']:.2f})")
        
        # Memory-based insights
        if len(active_memories) > 0:
            insights.append(f"💾 Found {len(active_memories)} relevant memories")
            
            # Analyze memory strengths
            avg_strength = sum(mem.strength for mem in active_memories) / len(active_memories)
            if avg_strength > 0.7:
                insights.append("🧠 Strong memory patterns identified")
            elif avg_strength < 0.3:
                insights.append("🔄 New patterns forming - system learning")
        
        # Reasoning-based insights
        if reasoning_result.get("confidence", 0) > 0.6:
            insights.append(f"🤔 High confidence analysis ({reasoning_result['confidence']:.2f})")
        
        return insights
    
    async def provide_feedback(self, memory_id: str, feedback_type: str, 
                             outcome: Dict[str, Any], source: str = "user") -> Dict[str, Any]:
        """
        Provide feedback to improve Brain AI learning
        
        Args:
            memory_id: ID of memory to update
            feedback_type: Type of feedback (positive, negative, neutral)
            outcome: Feedback outcome data
            source: Source of feedback
            
        Returns:
            Dict containing feedback processing results
        """
        try:
            result = await self.feedback_processor.process_feedback(
                memory_id=memory_id,
                feedback_type=feedback_type,
                outcome=outcome,
                source=FeedbackSource(source),
                quality=FeedbackQuality.HIGH
            )
            
            logger.info(f"Feedback processed for {memory_id}: {feedback_type}")
            
            return {
                "success": True,
                "feedback_queued": result["feedback_queued"],
                "memory_id": memory_id,
                "feedback_type": feedback_type,
                "message": f"Feedback processed successfully - {feedback_type} impact recorded"
            }
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return {
                "success": False,
                "error": str(e),
                "memory_id": memory_id
            }
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for relevant memories
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            # Create search context
            search_context = {
                "query": query,
                "search_type": "semantic",
                "application": self.application_name
            }
            
            # Encode search query
            encoded_query = self.encoder.encode({"search": query})
            
            # Retrieve memories
            memories = await self.memory_store.retrieve(
                encoded_query["pattern"]["signature"],
                search_context
            )
            
            return [mem.to_dict() for mem in memories[:limit]]
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get Brain AI system statistics
        
        Returns:
            Dict containing system statistics
        """
        try:
            return {
                "application": self.application_name,
                "initialized": self.initialized,
                "encoder_stats": self.encoder.get_pattern_stats(),
                "router_stats": self.router.get_activation_statistics(),
                "learning_stats": self.learning_engine.get_learning_statistics(),
                "memory_count": len(self.memory_store._memory_cache),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}
    
    async def get_memories(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get stored memories
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of memory dictionaries
        """
        try:
            all_memories = list(self.memory_store._memory_cache.values())
            
            # Sort by creation time (newest first)
            sorted_memories = sorted(
                all_memories, 
                key=lambda x: x.created_at, 
                reverse=True
            )
            
            return [mem.to_dict() for mem in sorted_memories[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return []


# Utility functions for common Brain AI operations

async def create_demo_session(app_name: str) -> BrainAIWrapper:
    """
    Create a new Brain AI session for demo purposes
    
    Args:
        app_name: Name of the application
        
    Returns:
        Initialized BrainAIWrapper instance
    """
    brain_ai = BrainAIWrapper(app_name)
    await brain_ai.initialize()
    return brain_ai


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def format_memory_for_display(memory: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format memory for display in web interfaces
    
    Args:
        memory: Memory dictionary
        
    Returns:
        Formatted memory for display
    """
    return {
        "id": memory["id"],
        "pattern": memory["pattern_signature"],
        "type": memory["memory_type"],
        "strength": f"{memory['strength']:.2f}",
        "access_count": memory["access_count"],
        "created_at": datetime.fromisoformat(memory["created_at"]).strftime("%Y-%m-%d %H:%M"),
        "last_accessed": datetime.fromisoformat(memory["last_accessed"]).strftime("%Y-%m-%d %H:%M"),
        "content_preview": str(memory["content"])[:100] + "..." if len(str(memory["content"])) > 100 else str(memory["content"])
    }


def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Create a standardized success response
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Standardized success response
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }


def create_error_response(error: str, code: int = 400) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        error: Error message
        code: HTTP status code
        
    Returns:
        Standardized error response
    """
    return {
        "success": False,
        "error": error,
        "code": code,
        "timestamp": datetime.now().isoformat()
    }
