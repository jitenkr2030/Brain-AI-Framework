"""
Brain AI Framework Client for LMS Backend
Handles all communications with the Brain AI framework services
"""

import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# ============ Pydantic Models ============

class ContentType(str, Enum):
    VIDEO_LECTURE = "video_lecture"
    TEXT_MODULE = "text_module"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    DISCUSSION = "discussion"
    COURSE = "course"


class SearchResult(BaseModel):
    result_id: str
    type: ContentType
    title: str
    snippet: str
    relevance_score: float = Field(ge=0, le=1)
    course: Optional[str] = None
    module: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None


class CourseRecommendation(BaseModel):
    course_id: str
    title: str
    instructor: str
    category: Optional[str] = None
    duration: Optional[str] = None
    rating: Optional[float] = None
    match_score: int = Field(ge=0, le=100)
    reasoning: Optional[str] = None
    prerequisites: List[str] = []
    skills_gained: List[str] = []


class RecommendationFilter(BaseModel):
    categories: Optional[List[str]] = None
    difficulty: Optional[str] = None
    duration_max: Optional[str] = None
    rating_min: Optional[float] = None
    instructor_id: Optional[str] = None


class LearningPathModule(BaseModel):
    module_id: str
    title: str
    description: str
    duration: str
    rationale: str
    order: int
    status: Optional[str] = None
    prerequisites: List[str] = []


class LearningPath(BaseModel):
    path_id: str
    user_id: str
    target_goal: str
    modules: List[LearningPathModule]
    total_modules: int
    estimated_duration: str
    created_at: datetime
    updated_at: datetime


class TutorMessage(BaseModel):
    id: str
    role: str  # 'user' | 'assistant'
    content: str
    timestamp: datetime


class TutorResponse(BaseModel):
    response: str
    conversation_id: str
    suggested_topics: List[str] = []
    related_resources: List[Dict[str, str]] = []


class SkillAssessment(BaseModel):
    assessment_id: str
    user_id: str
    skills: Dict[str, float]  # skill_name -> proficiency_level (0-1)
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    assessed_at: datetime


class PredictiveAnalytics(BaseModel):
    user_id: str
    predicted_completion_date: Optional[datetime] = None
    course_success_probability: float = Field(ge=0, le=1)
    risk_level: str  # 'low' | 'medium' | 'high'
    recommended_interventions: List[str] = []
    engagement_trend: str  # 'increasing' | 'stable' | 'declining'
    predicted_difficulty: str  # 'easy' | 'moderate' | 'challenging'
    personalized_tips: List[str] = []


# ============ Brain AI Client ============

