"""
Peer Review System
Enables community-driven learning through code reviews and collaborative feedback
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, asc
from enum import Enum
import json
import logging

from app.database import get_db
from app.models.user import User, UserRole
from app.models.lms_models import (
    Course, Module, Lesson, Progress, CourseEnrollment, CourseReview
)
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

class ReviewStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"

class ReviewPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ReviewType(Enum):
    CODE_REVIEW = "code_review"
    PROJECT_REVIEW = "project_review"
    ASSIGNMENT_REVIEW = "assignment_review"
    PORTFOLIO_REVIEW = "portfolio_review"

@dataclass
class CodeSubmission:
    """Represents a student's code submission for review"""
    submission_id: str
    user_id: int
    lesson_id: int
    course_id: int
    title: str
    description: str
    code: str
    language: str
    files: List[Dict[str, str]]  # filename -> content
    test_results: Optional[Dict[str, Any]] = None
    rubric_scores: Optional[Dict[str, int]] = None
    created_at: datetime = None
    status: ReviewStatus = ReviewStatus.PENDING

@dataclass
class ReviewRequest:
    """Represents a request for peer review"""
    request_id: str
    submission: CodeSubmission
    requested_by: int
    assigned_reviewers: List[int]
    priority: ReviewPriority
    review_type: ReviewType
    deadline: datetime
    requirements: List[str]  # Specific review requirements
    anonymous: bool = False
    created_at: datetime = None

@dataclass
class ReviewFeedback:
    """Represents review feedback from a peer"""
    feedback_id: str
    review_request_id: str
    reviewer_id: int
    overall_score: int  # 1-5
    detailed_feedback: Dict[str, Any]
    code_suggestions: List[Dict[str, str]]  # filename -> suggestions
    strengths: List[str]
    improvements: List[str]
    estimated_hours_spent: int
    is_anonymous: bool
    created_at: datetime = None

