"""
Community Features Models for Brain AI LMS
Handles alumni network, study groups, mentorship, and events
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class EventType(enum.Enum):
    WEBINAR = "webinar"
    WORKSHOP = "workshop"
    CONFERENCE = "conference"
    NETWORKING = "networking"
    Q_AND_A = "q_and_a"
    STUDY_SESSION = "study_session"

class EventStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StudyGroupStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StudyGroupPrivacy(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"

class OfficeHourType(enum.Enum):
    GROUP = "group"
    ONE_ON_ONE = "one_on_one"
    MENTORSHIP = "mentorship"

class AlumniStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MENTOR = "mentor"
    SPEAKER = "speaker"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_type = Column(Enum(EventType), nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), default="UTC")
    max_attendees = Column(Integer)
    current_attendees = Column(Integer, default=0)
    registration_required = Column(Boolean, default=True)
    registration_deadline = Column(DateTime(timezone=True))
    meeting_url = Column(String(500))
    recording_url = Column(String(500))
    materials_url = Column(String(500))
    speaker_bio = Column(Text)
    prerequisites = Column(Text)
    tags = Column(Text)  # JSON array of tags
    is_featured = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    registrations = relationship("EventRegistration", back_populates="event")
    created_by_user = relationship("User", back_populates="created_events")

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    attendance_confirmed = Column(Boolean, default=False)
    feedback_rating = Column(Integer)  # 1-5 scale
    feedback_comment = Column(Text)
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))

    event = relationship("Event", back_populates="registrations")
    user = relationship("User", back_populates="event_registrations")

class StudyGroup(Base):
    __tablename__ = "study_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    privacy_level = Column(Enum(StudyGroupPrivacy), default=StudyGroupPrivacy.PUBLIC)
    status = Column(Enum(StudyGroupStatus), default=StudyGroupStatus.ACTIVE)
    max_members = Column(Integer, default=20)
    current_members = Column(Integer, default=0)
    subject_area = Column(String(100))
    meeting_schedule = Column(String(100))  # "weekly", "bi-weekly", "custom"
    next_meeting_date = Column(DateTime(timezone=True))
    meeting_location = Column(String(255))  # Physical or virtual
    group_image_url = Column(String(500))
    tags = Column(Text)  # JSON array of tags
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    members = relationship("StudyGroupMember", back_populates="study_group")
    sessions = relationship("StudySession", back_populates="study_group")
    created_by_user = relationship("User", back_populates="created_study_groups")

class StudyGroupMember(Base):
    __tablename__ = "study_group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    study_group_id = Column(Integer, ForeignKey("study_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")  # "member", "moderator", "admin"
    joined_date = Column(DateTime(timezone=True), server_default=func.now())
    contribution_score = Column(Integer, default=0)  # Points for contributions
    is_active = Column(Boolean, default=True)

    study_group = relationship("StudyGroup", back_populates="members")
    user = relationship("User", back_populates="study_group_memberships")

class StudySession(Base):
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    study_group_id = Column(Integer, ForeignKey("study_groups.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    meeting_url = Column(String(500))
    recording_url = Column(String(500))
    agenda = Column(Text)
    notes = Column(Text)
    attendance_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    study_group = relationship("StudyGroup", back_populates="sessions")
    created_by_user = relationship("User", back_populates="created_study_sessions")
    attendees = relationship("StudySessionAttendance", back_populates="session")

class StudySessionAttendance(Base):
    __tablename__ = "study_session_attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True))
    left_at = Column(DateTime(timezone=True))
    participation_score = Column(Integer, default=0)

    session = relationship("StudySession", back_populates="attendees")
    user = relationship("User", back_populates="study_session_attendance")

class OfficeHour(Base):
    __tablename__ = "office_hours"
    
    id = Column(Integer, primary_key=True, index=True)
    expert_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    office_hour_type = Column(Enum(OfficeHourType), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    max_participants = Column(Integer, default=10)
    current_participants = Column(Integer, default=0)
    topics = Column(Text)  # JSON array of topics
    meeting_url = Column(String(500))
    status = Column(String(20), default="scheduled")  # "scheduled", "live", "completed", "cancelled"
    recording_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    expert = relationship("User", back_populates="office_hours_as_expert")
    registrations = relationship("OfficeHourRegistration", back_populates="office_hour")

class OfficeHourRegistration(Base):
    __tablename__ = "office_hour_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    office_hour_id = Column(Integer, ForeignKey("office_hours.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topics_of_interest = Column(Text)  # JSON array
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    attendance_confirmed = Column(Boolean, default=False)
    feedback_rating = Column(Integer)  # 1-5 scale
    feedback_comment = Column(Text)

    office_hour = relationship("OfficeHour", back_populates="registrations")
    user = relationship("User", back_populates="office_hour_registrations")

class AlumniProfile(Base):
    __tablename__ = "alumni_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    graduation_date = Column(DateTime(timezone=True))
    current_job_title = Column(String(255))
    current_company = Column(String(255))
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    github_url = Column(String(500))
    twitter_url = Column(String(500))
    bio = Column(Text)
    expertise_areas = Column(Text)  # JSON array
    availability_for_mentoring = Column(Boolean, default=False)
    willingness_to_speak = Column(Boolean, default=False)
    status = Column(Enum(AlumniStatus), default=AlumniStatus.ACTIVE)
    career_highlights = Column(Text)
    networking_interests = Column(Text)  # JSON array
    profile_completeness_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="alumni_profile")
    connections = relationship("AlumniConnection", back_populates="alumni_profile")

class AlumniConnection(Base):
    __tablename__ = "alumni_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    alumni_profile_id = Column(Integer, ForeignKey("alumni_profiles.id"), nullable=False)
    connected_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    connection_type = Column(String(20), default="network")  # "network", "mentorship", "collaboration"
    status = Column(String(20), default="pending")  # "pending", "accepted", "declined"
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    connected_at = Column(DateTime(timezone=True))

    alumni_profile = relationship("AlumniProfile", back_populates="connections")
    connected_user = relationship("User", back_populates="alumni_connections")

class JobOpportunity(Base):
    __tablename__ = "job_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    employment_type = Column(String(50))  # "full-time", "part-time", "contract", "freelance"
    experience_level = Column(String(50))  # "entry", "mid", "senior", "lead"
    salary_range_min = Column(Integer)
    salary_range_max = Column(Integer)
    currency = Column(String(3), default="USD")
    description = Column(Text)
    requirements = Column(Text)
    application_url = Column(String(500))
    application_deadline = Column(DateTime(timezone=True))
    is_remote = Column(Boolean, default=False)
    tags = Column(Text)  # JSON array
    status = Column(String(20), default="active")  # "active", "filled", "expired"
    views_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    posted_by_user = relationship("User", back_populates="posted_job_opportunities")
    applications = relationship("JobApplication", back_populates="job_opportunity")

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_opportunity_id = Column(Integer, ForeignKey("job_opportunities.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text)
    resume_url = Column(String(500))
    portfolio_url = Column(String(500))
    status = Column(String(20), default="pending")  # "pending", "reviewed", "interview", "offer", "rejected"
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    job_opportunity = relationship("JobOpportunity", back_populates="applications")
    applicant = relationship("User", back_populates="job_applications")