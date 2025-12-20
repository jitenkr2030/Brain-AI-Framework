"""
Reasoning Engine
LLM-based reasoning system that uses memory without modifying it.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import asyncio
from loguru import logger

from app.config import get_settings


class ReasoningType(Enum):
    """Types of reasoning operations"""
    ANALYSIS = "analysis"           # Analyze patterns and relationships
    EXPLANATION = "explanation"     # Explain decisions and outcomes
    PREDICTION = "prediction"       # Predict future outcomes
    PLANNING = "planning"          # Create action plans
    SYNTHESIS = "synthesis"        # Synthesize information
    COMPARISON = "comparison"      # Compare alternatives
    EVALUATION = "evaluation"      # Evaluate options
    DEBUGGING = "debugging"        # Debug problems


class ReasoningOutput(Enum):
    """Types of reasoning outputs"""
    TEXT = "text"                  # Natural language response
    JSON = "json"                  # Structured data
    PLAN = "plan"                  # Action plan
    RECOMMENDATION = "recommendation"  # Recommendation
    ANALYSIS = "analysis"          # Detailed analysis


@dataclass
class ReasoningRequest:
    """Request for reasoning operations"""
    query: str
    reasoning_type: ReasoningType
    memory_snapshot: List[Dict[str, Any]]
    context: Dict[str, Any]
    output_format: ReasoningOutput = ReasoningOutput.TEXT
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    constraints: Optional[List[str]] = None


@dataclass
class ReasoningResponse:
    """Response from reasoning operations"""
    result: str
    confidence: float
    reasoning_type: ReasoningType
    output_format: ReasoningOutput
    metadata: Dict[str, Any]
    execution_time: float
    tokens_used: int
    timestamp: datetime


class ReasoningEngine:
    """
    Reasoning Engine
    
    Provides reasoning capabilities using LLM:
    - Analyzes memory patterns
    - Explains decisions
    - Makes predictions
    - Creates plans
    - Synthesizes information
    
    Important: This engine does NOT modify memory - it only reads from it.
    """
    
    def __init__(self):
        self.settings = get_settings()
        
        # LLM client (placeholder - would be initialized with actual API)
        self.llm_client = None
        self.embedding_model = None
        
        # Reasoning templates
        self.reasoning_templates = self._initialize_templates()
        
        # Performance tracking
        self.stats = {
            "total_reasoning_requests": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_execution_time": 0,
            "total_tokens_used": 0,
            "reasoning_type_counts": {}
        }
        
        # Cache for similar queries
        self.query_cache: Dict[str, ReasoningResponse] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    async def initialize(self):
        """Initialize the reasoning engine"""
        logger.info("🧠 Initializing reasoning engine...")
        
        try:
            # Initialize LLM client (placeholder)
            # In a real implementation, this would connect to OpenAI, Anthropic, etc.
            await self._initialize_llm_client()
            
            # Initialize embedding model
            await self._initialize_embedding_model()
            
            logger.info("✅ Reasoning engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize reasoning engine: {e}")
            raise
    
    async def reason(
        self, 
        active_memories: List, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform reasoning with active memories and context
        
        Args:
            active_memories: Currently active memories
            context: Current context
            
        Returns:
            Reasoning result with analysis and insights
        """
        try:
            self.stats["total_reasoning_requests"] += 1
            
            start_time = datetime.now()
            
            # Determine reasoning type from context
            reasoning_type = self._determine_reasoning_type(context)
            
            # Create memory snapshot
            memory_snapshot = self._create_memory_snapshot(active_memories)
            
            # Create reasoning request
            request = ReasoningRequest(
                query=context.get("query", "Analyze the current situation"),
                reasoning_type=reasoning_type,
                memory_snapshot=memory_snapshot,
                context=context,
                output_format=ReasoningOutput.TEXT
            )
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.query_cache:
                cached_response = self.query_cache[cache_key]
                if self._is_cache_valid(cached_response):
                    logger.debug("Returning cached reasoning result")
                    return self._format_cached_response(cached_response)
            
            # Perform reasoning
            response = await self._perform_reasoning(request)
            
            # Cache the result
            self.query_cache[cache_key] = response
            
            # Clean old cache entries
            self._clean_cache()
            
            # Update statistics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(response, execution_time)
            
            logger.debug(f"Reasoning completed in {execution_time:.2f}s")
            
            return self._format_response(response)
            
        except Exception as e:
            logger.error(f"Error in reasoning: {e}")
            self.stats["failed_responses"] += 1
            raise
    
    async def explain(
        self, 
        decision: str, 
        active_memories: List, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide explanation for a decision using memories
        
        Args:
            decision: Decision to explain
            active_memories: Memories that influenced the decision
            context: Context of the decision
            
        Returns:
            Explanation with supporting evidence
        """
        try:
            request = ReasoningRequest(
                query=f"Explain why the decision '{decision}' was made",
                reasoning_type=ReasoningType.EXPLANATION,
                memory_snapshot=self._create_memory_snapshot(active_memories),
                context={**context, "decision": decision},
                output_format=ReasoningOutput.TEXT
            )
            
            response = await self._perform_reasoning(request)
            
            return {
                "explanation": response.result,
                "confidence": response.confidence,
                "supporting_memories": [
                    {
                        "id": memory.id,
                        "pattern": memory.pattern_signature,
                        "strength": memory.strength,
                        "relevance": memory.__dict__.get("relevance_score", 0)
                    }
                    for memory in active_memories
                ],
                "reasoning_metadata": response.metadata
            }
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            raise
    
    async def predict(
        self, 
        current_situation: Dict[str, Any], 
        active_memories: List, 
        time_horizon: str = "near_term"
    ) -> Dict[str, Any]:
        """
        Make predictions based on current situation and memories
        
        Args:
            current_situation: Current situation description
            active_memories: Relevant memories
            time_horizon: Prediction time horizon
            
        Returns:
            Prediction with confidence and reasoning
        """
        try:
            request = ReasoningRequest(
                query=f"Predict what might happen next in this situation: {current_situation}",
                reasoning_type=ReasoningType.PREDICTION,
                memory_snapshot=self._create_memory_snapshot(active_memories),
                context={
                    "situation": current_situation,
                    "time_horizon": time_horizon
                },
                output_format=ReasoningOutput.JSON
            )
            
            response = await self._perform_reasoning(request)
            
            # Parse prediction JSON if needed
            try:
                prediction_data = json.loads(response.result)
            except json.JSONDecodeError:
                prediction_data = {"prediction": response.result}
            
            return {
                "prediction": prediction_data,
                "confidence": response.confidence,
                "time_horizon": time_horizon,
                "based_on_memories": len(active_memories),
                "reasoning_trace": response.metadata
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    async def create_plan(
        self, 
        goal: str, 
        active_memories: List, 
        constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an action plan using relevant memories
        
        Args:
            goal: Goal to achieve
            active_memories: Relevant memories for planning
            constraints: Planning constraints
            
        Returns:
            Action plan with steps and rationale
        """
        try:
            request = ReasoningRequest(
                query=f"Create a plan to achieve the goal: {goal}",
                reasoning_type=ReasoningType.PLANNING,
                memory_snapshot=self._create_memory_snapshot(active_memories),
                context={"goal": goal, "constraints": constraints or []},
                output_format=ReasoningOutput.PLAN
            )
            
            response = await self._perform_reasoning(request)
            
            return {
                "plan": response.result,
                "confidence": response.confidence,
                "goal": goal,
                "constraints": constraints,
                "based_on_experience": len(active_memories),
                "plan_metadata": response.metadata
            }
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            raise
    
    def _determine_reasoning_type(self, context: Dict[str, Any]) -> ReasoningType:
        """Determine reasoning type from context"""
        
        query = context.get("query", "").lower()
        
        if "explain" in query or "why" in query:
            return ReasoningType.EXPLANATION
        elif "predict" in query or "future" in query or "what if" in query:
            return ReasoningType.PREDICTION
        elif "plan" in query or "strategy" in query or "how to" in query:
            return ReasoningType.PLANNING
        elif "compare" in query or "versus" in query or "difference" in query:
            return ReasoningType.COMPARISON
        elif "analyze" in query or "examine" in query:
            return ReasoningType.ANALYSIS
        elif "evaluate" in query or "assess" in query:
            return ReasoningType.EVALUATION
        elif "debug" in query or "problem" in query or "issue" in query:
            return ReasoningType.DEBUGGING
        else:
            return ReasoningType.ANALYSIS
    
    def _create_memory_snapshot(self, active_memories: List) -> List[Dict[str, Any]]:
        """Create a snapshot of active memories for reasoning"""
        
        snapshot = []
        for memory in active_memories:
            snapshot.append({
                "id": memory.id,
                "pattern_signature": memory.pattern_signature,
                "memory_type": memory.memory_type.value if hasattr(memory, 'memory_type') else "unknown",
                "content": memory.content if hasattr(memory, 'content') else {},
                "context": memory.context if hasattr(memory, 'context') else {},
                "strength": memory.strength,
                "confidence": memory.confidence,
                "relevance_score": memory.__dict__.get("relevance_score", 0),
                "tags": memory.tags if hasattr(memory, 'tags') else []
            })
        
        return snapshot
    
    async def _perform_reasoning(self, request: ReasoningRequest) -> ReasoningResponse:
        """Perform the actual reasoning operation"""
        
        try:
            # Build prompt based on reasoning type
            prompt = self._build_reasoning_prompt(request)
            
            # Call LLM (placeholder - would be actual API call)
            response_text = await self._call_llm(prompt, request)
            
            # Extract confidence from response
            confidence = self._extract_confidence(response_text)
            
            # Parse metadata
            metadata = self._extract_metadata(response_text, request)
            
            return ReasoningResponse(
                result=response_text,
                confidence=confidence,
                reasoning_type=request.reasoning_type,
                output_format=request.output_format,
                metadata=metadata,
                execution_time=0.0,  # Would be measured in real implementation
                tokens_used=len(response_text.split()),  # Simplified token count
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in reasoning operation: {e}")
            raise
    
    def _build_reasoning_prompt(self, request: ReasoningRequest) -> str:
        """Build prompt for reasoning based on type and context"""
        
        template = self.reasoning_templates.get(
            request.reasoning_type, 
            self.reasoning_templates[ReasoningType.ANALYSIS]
        )
        
        # Create memory context string
        memory_context = self._format_memory_context(request.memory_snapshot)
        
        # Fill in the template
        prompt = template.format(
            query=request.query,
            memory_context=memory_context,
            context_info=json.dumps(request.context, indent=2),
            constraints="\n".join(request.constraints) if request.constraints else "None"
        )
        
        return prompt
    
    def _format_memory_context(self, memory_snapshot: List[Dict[str, Any]]) -> str:
        """Format memory snapshot for inclusion in prompt"""
        
        if not memory_snapshot:
            return "No relevant memories available."
        
        context_lines = ["Relevant memories and experiences:"]
        
        for i, memory in enumerate(memory_snapshot[:10]):  # Limit to top 10 memories
            context_lines.append(f"{i+1}. Pattern: {memory['pattern_signature']}")
            context_lines.append(f"   Strength: {memory['strength']:.2f}")
            context_lines.append(f"   Type: {memory['memory_type']}")
            
            if memory.get('content'):
                content_summary = str(memory['content'])[:200]  # Truncate long content
                context_lines.append(f"   Content: {content_summary}...")
            
            if memory.get('relevance_score', 0) > 0:
                context_lines.append(f"   Relevance: {memory['relevance_score']:.2f}")
            
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    async def _call_llm(self, prompt: str, request: ReasoningRequest) -> str:
        """Call LLM API (placeholder implementation)"""
        
        # This is a placeholder - in a real implementation, this would:
        # 1. Connect to OpenAI, Anthropic, or other LLM API
        # 2. Send the prompt with appropriate parameters
        # 3. Handle rate limiting, retries, etc.
        # 4. Return the response
        
        try:
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # For demonstration, return a simple response based on reasoning type
            if request.reasoning_type == ReasoningType.EXPLANATION:
                return f"Based on the available memories and context, here's my analysis: {request.query}"
            elif request.reasoning_type == ReasoningType.PREDICTION:
                return f"Given the current situation and past experiences, I predict that {request.query} is likely to occur with moderate confidence."
            elif request.reasoning_type == ReasoningType.PLANNING:
                return f"To achieve the goal '{request.query}', I recommend the following steps based on similar past situations..."
            else:
                return f"Analysis of '{request.query}' based on {len(request.memory_snapshot)} relevant memories and contextual information."
                
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise
    
    def _extract_confidence(self, response_text: str) -> float:
        """Extract confidence score from response"""
        
        # Simple heuristic - look for confidence indicators
        response_lower = response_text.lower()
        
        if "high confidence" in response_lower or "very confident" in response_lower:
            return 0.9
        elif "confident" in response_lower or "likely" in response_lower:
            return 0.7
        elif "moderate confidence" in response_lower or "possible" in response_lower:
            return 0.5
        elif "low confidence" in response_lower or "uncertain" in response_lower:
            return 0.3
        else:
            return 0.6  # Default moderate confidence
    
    def _extract_metadata(self, response_text: str, request: ReasoningRequest) -> Dict[str, Any]:
        """Extract metadata from the response"""
        
        return {
            "reasoning_method": "llm_analysis",
            "memories_used": len(request.memory_snapshot),
            "context_keys": list(request.context.keys()),
            "response_length": len(response_text),
            "reasoning_type": request.reasoning_type.value
        }
    
    def _generate_cache_key(self, request: ReasoningRequest) -> str:
        """Generate cache key for request"""
        
        # Simple hash based on key components
        key_components = [
            request.query,
            request.reasoning_type.value,
            str(sorted(request.memory_snapshot, key=lambda x: x.get('id', ''))),
            str(sorted(request.context.items()))
        ]
        
        return str(hash("|".join(key_components)))
    
    def _is_cache_valid(self, cached_response: ReasoningResponse) -> bool:
        """Check if cached response is still valid"""
        
        age = (datetime.now() - cached_response.timestamp).total_seconds()
        return age < self.cache_ttl
    
    def _format_cached_response(self, cached_response: ReasoningResponse) -> Dict[str, Any]:
        """Format cached response for output"""
        
        return {
            "result": cached_response.result,
            "confidence": cached_response.confidence,
            "reasoning_type": cached_response.reasoning_type.value,
            "cached": True,
            "timestamp": cached_response.timestamp.isoformat(),
            "metadata": cached_response.metadata
        }
    
    def _format_response(self, response: ReasoningResponse) -> Dict[str, Any]:
        """Format reasoning response for output"""
        
        return {
            "result": response.result,
            "confidence": response.confidence,
            "reasoning_type": response.reasoning_type.value,
            "output_format": response.output_format.value,
            "execution_time": response.execution_time,
            "tokens_used": response.tokens_used,
            "timestamp": response.timestamp.isoformat(),
            "metadata": response.metadata
        }
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        
        current_time = datetime.now()
        expired_keys = []
        
        for key, response in self.query_cache.items():
            age = (current_time - response.timestamp).total_seconds()
            if age > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.query_cache[key]
        
        # Limit cache size
        if len(self.query_cache) > 100:
            # Remove oldest entries
            sorted_items = sorted(
                self.query_cache.items(),
                key=lambda x: x[1].timestamp
            )
            
            for key, _ in sorted_items[:20]:  # Remove oldest 20
                del self.query_cache[key]
    
    def _update_stats(self, response: ReasoningResponse, execution_time: float):
        """Update reasoning statistics"""
        
        self.stats["successful_responses"] += 1
        
        # Update average execution time
        total_requests = self.stats["total_reasoning_requests"]
        current_avg = self.stats["average_execution_time"]
        self.stats["average_execution_time"] = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )
        
        # Update token usage
        self.stats["total_tokens_used"] += response.tokens_used
        
        # Update reasoning type counts
        reasoning_type = response.reasoning_type.value
        self.stats["reasoning_type_counts"][reasoning_type] = (
            self.stats["reasoning_type_counts"].get(reasoning_type, 0) + 1
        )
    
    def _initialize_templates(self) -> Dict[ReasoningType, str]:
        """Initialize reasoning prompt templates"""
        
        return {
            ReasoningType.ANALYSIS: """
            Analyze the following query using the provided memories and context:
            
            Query: {query}
            
            {memory_context}
            
            Context: {context_info}
            
            Please provide a thorough analysis considering the patterns and experiences stored in memory.
            """,
            
            ReasoningType.EXPLANATION: """
            Explain the reasoning behind this decision or outcome:
            
            {query}
            
            Use the following memories and context to provide a detailed explanation:
            
            {memory_context}
            
            Context: {context_info}
            
            Please explain why this decision/outcome occurred based on past experiences and current context.
            """,
            
            ReasoningType.PREDICTION: """
            Make a prediction based on the current situation and past experiences:
            
            {query}
            
            Relevant memories and experiences:
            {memory_context}
            
            Current context: {context_info}
            
            Consider constraints: {constraints}
            
            Provide a prediction with reasoning based on similar past situations.
            """,
            
            ReasoningType.PLANNING: """
            Create an action plan to achieve the following goal:
            
            Goal: {query}
            
            Past experiences and relevant memories:
            {memory_context}
            
            Current context: {context_info}
            
            Constraints: {constraints}
            
            Develop a step-by-step plan based on what has worked in similar situations before.
            """,
            
            ReasoningType.COMPARISON: """
            Compare the following options or alternatives:
            
            {query}
            
            Use past experiences and memories:
            {memory_context}
            
            Context: {context_info}
            
            Provide a comparison with pros and cons based on similar past decisions.
            """,
            
            ReasoningType.EVALUATION: """
            Evaluate the following based on past experiences:
            
            {query}
            
            Relevant memories and experiences:
            {memory_context}
            
            Context: {context_info}
            
            Provide an evaluation with reasoning based on what you've learned from similar situations.
            """,
            
            ReasoningType.DEBUGGING: """
            Help debug or solve this problem:
            
            {query}
            
            Use relevant memories of past problems and solutions:
            {memory_context}
            
            Current context: {context_info}
            
            Identify potential causes and solutions based on similar past issues.
            """
        }
    
    async def _initialize_llm_client(self):
        """Initialize LLM client"""
        # Placeholder for LLM client initialization
        # In real implementation, this would set up OpenAI, Anthropic, etc.
        pass
    
    async def _initialize_embedding_model(self):
        """Initialize embedding model for semantic search"""
        # Placeholder for embedding model initialization
        pass
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get reasoning engine statistics"""
        
        success_rate = (
            self.stats["successful_responses"] / max(1, self.stats["total_reasoning_requests"])
        ) * 100
        
        return {
            **self.stats,
            "success_rate_percent": success_rate,
            "cache_size": len(self.query_cache),
            "average_tokens_per_request": (
                self.stats["total_tokens_used"] / max(1, self.stats["total_reasoning_requests"])
            ),
            "most_used_reasoning_types": dict(
                sorted(self.stats["reasoning_type_counts"].items(), 
                      key=lambda x: x[1], reverse=True)[:5]
            )
        }