class PeerReviewService:
    """Service managing peer review system for collaborative learning"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService()
        self.active_reviews: Dict[str, ReviewRequest] = {}
        self.review_queue: List[ReviewRequest] = []
        
    async def submit_code_for_review(
        self,
        user_id: int,
        lesson_id: int,
        title: str,
        description: str,
        code: str,
        language: str,
        files: List[Dict[str, str]] = None,
        review_type: ReviewType = ReviewType.CODE_REVIEW,
        anonymous: bool = False
    ) -> Dict[str, Any]:
        """Submit code for peer review"""
        
        # Generate submission ID
        submission_id = str(uuid.uuid4())
        
        # Get course and lesson context
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise ValueError("Lesson not found")
        
        course_id = lesson.module.course_id
        
        # Create code submission
        submission = CodeSubmission(
            submission_id=submission_id,
            user_id=user_id,
            lesson_id=lesson_id,
            course_id=course_id,
            title=title,
            description=description,
            code=code,
            language=language,
            files=files or [],
            created_at=datetime.utcnow(),
            status=ReviewStatus.PENDING
        )
        
        # Validate submission
        validation_result = await self._validate_submission(submission)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"],
                "suggestions": validation_result["suggestions"]
            }
        
        # Create review request
        review_request = await self._create_review_request(
            submission, user_id, review_type, anonymous
        )
        
        # Store in database (this would be implemented with proper models)
        await self._store_submission(submission)
        await self._store_review_request(review_request)
        
        # Auto-assign reviewers based on availability and expertise
        assigned_reviewers = await self._auto_assign_reviewers(review_request)
        
        # Notify reviewers
        await self._notify_reviewers(assigned_reviewers, review_request)
        
        # Track analytics
        await self._track_submission_event(user_id, submission_id, "submission_created")
        
        return {
            "success": True,
            "submission_id": submission_id,
            "review_request_id": review_request.request_id,
            "assigned_reviewers": assigned_reviewers,
            "estimated_review_time": self._estimate_review_time(review_type),
            "deadline": review_request.deadline.isoformat()
        }
    
    async def _validate_submission(self, submission: CodeSubmission) -> Dict[str, Any]:
        """Validate code submission before review"""
        
        validation_result = {
            "valid": True,
            "error": None,
            "suggestions": []
        }
        
        # Check code completeness
        if not submission.code.strip():
            validation_result["valid"] = False
            validation_result["error"] = "Code cannot be empty"
            return validation_result
        
        # Check code quality (basic checks)
        code_lines = submission.code.split('\n')
        if len(code_lines) < 5:
            validation_result["suggestions"].append(
                "Consider adding more code for better review feedback"
            )
        
        # Check for common issues
        if submission.language.lower() == "python":
            if "import" not in submission.code and len(code_lines) > 10:
                validation_result["suggestions"].append(
                    "Consider adding proper imports for better code structure"
                )
        
        # Check file structure
        if not submission.files and submission.language.lower() in ["python", "javascript"]:
            validation_result["suggestions"].append(
                "Consider organizing code into separate files for better structure"
            )
        
        # Check for documentation
        if "#" not in submission.code and submission.language.lower() == "python":
            validation_result["suggestions"].append(
                "Consider adding comments to explain your code logic"
            )
        
        return validation_result
    
    async def _create_review_request(
        self,
        submission: CodeSubmission,
        user_id: int,
        review_type: ReviewType,
        anonymous: bool
    ) -> ReviewRequest:
        """Create review request for submission"""
        
        request_id = str(uuid.uuid4())
        
        # Determine priority based on submission complexity and user progress
        priority = await self._determine_review_priority(submission, user_id)
        
        # Set deadline based on priority and review type
        deadline = self._calculate_review_deadline(priority, review_type)
        
        # Generate review requirements
        requirements = self._generate_review_requirements(review_type, submission)
        
        return ReviewRequest(
            request_id=request_id,
            submission=submission,
            requested_by=user_id,
            assigned_reviewers=[],
            priority=priority,
            review_type=review_type,
            deadline=deadline,
            requirements=requirements,
            anonymous=anonymous,
            created_at=datetime.utcnow()
        )
    
    async def _determine_review_priority(self, submission: CodeSubmission, user_id: int) -> ReviewPriority:
        """Determine review priority based on various factors"""
        
        # Check user progress (higher progress = higher priority for better feedback)
        user_progress = self.db.query(func.avg(Progress.progress_percentage)).filter(
            Progress.user_id == user_id
        ).scalar() or 0
        
        # Check submission complexity
        code_complexity = self._analyze_code_complexity(submission.code)
        
        # Determine priority
        if user_progress > 80 and code_complexity > 0.7:
            return ReviewPriority.HIGH
        elif user_progress > 50 or code_complexity > 0.5:
            return ReviewPriority.MEDIUM
        else:
            return ReviewPriority.LOW
    
    def _analyze_code_complexity(self, code: str) -> float:
        """Analyze code complexity (simplified version)"""
        
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Factors affecting complexity
        complexity_factors = {
            "function_count": len([line for line in non_empty_lines if line.strip().startswith('def')]),
            "class_count": len([line for line in non_empty_lines if line.strip().startswith('class')]),
            "loop_count": len([line for line in non_empty_lines if any(keyword in line for keyword in ['for', 'while'])]),
            "conditional_count": len([line for line in non_empty_lines if any(keyword in line for keyword in ['if', 'elif', 'else'])]),
            "import_count": len([line for line in non_empty_lines if line.strip().startswith('import')]),
            "line_count": len(non_empty_lines)
        }
        
        # Calculate complexity score (0-1)
        complexity_score = min(1.0, (
            complexity_factors["function_count"] * 0.2 +
            complexity_factors["class_count"] * 0.3 +
            complexity_factors["loop_count"] * 0.15 +
            complexity_factors["conditional_count"] * 0.15 +
            complexity_factors["import_count"] * 0.1 +
            min(complexity_factors["line_count"] / 100, 0.3)
        ))
        
        return complexity_score
    
    def _calculate_review_deadline(self, priority: ReviewPriority, review_type: ReviewType) -> datetime:
        """Calculate review deadline based on priority and type"""
        
        base_hours = {
            ReviewPriority.LOW: 48,
            ReviewPriority.MEDIUM: 24,
            ReviewPriority.HIGH: 12,
            ReviewPriority.URGENT: 4
        }
        
        type_multiplier = {
            ReviewType.CODE_REVIEW: 1.0,
            ReviewType.ASSIGNMENT_REVIEW: 0.8,
            ReviewType.PROJECT_REVIEW: 1.5,
            ReviewType.PORTFOLIO_REVIEW: 2.0
        }
        
        hours = base_hours[priority] * type_multiplier[review_type]
        return datetime.utcnow() + timedelta(hours=hours)
    
    def _generate_review_requirements(self, review_type: ReviewType, submission: CodeSubmission) -> List[str]:
        """Generate specific review requirements based on type and submission"""
        
        base_requirements = [
            "Review code structure and organization",
            "Check for potential bugs or errors",
            "Evaluate code readability and documentation",
            "Assess learning objectives achievement"
        ]
        
        if review_type == ReviewType.CODE_REVIEW:
            base_requirements.extend([
                "Focus on coding best practices",
                "Review algorithmic efficiency",
                "Check for security vulnerabilities"
            ])
        elif review_type == ReviewType.PROJECT_REVIEW:
            base_requirements.extend([
                "Evaluate project architecture",
                "Assess feature completeness",
                "Review user experience considerations"
            ])
        elif review_type == ReviewType.ASSIGNMENT_REVIEW:
            base_requirements.extend([
                "Verify assignment requirements compliance",
                "Check for creative problem solving",
                "Assess documentation quality"
            ])
        
        # Language-specific requirements
        if submission.language.lower() == "python":
            base_requirements.append("Review PEP 8 compliance")
        elif submission.language.lower() == "javascript":
            base_requirements.append("Check for modern JavaScript best practices")
        
        return base_requirements
    
    async def _auto_assign_reviewers(self, review_request: ReviewRequest) -> List[int]:
        """Auto-assign reviewers based on expertise and availability"""
        
        # Get potential reviewers from same course
        course_id = review_request.submission.course_id
        
        potential_reviewers = self.db.query(User).join(CourseEnrollment).filter(
            and_(
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.status == "active",
                User.id != review_request.requested_by,
                User.role.in_([UserRole.STUDENT, UserRole.INSTRUCTOR])
            )
        ).all()
        
        # Score reviewers based on various factors
        reviewer_scores = []
        for reviewer in potential_reviewers:
            score = await self._calculate_reviewer_score(reviewer, review_request)
            reviewer_scores.append((reviewer.id, score))
        
        # Sort by score and assign top reviewers
        reviewer_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Determine number of reviewers needed
        num_reviewers = self._determine_reviewer_count(review_request)
        
        assigned_reviewers = [reviewer_id for reviewer_id, _ in reviewer_scores[:num_reviewers]]
        review_request.assigned_reviewers = assigned_reviewers
        
        return assigned_reviewers
    
    async def _calculate_reviewer_score(self, reviewer: User, review_request: ReviewRequest) -> float:
        """Calculate reviewer suitability score"""
        
        score = 0.0
        
        # Base score for being an active student
        if reviewer.role == UserRole.STUDENT:
            score += 1.0
        
        # Progress-based scoring (more experienced students get higher scores)
        user_progress = self.db.query(func.avg(Progress.progress_percentage)).filter(
            Progress.user_id == reviewer.id
        ).scalar() or 0
        
        score += user_progress / 100 * 2.0
        
        # Review experience (would track in ReviewerProfile model)
        # For now, assume all students can review
        score += 1.0
        
        # Language expertise (simplified)
        if review_request.submission.language.lower() == "python":
            # Could check if reviewer has completed Python-related lessons
            score += 0.5
        
        # Availability (check recent activity)
        recent_activity = self.db.query(func.count(Progress.id)).filter(
            and_(
                Progress.user_id == reviewer.id,
                Progress.last_accessed >= datetime.utcnow() - timedelta(days=7)
            )
        ).scalar() or 0
        
        if recent_activity > 0:
            score += 0.5
        
        return score
    
    def _determine_reviewer_count(self, review_request: ReviewRequest) -> int:
        """Determine number of reviewers needed"""
        
        base_count = {
            ReviewPriority.LOW: 1,
            ReviewPriority.MEDIUM: 2,
            ReviewPriority.HIGH: 3,
            ReviewPriority.URGENT: 2  # Fewer reviewers but faster turnaround
        }
        
        type_multiplier = {
            ReviewType.CODE_REVIEW: 1.0,
            ReviewType.ASSIGNMENT_REVIEW: 1.0,
            ReviewType.PROJECT_REVIEW: 1.5,
            ReviewType.PORTFOLIO_REVIEW: 2.0
        }
        
        return max(1, int(base_count[review_request.priority] * type_multiplier[review_request.review_type]))
    
    async def _notify_reviewers(self, reviewer_ids: List[int], review_request: ReviewRequest):
        """Notify assigned reviewers of new review requests"""
        
        for reviewer_id in reviewer_ids:
            # Create notification (this would integrate with notification system)
            logger.info(f"Notifying reviewer {reviewer_id} of review request {review_request.request_id}")
            
            # Track notification event
            await self.analytics_service.track_event(
                user_id=reviewer_id,
                event_type="review_request_assigned",
                event_data={
                    "review_request_id": review_request.request_id,
                    "submission_title": review_request.submission.title,
                    "deadline": review_request.deadline.isoformat(),
                    "priority": review_request.priority.value
                }
            )
    
    def _estimate_review_time(self, review_type: ReviewType) -> int:
        """Estimate review time in hours"""
        
        time_estimates = {
            ReviewType.CODE_REVIEW: 2,
            ReviewType.ASSIGNMENT_REVIEW: 1,
            ReviewType.PROJECT_REVIEW: 4,
            ReviewType.PORTFOLIO_REVIEW: 6
        }
        
        return time_estimates.get(review_type, 2)
    
    async def submit_review_feedback(
        self,
        review_request_id: str,
        reviewer_id: int,
        overall_score: int,
        detailed_feedback: Dict[str, Any],
        code_suggestions: List[Dict[str, str]] = None,
        strengths: List[str] = None,
        improvements: List[str] = None,
        estimated_hours_spent: int = 1,
        is_anonymous: bool = False
    ) -> Dict[str, Any]:
        """Submit review feedback"""
        
        feedback_id = str(uuid.uuid4())
        
        # Validate review request and reviewer
        review_request = await self._get_review_request(review_request_id)
        if not review_request:
            return {"success": False, "error": "Review request not found"}
        
        if reviewer_id not in review_request.assigned_reviewers:
            return {"success": False, "error": "You are not assigned to this review"}
        
        # Create feedback
        feedback = ReviewFeedback(
            feedback_id=feedback_id,
            review_request_id=review_request_id,
            reviewer_id=reviewer_id,
            overall_score=overall_score,
            detailed_feedback=detailed_feedback,
            code_suggestions=code_suggestions or [],
            strengths=strengths or [],
            improvements=improvements or [],
            estimated_hours_spent=estimated_hours_spent,
            is_anonymous=is_anonymous,
            created_at=datetime.utcnow()
        )
        
        # Store feedback
        await self._store_feedback(feedback)
        
        # Update review request status
        await self._update_review_status(review_request_id)
        
        # Notify submission author
        await self._notify_submission_author(review_request, feedback)
        
        # Track analytics
        await self.analytics_service.track_event(
            user_id=reviewer_id,
            event_type="review_feedback_submitted",
            event_data={
                "feedback_id": feedback_id,
                "review_request_id": review_request_id,
                "overall_score": overall_score,
                "estimated_hours_spent": estimated_hours_spent
            }
        )
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "status": "submitted"
        }
    
    async def get_submission_reviews(self, submission_id: str) -> Dict[str, Any]:
        """Get all reviews for a submission"""
        
        reviews = await self._get_submission_reviews(submission_id)
        
        if not reviews:
            return {
                "success": False,
                "error": "No reviews found for this submission"
            }
        
        # Calculate aggregate metrics
        total_reviews = len(reviews)
        average_score = sum(r.overall_score for r in reviews) / total_reviews if total_reviews > 0 else 0
        
        # Compile all feedback
        all_strengths = []
        all_improvements = []
        all_suggestions = []
        
        for review in reviews:
            all_strengths.extend(review.strengths)
            all_improvements.extend(review.improvements)
            for suggestion in review.code_suggestions:
                all_suggestions.extend(suggestion.get("suggestions", []))
        
        return {
            "success": True,
            "submission_id": submission_id,
            "total_reviews": total_reviews,
            "average_score": average_score,
            "reviews": [
                {
                    "feedback_id": review.feedback_id,
                    "reviewer_id": review.reviewer_id if not review.is_anonymous else "anonymous",
                    "overall_score": review.overall_score,
                    "strengths": review.strengths,
                    "improvements": review.improvements,
                    "code_suggestions": review.code_suggestions,
                    "created_at": review.created_at.isoformat(),
                    "estimated_hours_spent": review.estimated_hours_spent
                }
                for review in reviews
            ],
            "aggregate_feedback": {
                "common_strengths": list(set(all_strengths)),
                "common_improvements": list(set(all_improvements)),
                "code_suggestions": list(set(all_suggestions))
            }
        }
    
    async def get_reviewer_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get dashboard data for reviewers"""
        
        # Get pending reviews
        pending_reviews = await self._get_pending_reviews_for_reviewer(user_id)
        
        # Get review history
        completed_reviews = await self._get_completed_reviews_for_reviewer(user_id)
        
        # Calculate reviewer metrics
        total_reviews = len(completed_reviews)
        average_score_given = sum(r.overall_score for r in completed_reviews) / total_reviews if total_reviews > 0 else 0
        total_time_spent = sum(r.estimated_hours_spent for r in completed_reviews)
        
        # Calculate reviewer level (simplified)
        reviewer_level = self._calculate_reviewer_level(total_reviews, average_score_given)
        
        return {
            "success": True,
            "reviewer_metrics": {
                "total_reviews_completed": total_reviews,
                "average_score_given": average_score_given,
                "total_time_spent_hours": total_time_spent,
                "reviewer_level": reviewer_level,
                "pending_reviews": len(pending_reviews)
            },
            "pending_reviews": [
                {
                    "review_request_id": r.request_id,
                    "submission_title": r.submission.title,
                    "submission_author": "Anonymous" if r.anonymous else "Visible",
                    "priority": r.priority.value,
                    "deadline": r.deadline.isoformat(),
                    "estimated_time_hours": self._estimate_review_time(r.review_type)
                }
                for r in pending_reviews
            ],
            "recent_reviews": [
                {
                    "submission_title": r.submission.title,
                    "score_given": r.overall_score,
                    "completed_at": r.created_at.isoformat()
                }
                for r in completed_reviews[-5:]  # Last 5 reviews
            ]
        }
    
    def _calculate_reviewer_level(self, total_reviews: int, average_score: float) -> str:
        """Calculate reviewer level based on performance"""
        
        if total_reviews >= 50 and average_score >= 4.5:
            return "Expert Reviewer"
        elif total_reviews >= 20 and average_score >= 4.0:
            return "Senior Reviewer"
        elif total_reviews >= 10 and average_score >= 3.5:
            return "Experienced Reviewer"
        elif total_reviews >= 5:
            return "Reviewer"
        else:
            return "New Reviewer"
    
    # Database storage methods (would be implemented with proper models)
    async def _store_submission(self, submission: CodeSubmission):
        """Store code submission in database"""
        # Implementation would save to CodeSubmission model
        pass
    
    async def _store_review_request(self, review_request: ReviewRequest):
        """Store review request in database"""
        # Implementation would save to ReviewRequest model
        pass
    
    async def _store_feedback(self, feedback: ReviewFeedback):
        """Store review feedback in database"""
        # Implementation would save to ReviewFeedback model
        pass
    
    async def _get_review_request(self, request_id: str) -> Optional[ReviewRequest]:
        """Get review request by ID"""
        # Implementation would query ReviewRequest model
        return self.active_reviews.get(request_id)
    
    async def _get_submission_reviews(self, submission_id: str) -> List[ReviewFeedback]:
        """Get all reviews for a submission"""
        # Implementation would query ReviewFeedback model
        return []
    
    async def _get_pending_reviews_for_reviewer(self, user_id: int) -> List[ReviewRequest]:
        """Get pending reviews for a reviewer"""
        # Implementation would query database
        return []
    
    async def _get_completed_reviews_for_reviewer(self, user_id: int) -> List[ReviewFeedback]:
        """Get completed reviews for a reviewer"""
        # Implementation would query database
        return []
    
    async def _update_review_status(self, review_request_id: str):
        """Update review request status based on feedback"""
        # Implementation would check if all reviewers have submitted
        pass
    
    async def _notify_submission_author(self, review_request: ReviewRequest, feedback: ReviewFeedback):
        """Notify submission author of new feedback"""
        # Implementation would create notification
        pass
    
    async def _track_submission_event(self, user_id: int, submission_id: str, event_type: str):
        """Track submission-related events"""
        await self.analytics_service.track_event(
            user_id=user_id,
            event_type=event_type,
            event_data={
                "submission_id": submission_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )