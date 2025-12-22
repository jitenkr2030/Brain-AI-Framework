"""
Course Service for Brain AI LMS
Handles business logic for course management, enrollment, and progress tracking
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import json

from app.models.course import Course, CourseLevel, CourseCategory
from app.models.lms_models import (
    CourseEnrollment, EnrollmentStatus, Progress, Module, Lesson, 
    CourseReview, LearningPath, ForumPost, ForumComment
)
from app.models.user import User
from app.schemas.course_schemas import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse,
    CourseEnrollmentRequest, CourseEnrollmentResponse,
    CourseFilterParams, CourseReviewRequest, CourseReviewResponse,
    CourseProgressResponse, ProgressResponse, LearningPath,
    BrainAIExample, BrainAILabConfig, CertificateInfo,
    CourseStats, CourseRecommendation, CourseRecommendationsResponse
)

class CourseService:
    """Service class for course-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Course Management
    async def get_courses(self, skip: int = limit: int, filters: CourseFilterParams) -> Tuple[List[CourseResponse], int]:
        """Get courses with filtering and pagination"""
        query = self.db.query(Course)
        
        # Apply filters
        if filters.level:
            query = query.filter(Course.level == filters.level)
        if filters.category:
            query = query.filter(Course.category == filters.category)
        if filters.price_min is not None:
            query = query.filter(Course.price_usd >= filters.price_min)
        if filters.price_max is not None:
            query = query.filter(Course.price_usd <= filters.price_max)
        if filters.featured_only:
            query = query.filter(Course.is_featured == True)
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Course.title.ilike(search_term),
                    Course.description.ilike(search_term),
                    Course.short_description.ilike(search_term)
                )
            )
        
        # Only published courses for public access
        query = query.filter(Course.is_published == True)
        
        # Sorting
        sort_field = getattr(Course, filters.sort_by, Course.created_at)
        if filters.sort_order == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        courses = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        course_responses = [self._convert_course_to_response(course) for course in courses]
        
        return course_responses, total
    
    async def get_featured_courses(self, limit: int = 6) -> List[CourseResponse]:
        """Get featured courses for homepage"""
        courses = self.db.query(Course).filter(
            and_(
                Course.is_featured == True,
                Course.is_published == True
            )
        ).order_by(desc(Course.created_at)).limit(limit).all()
        
        return [self._convert_course_to_response(course) for course in courses]
    
    async def get_course_details(self, course: Course, include_content: bool = True, 
                                include_enrollment: bool = False, 
                                current_user: Optional[User] = None) -> CourseResponse:
        """Get detailed course information"""
        response = self._convert_course_to_response(course)
        
        if include_content:
            # Load modules and lessons
            modules = self.db.query(Module).filter(
                Module.course_id == course.id
            ).order_by(Module.order_index).all()
            
            module_responses = []
            for module in modules:
                lessons = self.db.query(Lesson).filter(
                    Lesson.module_id == module.id
                ).order_by(Lesson.order_index).all()
                
                lesson_responses = []
                for lesson in lessons:
                    lesson_data = {
                        "id": lesson.id,
                        "title": lesson.title,
                        "description": lesson.description,
                        "lesson_type": lesson.lesson_type,
                        "order_index": lesson.order_index,
                        "duration_minutes": lesson.duration_minutes,
                        "is_published": lesson.is_published,
                        "brain_ai_example_id": lesson.brain_ai_example_id,
                        "requires_brain_ai_setup": lesson.requires_brain_ai_setup
                    }
                    lesson_responses.append(lesson_data)
                
                module_data = {
                    "id": module.id,
                    "title": module.title,
                    "description": module.description,
                    "order_index": module.order_index,
                    "estimated_duration_minutes": module.estimated_duration_minutes,
                    "is_prerequisite": module.is_prerequisite,
                    "is_published": module.is_published,
                    "lessons": lesson_responses
                }
                module_responses.append(module_data)
            
            response.modules = module_responses
        
        if include_enrollment and current_user:
            enrollment = self.db.query(CourseEnrollment).filter(
                and_(
                    CourseEnrollment.user_id == current_user.id,
                    CourseEnrollment.course_id == course.id
                )
            ).first()
            
            if enrollment:
                enrollment_data = {
                    "id": enrollment.id,
                    "status": enrollment.status,
                    "enrolled_at": enrollment.enrolled_at,
                    "completed_at": enrollment.completed_at,
                    "progress_percentage": enrollment.progress_percentage
                }
                response.enrollment = enrollment_data
        
        return response
    
    async def create_course(self, course_data: CourseCreate, creator_id: int) -> CourseResponse:
        """Create a new course"""
        # Generate slug if not provided
        slug = course_data.slug or self._generate_slug(course_data.title)
        
        # Check if slug is unique
        existing_course = self.db.query(Course).filter(Course.slug == slug).first()
        if existing_course:
            raise ValueError("Course with this slug already exists")
        
        # Create course
        course = Course(
            title=course_data.title,
            slug=slug,
            description=course_data.description,
            short_description=course_data.short_description,
            level=course_data.level,
            category=course_data.category,
            duration_hours=course_data.duration_hours,
            difficulty_rating=course_data.difficulty_rating,
            price_usd=course_data.price_usd,
            currency=course_data.currency,
            learning_outcomes=course_data.learning_outcomes,
            prerequisites=course_data.prerequisites,
            syllabus=course_data.syllabus,
            thumbnail_url=course_data.thumbnail_url,
            preview_video_url=course_data.preview_video_url,
            has_interactive_labs=course_data.has_interactive_labs,
            has_certification=course_data.has_certification,
            has_live_sessions=course_data.has_live_sessions,
            has_community_access=course_data.has_community_access,
            creator_id=creator_id
        )
        
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        
        # Add additional instructors if provided
        if course_data.instructor_ids:
            instructors = self.db.query(User).filter(User.id.in_(course_data.instructor_ids)).all()
            course.instructors.extend(instructors)
            self.db.commit()
        
        return self._convert_course_to_response(course)
    
    async def update_course(self, course: Course, course_data: CourseUpdate) -> CourseResponse:
        """Update course information"""
        # Update fields
        update_data = course_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(course, field, value)
        
        course.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(course)
        
        return self._convert_course_to_response(course)
    
    # Enrollment Management
    async def enroll_course(self, user_id: int, course_id: int) -> CourseEnrollmentResponse:
        """Enroll user in a course"""
        # Check if already enrolled
        existing = self.db.query(CourseEnrollment).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            )
        ).first()
        
        if existing:
            raise ValueError("Already enrolled in this course")
        
        # Create enrollment
        enrollment = CourseEnrollment(
            user_id=user_id,
            course_id=course_id,
            status=EnrollmentStatus.ACTIVE
        )
        
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        
        # Update course enrollment count
        course = self.db.query(Course).filter(Course.id == course_id).first()
        course.enrollment_count += 1
        self.db.commit()
        
        return CourseEnrollmentResponse(
            id=enrollment.id,
            status=enrollment.status,
            enrolled_at=enrollment.enrolled_at,
            completed_at=enrollment.completed_at,
            progress_percentage=enrollment.progress_percentage,
            course=self._convert_course_to_response(course)
        )
    
    async def get_course_progress(self, user_id: int, course_id: int) -> CourseProgressResponse:
        """Get detailed progress for a course"""
        # Get all lessons in the course
        lessons_query = self.db.query(Lesson).join(Module).filter(
            Module.course_id == course_id,
            Lesson.is_published == True
        ).order_by(Module.order_index, Lesson.order_index)
        
        lessons = lessons_query.all()
        total_lessons = len(lessons)
        
        # Get progress records
        progress_records = self.db.query(Progress).filter(
            and_(
                Progress.user_id == user_id,
                Progress.course_id == course_id,
                Progress.lesson_id.in_([lesson.id for lesson in lessons])
            )
        ).all()
        
        # Create progress lookup
        progress_lookup = {pr.lesson_id: pr for pr in progress_records}
        
        # Calculate overall progress
        completed_lessons = sum(1 for pr in progress_records if pr.status == "completed")
        total_time_spent = sum(pr.time_spent_minutes for pr in progress_records)
        
        # Estimate time remaining
        remaining_lessons = total_lessons - completed_lessons
        avg_lesson_time = total_time_spent / max(completed_lessons, 1)
        estimated_remaining = int(remaining_lessons * avg_lesson_time)
        
        # Convert progress records to response format
        lesson_progress = []
        for lesson in lessons:
            progress = progress_lookup.get(lesson.id)
            if progress:
                lesson_progress.append(ProgressResponse(
                    lesson_id=lesson.id,
                    status=progress.status,
                    progress_percentage=progress.progress_percentage,
                    time_spent_minutes=progress.time_spent_minutes,
                    quiz_score=progress.quiz_score,
                    last_accessed=progress.last_accessed,
                    completion_date=progress.completion_date
                ))
        
        overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return CourseProgressResponse(
            course_id=course_id,
            overall_progress=overall_progress,
            completed_lessons=completed_lessons,
            total_lessons=total_lessons,
            total_time_spent_minutes=total_time_spent,
            estimated_time_remaining_minutes=estimated_remaining,
            lesson_progress=lesson_progress
        )
    
    async def update_lesson_progress(self, user_id: int, course_id: int, lesson_id: int,
                                   status: str, progress_percentage: float, 
                                   time_spent_minutes: int) -> ProgressResponse:
        """Update progress for a specific lesson"""
        # Get or create progress record
        progress = self.db.query(Progress).filter(
            and_(
                Progress.user_id == user_id,
                Progress.course_id == course_id,
                Progress.lesson_id == lesson_id
            )
        ).first()
        
        if not progress:
            progress = Progress(
                user_id=user_id,
                course_id=course_id,
                lesson_id=lesson_id,
                status=status,
                progress_percentage=progress_percentage,
                time_spent_minutes=time_spent_minutes
            )
            self.db.add(progress)
        else:
            progress.status = status
            progress.progress_percentage = progress_percentage
            progress.time_spent_minutes += time_spent_minutes
            progress.last_accessed = datetime.utcnow()
            
            if status == "completed" and not progress.completion_date:
                progress.completion_date = datetime.utcnow()
        
        # Update enrollment progress
        enrollment = self.db.query(CourseEnrollment).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.course_id == course_id
            )
        ).first()
        
        if enrollment:
            # Calculate overall progress
            total_lessons = self.db.query(Lesson).join(Module).filter(
                and_(
                    Module.course_id == course_id,
                    Lesson.is_published == True
                )
            ).count()
            
            completed_lessons = self.db.query(func.count(Progress.id)).filter(
                and_(
                    Progress.user_id == user_id,
                    Progress.course_id == course_id,
                    Progress.status == "completed"
                )
            ).scalar()
            
            enrollment.progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            # Mark as completed if 100%
            if enrollment.progress_percentage >= 100:
                enrollment.status = EnrollmentStatus.COMPLETED
                enrollment.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(progress)
        
        return ProgressResponse(
            lesson_id=progress.lesson_id,
            status=progress.status,
            progress_percentage=progress.progress_percentage,
            time_spent_minutes=progress.time_spent_minutes,
            quiz_score=progress.quiz_score,
            last_accessed=progress.last_accessed,
            completion_date=progress.completion_date
        )
    
    # Review Management
    async def create_review(self, user_id: int, course_id: int, review_data: CourseReviewRequest) -> CourseReviewResponse:
        """Create a course review"""
        # Check if already reviewed
        existing_review = self.db.query(CourseReview).filter(
            and_(
                CourseReview.user_id == user_id,
                CourseReview.course_id == course_id
            )
        ).first()
        
        if existing_review:
            raise ValueError("You have already reviewed this course")
        
        # Create review
        review = CourseReview(
            user_id=user_id,
            course_id=course_id,
            rating=review_data.rating,
            title=review_data.title,
            content=review_data.content,
            is_verified_purchase=True  # Assuming enrolled users are verified
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        
        # Update course rating
        await self._update_course_rating(course_id)
        
        return self._convert_review_to_response(review)
    
    async def get_course_reviews(self, course_id: int, skip: int = 0, limit: int = 20) -> Tuple[List[CourseReviewResponse], int]:
        """Get reviews for a course"""
        reviews_query = self.db.query(CourseReview).filter(
            CourseReview.course_id == course_id
        ).order_by(desc(CourseReview.created_at))
        
        total = reviews_query.count()
        reviews = reviews_query.offset(skip).limit(limit).all()
        
        return [self._convert_review_to_response(review) for review in reviews], total
    
    # User Course Management
    async def get_user_courses(self, user_id: int, status: Optional[EnrollmentStatus] = None) -> List[Dict[str, Any]]:
        """Get courses for a user"""
        query = self.db.query(CourseEnrollment).join(Course).filter(
            CourseEnrollment.user_id == user_id
        )
        
        if status:
            query = query.filter(CourseEnrollment.status == status)
        
        enrollments = query.order_by(desc(CourseEnrollment.enrolled_at)).all()
        
        result = []
        for enrollment in enrollments:
            # Get progress
            total_lessons = self.db.query(Lesson).join(Module).filter(
                Module.course_id == enrollment.course_id
            ).count()
            
            completed_lessons = self.db.query(func.count(Progress.id)).filter(
                and_(
                    Progress.user_id == user_id,
                    Progress.course_id == enrollment.course_id,
                    Progress.status == "completed"
                )
            ).scalar()
            
            course_data = {
                "id": enrollment.course.id,
                "title": enrollment.course.title,
                "slug": enrollment.course.slug,
                "thumbnail_url": enrollment.course.thumbnail_url,
                "level": enrollment.course.level,
                "category": enrollment.course.category,
                "enrollment": {
                    "id": enrollment.id,
                    "status": enrollment.status,
                    "enrolled_at": enrollment.enrolled_at,
                    "progress_percentage": enrollment.progress_percentage
                },
                "progress": {
                    "completed_lessons": completed_lessons or 0,
                    "total_lessons": total_lessons,
                    "completion_percentage": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
                }
            }
            result.append(course_data)
        
        return result
    
    # AI-Powered Features
    async def get_personalized_paths(self, user: User) -> List[LearningPath]:
        """Get personalized learning paths for user"""
        # This would implement AI-powered path generation based on:
        # - User's current skill level
        # - Learning preferences
        # - Completed courses
        # - Career goals
        # - Industry trends
        
        # For now, return predefined paths
        paths = self.db.query(LearningPath).filter(
            LearningPath.is_published == True
        ).all()
        
        # Filter paths based on user's experience level
        if user.experience_level == "beginner":
            paths = [p for p in paths if p.difficulty_level in ["beginner", "intermediate"]]
        elif user.experience_level == "intermediate":
            paths = [p for p in paths if p.difficulty_level in ["intermediate", "advanced"]]
        elif user.experience_level == "advanced":
            paths = [p for p in paths if p.difficulty_level in ["advanced", "expert"]]
        
        return [self._convert_learning_path_to_response(path) for path in paths]
    
    async def get_recommendations(self, user_id: int, limit: int = 6) -> List[CourseRecommendation]:
        """Get AI-powered course recommendations"""
        # Get user's enrolled courses and preferences
        user_enrollments = self.db.query(CourseEnrollment).filter(
            CourseEnrollment.user_id == user_id
        ).all()
        
        enrolled_course_ids = [e.course_id for e in user_enrollments]
        
        # Get courses not yet enrolled
        query = self.db.query(Course).filter(
            and_(
                Course.is_published == True,
                Course.id.notin_(enrolled_course_ids) if enrolled_course_ids else True
            )
        )
        
        courses = query.limit(limit * 3).all()  # Get more for filtering
        
        recommendations = []
        for course in courses:
            # Calculate relevance score based on:
            # - User's completed courses
            # - Course prerequisites
            # - Difficulty level match
            # - Category preferences
            
            relevance_score = self._calculate_relevance_score(user_id, course)
            
            if relevance_score > 0.3:  # Minimum threshold
                reason = self._generate_recommendation_reason(user_id, course)
                personalized_factors = self._get_personalized_factors(user_id, course)
                
                recommendations.append(CourseRecommendation(
                    course=self._convert_course_to_response(course),
                    relevance_score=relevance_score,
                    reason=reason,
                    personalized_factors=personalized_factors
                ))
        
        # Sort by relevance and return top results
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return recommendations[:limit]
    
    # Statistics
    async def get_user_stats(self, user_id: int) -> CourseStats:
        """Get user course statistics"""
        # Get enrollment stats
        total_enrollments = self.db.query(CourseEnrollment).filter(
            CourseEnrollment.user_id == user_id
        ).count()
        
        active_enrollments = self.db.query(CourseEnrollment).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            )
        ).count()
        
        completed_courses = self.db.query(CourseEnrollment).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.status == EnrollmentStatus.COMPLETED
            )
        ).count()
        
        # Get learning time
        total_time = self.db.query(func.sum(Progress.time_spent_minutes)).filter(
            Progress.user_id == user_id
        ).scalar() or 0
        
        # Calculate completion rate
        avg_completion_rate = self.db.query(func.avg(CourseEnrollment.progress_percentage)).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            )
        ).scalar() or 0
        
        # Calculate current streak (simplified)
        recent_progress = self.db.query(Progress).filter(
            and_(
                Progress.user_id == user_id,
                Progress.last_accessed >= datetime.utcnow() - timedelta(days=30)
            )
        ).count()
        
        current_streak_days = min(recent_progress, 30)  # Simplified streak calculation
        
        # Get certificates
        certificates = self.db.query(CourseEnrollment).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.status == EnrollmentStatus.COMPLETED,
                Course.has_certification == True
            )
        ).join(Course).count()
        
        # Get total spent
        total_spent = self.db.query(func.sum(Course.price_usd)).filter(
            and_(
                CourseEnrollment.user_id == user_id,
                CourseEnrollment.status == EnrollmentStatus.COMPLETED
            )
        ).join(Course).scalar() or 0
        
        return CourseStats(
            total_courses=total_enrollments,
            active_enrollments=active_enrollments,
            completed_courses=completed_courses,
            total_learning_time_minutes=total_time,
            average_completion_rate=avg_completion_rate,
            current_streak_days=current_streak_days,
            certificates_earned=certificates,
            total_spent=total_spent
        )
    
    # Brain AI Integration
    async def get_brain_ai_examples(self, course_id: Optional[int] = None, 
                                   lesson_id: Optional[int] = None,
                                   category: Optional[str] = None) -> List[BrainAIExample]:
        """Get Brain AI examples integrated with courses"""
        # This would integrate with the Brain AI framework examples
        # For now, return mock data
        
        examples = [
            BrainAIExample(
                id="example_001",
                name="Simple Memory System",
                description="Basic implementation of persistent memory using vectors",
                category="memory_systems",
                languages=["python", "javascript"],
                difficulty_level=CourseLevel.FOUNDATION,
                course_id=course_id,
                lesson_id=lesson_id,
                demo_url="https://examples.brainaiframework.com/memory-system",
                source_code_url="https://github.com/brain-ai/examples/tree/main/memory-system"
            ),
            BrainAIExample(
                id="example_002",
                name="Learning Engine",
                description="Implementation of incremental learning with feedback",
                category="learning_engines",
                languages=["python", "go", "rust"],
                difficulty_level=CourseLevel.INTERMEDIATE,
                course_id=course_id,
                lesson_id=lesson_id,
                demo_url="https://examples.brainaiframework.com/learning-engine",
                source_code_url="https://github.com/brain-ai/examples/tree/main/learning-engine"
            )
        ]
        
        # Filter by category if provided
        if category:
            examples = [ex for ex in examples if ex.category == category]
        
        return examples
    
    async def setup_brain_ai_lab(self, user_id: int, course_id: int, lesson_id: int) -> BrainAILabConfig:
        """Setup Brain AI lab environment for a lesson"""
        # This would integrate with Brain AI framework to set up a sandbox environment
        # For now, return mock configuration
        
        lab_id = f"lab_{user_id}_{course_id}_{lesson_id}_{uuid.uuid4().hex[:8]}"
        
        return BrainAILabConfig(
            lab_id=lab_id,
            environment_ready=True,
            dependencies=["brain-ai==1.0.0", "numpy>=1.21.0", "scikit-learn>=1.0.0"],
            setup_instructions=[
                "Install required dependencies",
                "Initialize Brain AI framework",
                "Load lesson-specific configuration",
                "Start interactive coding environment"
            ],
            example_code="""from brain_ai import MemorySystem, LearningEngine

# Initialize memory system
memory = MemorySystem()
learning = LearningEngine()

# Your code here...
""",
            interactive_url=f"https://labs.brainaiframework.com/{lab_id}"
        )
    
    async def verify_certificate(self, certificate_id: str) -> CertificateInfo:
        """Verify course certificate"""
        # This would verify certificates issued by the platform
        # For now, return mock data
        
        return CertificateInfo(
            certificate_id=certificate_id,
            course_title="Brain AI Fundamentals",
            student_name="John Doe",
            completion_date=datetime.utcnow(),
            instructor_name="Brain AI Expert",
            certificate_url=f"https://certificates.brainaiframework.com/{certificate_id}",
            verification_url=f"https://verify.brainaiframework.com/{certificate_id}"
        )
    
    # Helper Methods
    def _convert_course_to_response(self, course: Course) -> CourseResponse:
        """Convert Course model to CourseResponse"""
        return CourseResponse(
            # Basic info
            id=course.id,
            title=course.title,
            slug=course.slug,
            description=course.description,
            short_description=course.short_description,
            level=course.level,
            category=course.category,
            duration_hours=course.duration_hours,
            difficulty_rating=course.difficulty_rating,
            price_usd=course.price_usd,
            currency=course.currency,
            thumbnail_url=course.thumbnail_url,
            preview_video_url=course.preview_video_url,
            learning_outcomes=course.learning_outcomes,
            prerequisites=course.prerequisites,
            syllabus=course.syllabus,
            has_interactive_labs=course.has_interactive_labs,
            has_certification=course.has_certification,
            has_live_sessions=course.has_live_sessions,
            has_community_access=course.has_community_access,
            is_published=course.is_published,
            is_featured=course.is_featured,
            is_enterprise_only=course.is_enterprise_only,
            enrollment_count=course.enrollment_count,
            completion_rate=course.completion_rate,
            average_rating=course.average_rating,
            review_count=course.review_count,
            created_at=course.created_at,
            updated_at=course.updated_at,
            # Relationships
            instructors=[
                InstructorInfo(
                    id=instructor.id,
                    full_name=instructor.full_name,
                    avatar_url=instructor.avatar_url,
                    bio=instructor.bio,
                    company=instructor.company,
                    job_title=instructor.job_title
                ) for instructor in course.instructors
            ],
            creator=InstructorInfo(
                id=course.creator.id,
                full_name=course.creator.full_name,
                avatar_url=course.creator.avatar_url,
                bio=course.creator.bio,
                company=course.creator.company,
                job_title=course.creator.job_title
            )
        )
    
    def _convert_review_to_response(self, review: CourseReview) -> CourseReviewResponse:
        """Convert CourseReview model to CourseReviewResponse"""
        return CourseReviewResponse(
            id=review.id,
            rating=review.rating,
            title=review.title,
            content=review.content,
            is_verified_purchase=review.is_verified_purchase,
            helpful_count=review.helpful_count,
            created_at=review.created_at,
            reviewer=ReviewerInfo(
                id=review.user.id,
                full_name=review.user.full_name,
                avatar_url=review.user.avatar_url,
                company=review.user.company,
                verified_purchase=review.is_verified_purchase
            )
        )
    
    def _convert_learning_path_to_response(self, path: LearningPath) -> LearningPath:
        """Convert LearningPath model to LearningPath response"""
        # This would convert the database model to response format
        # Implementation depends on the exact structure needed
        return LearningPath(
            id=path.id,
            title=path.title,
            description=path.description,
            difficulty_level=path.difficulty_level,
            target_audience=path.target_audience,
            estimated_duration_hours=path.estimated_duration_hours,
            courses=[],  # Would need to fetch and convert path courses
            prerequisites=path.prerequisites
        )
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        slug = re.sub(r'[^a-zA-Z0-9-]', '-', title.lower())
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug
    
    async def _update_course_rating(self, course_id: int):
        """Update course average rating"""
        # Calculate new average rating
        result = self.db.query(func.avg(CourseReview.rating)).filter(
            CourseReview.course_id == course_id
        ).scalar()
        
        review_count = self.db.query(func.count(CourseReview.id)).filter(
            CourseReview.course_id == course_id
        ).scalar()
        
        # Update course
        course = self.db.query(Course).filter(Course.id == course_id).first()
        course.average_rating = result or 0
        course.review_count = review_count or 0
        self.db.commit()
    
    def _calculate_relevance_score(self, user_id: int, course: Course) -> float:
        """Calculate relevance score for course recommendation"""
        score = 0.0
        
        # Base score for published courses
        score += 0.1
        
        # Bonus for featured courses
        if course.is_featured:
            score += 0.2
        
        # Score based on difficulty level (prefer courses matching user level)
        # This would use user's experience_level from profile
        score += 0.1
        
        # Score based on category preferences
        # This would analyze user's enrolled courses
        score += 0.1
        
        # Score based on prerequisites matching user's completed courses
        score += 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendation_reason(self, user_id: int, course: Course) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = [
            "Based on your learning history",
            "Matches your skill level",
            "Popular among similar learners",
            "Builds on your completed courses",
            "Recommended for your career goals"
        ]
        return reasons[0]  # Simplified
    
    def _get_personalized_factors(self, user_id: int, course: Course) -> List[str]:
        """Get factors that make this recommendation personalized"""
        factors = [
            "Your skill level matches this course difficulty",
            "Similar to courses you've completed",
            "Fits your learning preferences",
            "Recommended by AI based on your goals"
        ]
        return factors[:2]  # Return top 2 factors