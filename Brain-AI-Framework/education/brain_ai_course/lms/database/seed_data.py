"""
Database seed data script for Brain AI LMS
Populates the database with initial data for development and testing
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.lms_models import (
    User, UserRole, Course, CourseLevel, CourseCategory,
    Module, Lesson, LessonType, Enrollment, Progress
)


def generate_certificate_number() -> str:
    """Generate a unique certificate number"""
    return f"BAI-{uuid.uuid4().hex[:8].upper()}"


def create_admin_user(db: Session) -> User:
    """Create default admin user"""
    admin = db.query(User).filter(User.email == "admin@brainai.com").first()
    if admin:
        return admin
    
    admin = User(
        email="admin@brainai.com",
        username="admin",
        full_name="Brain AI Administrator",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.tMPBxQbV1Vj7Fe",  # "admin123"
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"Created admin user: {admin.email}")
    return admin


def create_instructor(db: Session) -> User:
    """Create sample instructor"""
    instructor = db.query(User).filter(User.email == "instructor@brainai.com").first()
    if instructor:
        return instructor
    
    instructor = User(
        email="instructor@brainai.com",
        username="brain_ai_instructor",
        full_name="Dr. Sarah Chen",
        hashed_password="$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi",  # "password"
        role=UserRole.INSTRUCTOR,
        is_active=True,
        is_verified=True
    )
    db.add(instructor)
    db.commit()
    db.refresh(instructor)
    print(f"Created instructor: {instructor.email}")
    return instructor


def create_sample_student(db: Session) -> User:
    """Create sample student"""
    student = db.query(User).filter(User.email == "student@brainai.com").first()
    if student:
        return student
    
    student = User(
        email="student@brainai.com",
        username="brain_ai_student",
        full_name="John Doe",
        hashed_password="$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi",  # "password"
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    print(f"Created student: {student.email}")
    return student


def create_foundation_course(db: Session, instructor: User) -> Course:
    """Create Foundation level course"""
    course = db.query(Course).filter(Course.slug == "brain-ai-fundamentals").first()
    if course:
        return course
    
    course = Course(
        title="Brain AI Fundamentals",
        slug="brain-ai-fundamentals",
        description="""This comprehensive course introduces you to the fascinating world of brain-inspired artificial intelligence. 
        
You'll learn how memory architectures mimic the human brain's ability to store and retrieve information, and how learning engines enable continuous improvement without forgetting previous knowledge.

By the end of this course, you'll have a solid understanding of the foundational concepts that make brain-inspired AI different from traditional machine learning approaches.""",
        short_description="Master the fundamentals of brain-inspired AI with hands-on coding exercises.",
        level=CourseLevel.FOUNDATION,
        category=CourseCategory.BRAIN_AI_FUNDAMENTALS,
        duration_hours=40,
        difficulty_rating=1.0,
        price_usd=2500.00,
        instructor_id=instructor.id,
        learning_outcomes=[
            "Understand brain-inspired AI concepts and architecture",
            "Build simple memory systems from scratch",
            "Implement basic learning algorithms",
            "Create your first brain AI application"
        ],
        prerequisites=[],
        syllabus={
            "modules": [
                {"title": "Introduction to Brain AI", "lessons": 5},
                {"title": "Memory Systems Fundamentals", "lessons": 8},
                {"title": "Learning Algorithms Basics", "lessons": 7}
            ]
        },
        has_interactive_labs=True,
        has_certification=True,
        has_live_sessions=False,
        has_community_access=True,
        is_published=True,
        is_featured=True
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    print(f"Created course: {course.title}")
    return course