class BrainAIClient:
    """
    Client for interacting with the Brain AI Framework services.
    Provides methods for recommendations, search, tutoring, and analytics.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def close(self):
        """Close the async client."""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # ============ Search Methods ============

    async def smart_search(
        self,
        query: str,
        user_id: Optional[str] = None,
        user_context: Optional[Dict[str, str]] = None,
        scope: str = "all",
        limit: int = 10,
    ) -> List[SearchResult]:
        """
        Perform AI-powered semantic search across courses and content.

        Args:
            query: Natural language search query
            user_id: Optional user ID for personalized results
            user_context: Current user context (e.g., current course)
            scope: Search scope ('all', 'courses', 'content', 'discussions')
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects ranked by relevance
        """
        payload = {
            "query": query,
            "user_id": user_id,
            "user_context": user_context or {},
            "scope": scope,
            "limit": limit,
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/search",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return [SearchResult(**result) for result in data.get("results", [])]

    async def get_search_suggestions(
        self,
        query: str,
        limit: int = 5,
    ) -> List[str]:
        """Get AI-powered search suggestions based on partial query."""
        payload = {"query": query, "limit": limit}

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/search/suggestions",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return data.get("suggestions", [])

    # ============ Recommendation Methods ============

    async def get_course_recommendations(
        self,
        user_id: str,
        limit: int = 5,
        filters: Optional[RecommendationFilter] = None,
    ) -> List[CourseRecommendation]:
        """
        Get personalized course recommendations for a user.

        Args:
            user_id: The user ID to get recommendations for
            limit: Maximum number of recommendations
            filters: Optional filters to apply

        Returns:
            List of CourseRecommendation objects sorted by match score
        """
        params = {"user_id": user_id, "limit": limit}
        if filters:
            params.update(filters.model_dump(exclude_none=True))

        async with self.client.get(
            f"{self.base_url}/api/v1/brain-ai/recommendations",
            params=params,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return [
                CourseRecommendation(**rec) for rec in data.get("recommendations", [])
            ]

    async def get_skill_based_recommendations(
        self,
        user_id: str,
        current_skills: Dict[str, float],
        target_skills: List[str],
        limit: int = 5,
    ) -> List[CourseRecommendation]:
        """Get course recommendations based on skill gaps."""
        payload = {
            "user_id": user_id,
            "current_skills": current_skills,
            "target_skills": target_skills,
            "limit": limit,
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/recommendations/skill-based",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return [
                CourseRecommendation(**rec) for rec in data.get("recommendations", [])
            ]

    async def record_recommendation_interaction(
        self,
        user_id: str,
        course_id: str,
        interaction_type: str,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Record user interaction with a recommendation for improved future suggestions.

        Args:
            user_id: The user ID
            course_id: The recommended course ID
            interaction_type: Type of interaction ('viewed', 'clicked', 'enrolled', 'dismissed')
            timestamp: Optional interaction timestamp

        Returns:
            True if recording was successful
        """
        payload = {
            "user_id": user_id,
            "course_id": course_id,
            "interaction_type": interaction_type,
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/recommendations/interact",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            return True

    # ============ Learning Path Methods ============

    async def generate_learning_path(
        self,
        user_id: str,
        target_goal: str,
        current_skills: Optional[Dict[str, float]] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> LearningPath:
        """
        Generate a personalized learning path for achieving a target goal.

        Args:
            user_id: The user ID
            target_goal: The learning goal (e.g., 'Become a Data Scientist')
            current_skills: User's current skill levels
            preferences: Additional preferences (time commitment, preferred format, etc.)

        Returns:
            LearningPath object with ordered modules
        """
        payload = {
            "user_id": user_id,
            "target_goal": target_goal,
            "current_skills": current_skills or {},
            "preferences": preferences or {},
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/learning-path",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return LearningPath(**data)

    async def update_learning_path(
        self,
        path_id: str,
        completed_modules: List[str],
        progress_data: Dict[str, Any],
    ) -> LearningPath:
        """
        Update an existing learning path based on user progress.

        Args:
            path_id: The learning path ID
            completed_modules: List of completed module IDs
            progress_data: Additional progress metrics

        Returns:
            Updated LearningPath object
        """
        payload = {
            "path_id": path_id,
            "completed_modules": completed_modules,
            "progress_data": progress_data,
        }

        async with self.client.put(
            f"{self.base_url}/api/v1/brain-ai/learning-path",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return LearningPath(**data)

    async def get_learning_path_status(
        self,
        path_id: str,
    ) -> Dict[str, Any]:
        """Get the current status of a learning path."""
        async with self.client.get(
            f"{self.base_url}/api/v1/brain-ai/learning-path/{path_id}/status",
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            return response.json()

    # ============ AI Tutor Methods ============

    async def get_tutor_response(
        self,
        user_id: str,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        current_content: Optional[str] = None,
        current_course: Optional[str] = None,
        current_module: Optional[str] = None,
    ) -> TutorResponse:
        """
        Get a response from the AI tutor.

        Args:
            user_id: The user ID
            question: The user's question
            conversation_history: Previous conversation messages
            current_content: Content the user is currently viewing
            current_course: Course the user is currently enrolled in
            current_module: Module the user is currently working on

        Returns:
            TutorResponse with the AI's answer and metadata
        """
        payload = {
            "user_id": user_id,
            "question": question,
            "conversation_history": conversation_history or [],
            "current_content": current_content or "",
            "current_course": current_course or "",
            "current_module": current_module or "",
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/tutor",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return TutorResponse(**data)

    async def start_tutor_conversation(
        self,
        user_id: str,
        initial_context: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Start a new tutor conversation and return the conversation ID.

        Args:
            user_id: The user ID
            initial_context: Initial context for the conversation

        Returns:
            The new conversation ID
        """
        payload = {
            "user_id": user_id,
            "initial_context": initial_context or {},
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/tutor/conversation",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return data["conversation_id"]

    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50,
    ) -> List[TutorMessage]:
        """Get the history of a tutor conversation."""
        async with self.client.get(
            f"{self.base_url}/api/v1/brain-ai/tutor/conversation/{conversation_id}",
            params={"limit": limit},
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return [TutorMessage(**msg) for msg in data.get("messages", [])]

    async def clear_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        """Clear the history of a tutor conversation."""
        async with self.client.delete(
            f"{self.base_url}/api/v1/brain-ai/tutor/conversation/{conversation_id}",
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            return True

    # ============ Analytics Methods ============

    async def get_predictive_analytics(
        self,
        user_id: str,
        course_id: Optional[str] = None,
    ) -> PredictiveAnalytics:
        """
        Get predictive analytics for a user's learning progress.

        Args:
            user_id: The user ID
            course_id: Optional specific course to analyze

        Returns:
            PredictiveAnalytics with predictions and recommendations
        """
        params = {"user_id": user_id}
        if course_id:
            params["course_id"] = course_id

        async with self.client.get(
            f"{self.base_url}/api/v1/brain-ai/analytics",
            params=params,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return PredictiveAnalytics(**data)

    async def record_engagement_metric(
        self,
        user_id: str,
        metric_type: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """
        Record an engagement metric for improved analytics.

        Args:
            user_id: The user ID
            metric_type: Type of metric ('time_spent', 'completion_rate', 'quiz_score', etc.)
            value: The metric value
            metadata: Additional metadata
            timestamp: Optional recording timestamp

        Returns:
            True if recording was successful
        """
        payload = {
            "user_id": user_id,
            "metric_type": metric_type,
            "value": value,
            "metadata": metadata or {},
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/analytics/engagement",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            return True

    # ============ Skill Assessment Methods ============

    async def assess_skills(
        self,
        user_id: str,
        assessment_results: Dict[str, float],
    ) -> SkillAssessment:
        """
        Assess a user's skills based on quiz or exercise results.

        Args:
            user_id: The user ID
            assessment_results: Dictionary of skill names to proficiency scores (0-1)

        Returns:
            SkillAssessment with strengths, weaknesses, and recommendations
        """
        payload = {
            "user_id": user_id,
            "assessment_results": assessment_results,
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/skills/assess",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return SkillAssessment(**data)

    async def get_skill_gap_analysis(
        self,
        user_id: str,
        target_role: str,
    ) -> Dict[str, Any]:
        """
        Get a skill gap analysis for a target role.

        Args:
            user_id: The user ID
            target_role: The target job role

        Returns:
            Dictionary with current skills, required skills, and gap analysis
        """
        async with self.client.get(
            f"{self.base_url}/api/v1/brain-ai/skills/gap-analysis",
            params={"user_id": user_id, "target_role": target_role},
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            return response.json()

    # ============ Content Enhancement Methods ============

    async def generate_content_summary(
        self,
        content: str,
        content_type: str,
        max_length: int = 200,
    ) -> str:
        """
        Generate an AI summary of content.

        Args:
            content: The original content
            content_type: Type of content ('video', 'text', 'document')
            max_length: Maximum summary length

        Returns:
            Generated summary text
        """
        payload = {
            "content": content,
            "content_type": content_type,
            "max_length": max_length,
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/content/summarize",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return data["summary"]

    async def extract_key_concepts(
        self,
        content: str,
        num_concepts: int = 5,
    ) -> List[Dict[str, str]]:
        """
        Extract key concepts from content.

        Args:
            content: The content to analyze
            num_concepts: Number of concepts to extract

        Returns:
            List of concept dictionaries with 'term' and 'definition'
        """
        payload = {"content": content, "num_concepts": num_concepts}

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/content/concepts",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return data.get("concepts", [])

    async def generate_quiz_questions(
        self,
        content: str,
        num_questions: int = 5,
        difficulty: str = "medium",
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions from content.

        Args:
            content: The content to generate questions from
            num_questions: Number of questions to generate
            difficulty: Question difficulty level

        Returns:
            List of question dictionaries
        """
        payload = {
            "content": content,
            "num_questions": num_questions,
            "difficulty": difficulty,
        }

        async with self.client.post(
            f"{self.base_url}/api/v1/brain-ai/content/quiz",
            json=payload,
            headers=self._get_headers(),
        ) as response:
            response.raise_for_status()
            data = response.json()
            return data.get("questions", [])


# ============ Sync Wrapper ============

class SyncBrainAIClient:
    """Synchronous wrapper for BrainAIClient for use in non-async contexts."""

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self._async_client = BrainAIClient(base_url, api_key, timeout)
        self._loop = None
        self._client = None

    def _get_client(self):
        """Get or create sync client wrapper."""
        if self._client is None:
            import asyncio
            self._loop = asyncio.new_event_loop()
            self._client = self._loop.run_until_complete(
                self._async_client.__aenter__()
            )
        return self._client

    def close(self):
        """Close the client."""
        if self._client:
            self._loop.run_until_complete(self._async_client.__aexit__(None, None, None))
            self._client = None
            self._loop = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def smart_search(self, *args, **kwargs):
        client = self._get_client()
        return self._loop.run_until_complete(client.smart_search(*args, **kwargs))

    def get_course_recommendations(self, *args, **kwargs):
        client = self._get_client()
        return self._loop.run_until_complete(
            client.get_course_recommendations(*args, **kwargs)
        )

    def generate_learning_path(self, *args, **kwargs):
        client = self._get_client()
        return self._loop.run_until_complete(
            client.generate_learning_path(*args, **kwargs)
        )

    def get_tutor_response(self, *args, **kwargs):
        client = self._get_client()
        return self._loop.run_until_complete(
            client.get_tutor_response(*args, **kwargs)
        )

    def get_predictive_analytics(self, *args, **kwargs):
        client = self._get_client()
        return self._loop.run_until_complete(
            client.get_predictive_analytics(*args, **kwargs)
        )

    def assess_skills(self, *args, **kwargs):
        client = self._get_client()
        return self._loop.run_until_complete(client.assess_skills(*args, **kwargs))


# ============ Dependency Injection ============

# Global client instance for use across the application
_brain_ai_client: Optional[BrainAIClient] = None


def get_brain_ai_client() -> BrainAIClient:
    """Get or create the global Brain AI client instance."""
    global _brain_ai_client
    if _brain_ai_client is None:
        _brain_ai_client = BrainAIClient(
            base_url="http://localhost:8001",
            api_key=None,
            timeout=30.0,
        )
    return _brain_ai_client


async def close_brain_ai_client():
    """Close the global Brain AI client."""
    global _brain_ai_client
    if _brain_ai_client:
        await _brain_ai_client.close()
        _brain_ai_client = None


def set_brain_ai_client(client: BrainAIClient):
    """Set a custom Brain AI client instance (for testing or configuration)."""
    global _brain_ai_client
    _brain_ai_client = client
