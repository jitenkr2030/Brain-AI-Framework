#!/usr/bin/env python3
"""
Brain-Inspired AI Framework Python SDK
Easy-to-use Python client for the Brain-Inspired AI Framework.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import aiohttp
from loguru import logger


@dataclass
class Memory:
    """Represents a memory item"""
    id: str
    pattern_signature: str
    memory_type: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    strength: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    associations: List[str]
    tags: List[str]
    confidence: float


@dataclass
class ReasoningResult:
    """Represents a reasoning result"""
    result: str
    confidence: float
    reasoning_type: str
    execution_time: float
    tokens_used: int
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class ProcessingResult:
    """Represents a processing result"""
    encoded_event: Dict[str, Any]
    active_memories: List[Memory]
    reasoning_result: ReasoningResult
    memory_count: int
    execution_time: float
    processing_metadata: Dict[str, Any]


@dataclass
class SystemStatus:
    """Represents system status"""
    status: str
    brain_initialized: bool
    uptime: float
    memory_count: int
    total_operations: int
    health_check: Dict[str, Any]


class BrainAI:
    """
    Brain-Inspired AI Framework Python SDK
    
    Provides an easy-to-use interface for the Brain-Inspired AI Framework.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        retries: int = 3
    ):
        """
        Initialize the Brain AI client
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the Brain AI API
            timeout: Request timeout in seconds
            retries: Number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        self.timeout = timeout
        self.retries = retries
        
        # Session for connection pooling
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
    
    async def close(self):
        """Close the client session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check system health
        
        Returns:
            Health check information
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.api_url}/health") as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    async def process(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        reasoning_type: str = "analysis"
    ) -> ProcessingResult:
        """
        Process input through the brain system
        
        Args:
            data: Input data to process
            context: Additional context
            reasoning_type: Type of reasoning to perform
            
        Returns:
            Processing result with active memories and reasoning
        """
        await self._ensure_session()
        
        payload = {
            "data": data,
            "context": context or {},
            "reasoning_type": reasoning_type
        }
        
        try:
            async with self.session.post(f"{self.api_url}/process", json=payload) as response:
                response.raise_for_status()
                result = await response.json()
                
                # Convert to typed objects
                active_memories = [
                    Memory(**memory_data) for memory_data in result.get("active_memories", [])
                ]
                
                reasoning_result = ReasoningResult(
                    **result.get("reasoning_result", {})
                )
                
                return ProcessingResult(
                    encoded_event=result.get("encoded_event", {}),
                    active_memories=active_memories,
                    reasoning_result=reasoning_result,
                    memory_count=result.get("memory_count", 0),
                    execution_time=result.get("execution_time", 0.0),
                    processing_metadata=result.get("processing_metadata", {})
                )
                
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    
    async def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Simple thinking interface - just provide a query and get a response
        
        Args:
            query: Your question or input
            context: Additional context
            
        Returns:
            AI response
        """
        result = await self.process(
            data={"query": query},
            context=context,
            reasoning_type="analysis"
        )
        return result.reasoning_result.result
    
    async def learn(
        self,
        experience: str,
        feedback: Union[str, Dict[str, Any]],
        outcome: Optional[Dict[str, Any]] = None
    ):
        """
        Provide feedback to help the AI learn
        
        Args:
            experience: What happened
            feedback: Feedback type ("positive", "negative", "neutral") or detailed feedback
            outcome: Outcome information
        """
        # For now, this is a placeholder - the full learning interface
        # would need access to specific memory IDs
        logger.info(f"Learning from experience: {experience}")
        logger.info(f"Feedback: {feedback}")
    
    async def explain(self, decision: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Explain a decision using memory
        
        Args:
            decision: Decision to explain
            context: Context of the decision
            
        Returns:
            Explanation with supporting evidence
        """
        await self._ensure_session()
        
        payload = {
            "decision": decision,
            "context": context or {}
        }
        
        try:
            async with self.session.post(f"{self.api_url}/explain", json=payload) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
            raise
    
    async def predict(
        self,
        situation: Dict[str, Any],
        time_horizon: str = "near_term"
    ) -> Dict[str, Any]:
        """
        Make a prediction based on current situation
        
        Args:
            situation: Current situation description
            time_horizon: Prediction time horizon
            
        Returns:
            Prediction with confidence and reasoning
        """
        await self._ensure_session()
        
        payload = {
            "situation": situation,
            "time_horizon": time_horizon
        }
        
        try:
            async with self.session.post(f"{self.api_url}/predict", json=payload) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    async def plan(
        self,
        goal: str,
        constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an action plan to achieve a goal
        
        Args:
            goal: Goal to achieve
            constraints: Planning constraints
            
        Returns:
            Action plan with steps and rationale
        """
        await self._ensure_session()
        
        payload = {
            "goal": goal,
            "constraints": constraints or []
        }
        
        try:
            async with self.session.post(f"{self.api_url}/plan", json=payload) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            raise
    
    async def get_memories(self, limit: int = 100) -> List[Memory]:
        """
        Get current memories
        
        Args:
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memory objects
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.api_url}/memories?limit={limit}") as response:
                response.raise_for_status()
                data = await response.json()
                
                memories = [
                    Memory(**memory_data) for memory_data in data.get("memories", [])
                ]
                
                return memories
                
        except Exception as e:
            logger.error(f"Failed to get memories: {e}")
            raise
    
    async def get_status(self) -> SystemStatus:
        """
        Get comprehensive system status
        
        Returns:
            System status information
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.api_url}/status") as response:
                response.raise_for_status()
                data = await response.json()
                
                return SystemStatus(
                    status=data.get("status", "unknown"),
                    brain_initialized=data.get("brain_system", {}).get("initialized", False),
                    uptime=data.get("uptime", 0.0),
                    memory_count=data.get("brain_system", {}).get("memory_count", 0),
                    total_operations=data.get("statistics", {}).get("total_operations", 0),
                    health_check=data.get("statistics", {}).get("health_check", {})
                )
                
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            raise
    
    async def test(self) -> Dict[str, Any]:
        """
        Run system test
        
        Returns:
            Test results
        """
        await self._ensure_session()
        
        try:
            async with self.session.post(f"{self.api_url}/test") as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"System test failed: {e}")
            raise
    
    # Convenience methods for common use cases
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Simple chat interface
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            
        Returns:
            AI response
        """
        context = {"chat_mode": True}
        if conversation_history:
            context["conversation_history"] = conversation_history
        
        result = await self.process(
            data={"message": message, "type": "chat"},
            context=context,
            reasoning_type="analysis"
        )
        
        return result.reasoning_result.result
    
    async def analyze_text(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze text content
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis
            
        Returns:
            Analysis results
        """
        result = await self.process(
            data={"text": text, "analysis_type": analysis_type},
            context={"source": "text_analysis"},
            reasoning_type="analysis"
        )
        
        return {
            "analysis": result.reasoning_result.result,
            "active_memories": [m.pattern_signature for m in result.active_memories],
            "confidence": result.reasoning_result.confidence,
            "processing_time": result.execution_time
        }
    
    async def make_recommendation(
        self,
        user_profile: Dict[str, Any],
        context: Dict[str, Any],
        recommendation_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Make a recommendation based on user profile and context
        
        Args:
            user_profile: User profile information
            context: Current context
            recommendation_type: Type of recommendation
            
        Returns:
            Recommendation with reasoning
        """
        result = await self.process(
            data={
                "user_profile": user_profile,
                "recommendation_type": recommendation_type
            },
            context=context,
            reasoning_type="analysis"
        )
        
        return {
            "recommendation": result.reasoning_result.result,
            "confidence": result.reasoning_result.confidence,
            "supporting_memories": len(result.active_memories),
            "reasoning_trace": result.reasoning_result.metadata
        }
    
    async def get_insights(
        self,
        query: str,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get insights based on query and time range
        
        Args:
            query: Insight query
            time_range: Time range for insights
            
        Returns:
            Insights with supporting evidence
        """
        context = {"insight_mode": True}
        if time_range:
            context["time_range"] = time_range
        
        result = await self.process(
            data={"insight_query": query},
            context=context,
            reasoning_type="analysis"
        )
        
        return {
            "insights": result.reasoning_result.result,
            "related_memories": [
                {
                    "pattern": m.pattern_signature,
                    "strength": m.strength,
                    "type": m.memory_type
                }
                for m in result.active_memories
            ],
            "confidence": result.reasoning_result.confidence
        }


# Synchronous wrapper for backward compatibility
class SyncBrainAI:
    """Synchronous wrapper for BrainAI"""
    
    def __init__(self, *args, **kwargs):
        self._async_brain = BrainAI(*args, **kwargs)
        self._loop = None
    
    def _ensure_loop(self):
        """Ensure event loop is running"""
        import asyncio
        try:
            self._loop = asyncio.get_event_loop()
            if self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
    
    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        self._ensure_loop()
        return self._loop.run_until_complete(coro)
    
    def health_check(self) -> Dict[str, Any]:
        return self._run_async(self._async_brain.health_check())
    
    def process(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None, reasoning_type: str = "analysis") -> ProcessingResult:
        return self._run_async(self._async_brain.process(data, context, reasoning_type))
    
    def think(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        return self._run_async(self._async_brain.think(query, context))
    
    def explain(self, decision: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._run_async(self._async_brain.explain(decision, context))
    
    def predict(self, situation: Dict[str, Any], time_horizon: str = "near_term") -> Dict[str, Any]:
        return self._run_async(self._async_brain.predict(situation, time_horizon))
    
    def plan(self, goal: str, constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        return self._run_async(self._async_brain.plan(goal, constraints))
    
    def get_memories(self, limit: int = 100) -> List[Memory]:
        return self._run_async(self._async_brain.get_memories(limit))
    
    def get_status(self) -> SystemStatus:
        return self._run_async(self._async_brain.get_status())
    
    def test(self) -> Dict[str, Any]:
        return self._run_async(self._async_brain.test())
    
    def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        return self._run_async(self._async_brain.chat(message, conversation_history))
    
    def analyze_text(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        return self._run_async(self._async_brain.analyze_text(text, analysis_type))
    
    def make_recommendation(self, user_profile: Dict[str, Any], context: Dict[str, Any], recommendation_type: str = "general") -> Dict[str, Any]:
        return self._run_async(self._async_brain.make_recommendation(user_profile, context, recommendation_type))
    
    def get_insights(self, query: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        return self._run_async(self._async_brain.get_insights(query, time_range))


# Convenience function for quick start
def create_brain_ai(api_key: Optional[str] = None, base_url: str = "http://localhost:8000") -> BrainAI:
    """
    Create a Brain AI instance with default settings
    
    Args:
        api_key: API key for authentication
        base_url: Base URL for the API
        
    Returns:
        BrainAI instance
    """
    return BrainAI(api_key=api_key, base_url=base_url)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize Brain AI
        brain = BrainAI(base_url="http://localhost:8000")
        
        try:
            # Check health
            health = await brain.health_check()
            print(f"System health: {health}")
            
            # Process some input
            result = await brain.process({
                "user_input": "I need help with machine learning",
                "context": "learning"
            })
            
            print(f"AI response: {result.reasoning_result.result}")
            print(f"Active memories: {len(result.active_memories)}")
            
            # Get system status
            status = await brain.get_status()
            print(f"System status: {status.status}")
            
        finally:
            await brain.close()
    
    # Run example
    asyncio.run(main())