def create_implementation_course(db: Session, instructor: User) -> Course:
    """Create Implementation level course"""
    course = db.query(Course).filter(Course.slug == "advanced-memory-architectures").first()
    if course:
        return course
    
    course = Course(
        title="Advanced Memory Architectures",
        slug="advanced-memory-architectures",
        description="""Dive deep into advanced memory systems and associative networks that power modern brain-inspired AI applications.
        
This course covers vector-based memory systems, attention mechanisms, and how to optimize memory performance for production environments.""",
        short_description="Master advanced memory architectures and associative networks.",
        level=CourseLevel.ADVANCED,
        category=CourseCategory.MEMORY_SYSTEMS,
        duration_hours=60,
        difficulty_rating=4.0,
        price_usd=3500.00,
        instructor_id=instructor.id,
        learning_outcomes=[
            "Design complex memory systems",
            "Implement associative networks",
            "Optimize memory performance for production",
            "Build scalable brain AI applications"
        ],
        prerequisites=["brain-ai-fundamentals"],
        syllabus={
            "modules": [
                {"title": "Vector Memory Systems", "lessons": 10},
                {"title": "Associative Networks", "lessons": 12},
                {"title": "Memory Optimization", "lessons": 8}
            ]
        },
        has_interactive_labs=True,
        has_certification=True,
        has_live_sessions=True,
        has_community_access=True,
        is_published=True,
        is_featured=True
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    print(f"Created course: {course.title}")
    return course


def create_mastery_course(db: Session, instructor: User) -> Course:
    """Create Mastery level course"""
    course = db.query(Course).filter(Course.slug == "custom-model-development").first()
    if course:
        return course
    
    course = Course(
        title="Custom Model Development",
        slug="custom-model-development",
        description="""Take your skills to the expert level with custom model development and research-level implementations.
        
This capstone course guides you through building a production-ready brain AI system from scratch, with one-on-one mentorship from industry experts.""",
        short_description="Expert-level training with capstone project and mentorship.",
        level=CourseLevel.EXPERT,
        category=CourseCategory.RESEARCH_ADVANCED,
        duration_hours=40,
        difficulty_rating=5.0,
        price_usd=5000.00,
        instructor_id=instructor.id,
        learning_outcomes=[
            "Develop custom brain AI models",
            "Implement research-level algorithms",
            "Build production-ready applications",
            "Present capstone project to industry experts"
        ],
        prerequisites=["brain-ai-fundamentals", "advanced-memory-architectures"],
        syllabus={
            "modules": [
                {"title": "Advanced AI Techniques", "lessons": 8},
                {"title": "Custom Model Architecture", "lessons": 10},
                {"title": "Capstone Project", "lessons": 12}
            ]
        },
        has_interactive_labs=True,
        has_certification=True,
        has_live_sessions=True,
        has_community_access=True,
        is_published=True,
        is_featured=True
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    print(f"Created course: {course.title}")
    return course


def create_modules_and_lessons(db: Session, course: Course):
    """Create modules and lessons for a course"""
    # Check if modules already exist
    existing_modules = db.query(Module).filter(Module.course_id == course.id).count()
    if existing_modules > 0:
        return
    
    # Create modules based on syllabus
    syllabus = course.syllabus or {}
    modules_data = syllabus.get("modules", [
        {"title": "Getting Started", "lessons": 3},
        {"title": "Core Concepts", "lessons": 5},
        {"title": "Practical Applications", "lessons": 4}
    ])
    
    for idx, module_data in enumerate(modules_data):
        module = Module(
            course_id=course.id,
            title=module_data["title"],
            description=f"Learn about {module_data['title'].lower()} in this module.",
            order_index=idx
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        
        # Create lessons for each module
        for lesson_idx in range(module_data["lessons"]):
            lesson = Lesson(
                module_id=module.id,
                title=f"Lesson {lesson_idx + 1}: {module_data['title']} Part {lesson_idx + 1}",
                description=f"Content for {module_data['title']} - Part {lesson_idx + 1}",
                type=LessonType.VIDEO if lesson_idx % 2 == 0 else LessonType.INTERACTIVE_LAB,
                duration_minutes=30 + (lesson_idx * 5),
                order_index=lesson_idx,
                is_free_preview=lesson_idx == 0,
                content={
                    "video_url": f"https://example.com/videos/{course.slug}/module-{idx}/lesson-{lesson_idx}.mp4",
                    "transcript": "Lesson transcript here...",
                    "resources": ["Resource 1", "Resource 2"]
                }
            )
            db.add(lesson)
    
    db.commit()
    print(f"Created modules and lessons for: {course.title}")


def seed_database():
    """Main function to seed all database data"""
    print("Starting database seeding...")
    
    # Create database tables
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified.")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create users
        admin = create_admin_user(db)
        instructor = create_instructor(db)
        student = create_sample_student(db)
        
        # Create courses
        foundation_course = create_foundation_course(db, instructor)
        implementation_course = create_implementation_course(db, instructor)
        mastery_course = create_mastery_course(db, instructor)
        
        # Create modules and lessons
        create_modules_and_lessons(db, foundation_course)
        create_modules_and_lessons(db, implementation_course)
        create_modules_and_lessons(db, mastery_course)
        
        # Create sample enrollment
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == student.id,
            Enrollment.course_id == foundation_course.id
        ).first()
        
        if not enrollment:
            enrollment = Enrollment(
                user_id=student.id,
                course_id=foundation_course.id,
                status="active",
                progress_percentage=25.0,
                amount_paid=2500.00
            )
            db.add(enrollment)
            db.commit()
            print(f"Created sample enrollment for: {student.email}")
        
        print("\n✅ Database seeding completed successfully!")
        print("\n📋 Test Accounts:")
        print(f"   Admin: admin@brainai.com / admin123")
        print(f"   Instructor: instructor@brainai.com / password")
        print(f"   Student: student@brainai.com / password")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
