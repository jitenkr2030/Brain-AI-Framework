"""
Community Features Schemas for Brain AI LMS API
Handles events, study groups, office hours, alumni network, and job opportunities
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    WEBINAR = "webinar"
    WORKSHOP = "workshop"
    CONFERENCE = "conference"
    NETWORKING = "networking"
    Q_AND_A = "q_and_a"
    STUDY_SESSION = "study_session"

class EventStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StudyGroupStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StudyGroupPrivacy(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"

class OfficeHourType(str, Enum):
    GROUP = "group"
    ONE_ON_ONE = "one_on_one"
    MENTORSHIP = "mentorship"

class AlumniStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MENTOR = "mentor"
    SPEAKER = "speaker"

# Event Schemas
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    event_type: EventType = Field(..., description="Event type")
    start_datetime: datetime = Field(..., description="Event start date and time")
    end_datetime: datetime = Field(..., description="Event end date and time")
    timezone: str = Field(default="UTC", description="Event timezone")
    max_attendees: Optional[int] = Field(None, ge=1, description="Maximum attendees")
    registration_required: bool = Field(default=True, description="Registration required")
    registration_deadline: Optional[datetime] = Field(None, description="Registration deadline")
    meeting_url: Optional[str] = Field(None, description="Meeting URL")
    recording_url: Optional[str] = Field(None, description="Recording URL")
    materials_url: Optional[str] = Field(None, description="Materials URL")
    speaker_bio: Optional[str] = Field(None, description="Speaker bio")
    prerequisites: Optional[str] = Field(None, description="Prerequisites")
    tags: Optional[str] = Field(None, description="Tags as JSON array")
    is_featured: bool = Field(default=False, description="Featured event")

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[EventStatus] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    max_attendees: Optional[int] = Field(None, ge=1)
    registration_deadline: Optional[datetime] = None
    meeting_url: Optional[str] = None
    recording_url: Optional[str] = None
    materials_url: Optional[str] = None
    is_featured: Optional[bool] = None

class Event(EventBase):
    id: int
    status: EventStatus
    current_attendees: int = Field(default=0)
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Event Registration Schemas
class EventRegistrationBase(BaseModel):
    event_id: int = Field(..., description="Event ID")

class EventRegistrationCreate(EventRegistrationBase):
    pass

class EventRegistration(EventRegistrationBase):
    id: int
    user_id: int
    registration_date: datetime
    attendance_confirmed: bool = Field(default=False)
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comment: Optional[str] = None
    certificate_issued: bool = Field(default=False)
    certificate_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# Study Group Schemas
class StudyGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Study group name")
    description: Optional[str] = Field(None, description="Study group description")
    privacy_level: StudyGroupPrivacy = Field(default=StudyGroupPrivacy.PUBLIC, description="Privacy level")
    max_members: int = Field(default=20, ge=2, description="Maximum members")
    subject_area: Optional[str] = Field(None, max_length=100, description="Subject area")
    meeting_schedule: Optional[str] = Field(None, max_length=100, description="Meeting schedule")
    next_meeting_date: Optional[datetime] = Field(None, description="Next meeting date")
    meeting_location: Optional[str] = Field(None, max_length=255, description="Meeting location")
    group_image_url: Optional[str] = Field(None, description="Group image URL")
    tags: Optional[str] = Field(None, description="Tags as JSON array")

class StudyGroupCreate(StudyGroupBase):
    pass

class StudyGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    privacy_level: Optional[StudyGroupPrivacy] = None
    status: Optional[StudyGroupStatus] = None
    max_members: Optional[int] = Field(None, ge=2)
    subject_area: Optional[str] = Field(None, max_length=100)
    meeting_schedule: Optional[str] = Field(None, max_length=100)
    next_meeting_date: Optional[datetime] = None
    meeting_location: Optional[str] = Field(None, max_length=255)
    group_image_url: Optional[str] = None
    tags: Optional[str] = None

class StudyGroup(StudyGroupBase):
    id: int
    status: StudyGroupStatus
    current_members: int = Field(default=0)
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Study Group Member Schemas
class StudyGroupMemberBase(BaseModel):
    study_group_id: int = Field(..., description="Study group ID")

class StudyGroupMemberCreate(StudyGroupMemberBase):
    pass

class StudyGroupMember(BaseGroupMemberBase):
    id: int
    user_id: int
    role: str
    joined_date: datetime
    contribution_score: int = Field(default=0)
    is_active: bool = Field(default=True)
    
    class Config:
        from_attributes = True

# Study Session Schemas
class StudySessionBase(BaseModel):
    study_group_id: int = Field(..., description="Study group ID")
    title: str = Field(..., min_length=1, max_length=255, description="Session title")
    description: Optional[str] = Field(None, description="Session description")
    scheduled_start: datetime = Field(..., description="Scheduled start time")
    scheduled_end: datetime = Field(..., description="Scheduled end time")
    meeting_url: Optional[str] = Field(None, description="Meeting URL")
    recording_url: Optional[str] = Field(None, description="Recording URL")
    agenda: Optional[str] = Field(None, description="Session agenda")
    notes: Optional[str] = Field(None, description="Session notes")

class StudySessionCreate(StudySessionBase):
    pass

class StudySession(StudySessionBase):
    id: int
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    attendance_count: int = Field(default=0)
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Office Hour Schemas
class OfficeHourBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Office hour title")
    description: Optional[str] = Field(None, description="Office hour description")
    office_hour_type: OfficeHourType = Field(..., description="Office hour type")
    scheduled_date: datetime = Field(..., description="Scheduled date")
    duration_minutes: int = Field(default=60, gt=0, description="Duration in minutes")
    max_participants: int = Field(default=10, ge=1, description="Maximum participants")
    topics: Optional[str] = Field(None, description="Topics as JSON array")
    meeting_url: Optional[str] = Field(None, description="Meeting URL")

class OfficeHourCreate(OfficeHourBase):
    pass

class OfficeHour(OfficeHourBase):
    id: int
    expert_id: int
    current_participants: int = Field(default=0)
    status: str = Field(default="scheduled")
    recording_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Office Hour Registration Schemas
class OfficeHourRegistrationBase(BaseModel):
    office_hour_id: int = Field(..., description="Office hour ID")
    topics_of_interest: Optional[str] = Field(None, description="Topics of interest as JSON array")

class OfficeHourRegistrationCreate(OfficeHourRegistrationBase):
    pass

class OfficeHourRegistration(OfficeHourRegistrationBase):
    id: int
    user_id: int
    registration_date: datetime
    attendance_confirmed: bool = Field(default=False)
    feedback_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_comment: Optional[str] = None
    
    class Config:
        from_attributes = True

# Alumni Profile Schemas
class AlumniProfileBase(BaseModel):
    graduation_date: Optional[datetime] = Field(None, description="Graduation date")
    current_job_title: Optional[str] = Field(None, max_length=255, description="Current job title")
    current_company: Optional[str] = Field(None, max_length=255, description="Current company")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    portfolio_url: Optional[str] = Field(None, description="Portfolio URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    twitter_url: Optional[str] = Field(None, description="Twitter profile URL")
    bio: Optional[str] = Field(None, description="Bio")
    expertise_areas: Optional[str] = Field(None, description="Expertise areas as JSON array")
    availability_for_mentoring: bool = Field(default=False, description="Available for mentoring")
    willingness_to_speak: bool = Field(default=False, description="Willing to speak at events")
    status: AlumniStatus = Field(default=AlumniStatus.ACTIVE, description="Alumni status")
    career_highlights: Optional[str] = Field(None, description="Career highlights")
    networking_interests: Optional[str] = Field(None, description="Networking interests as JSON array")

class AlumniProfileCreate(AlumniProfileBase):
    pass

class AlumniProfileUpdate(BaseModel):
    graduation_date: Optional[datetime] = None
    current_job_title: Optional[str] = Field(None, max_length=255)
    current_company: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    bio: Optional[str] = None
    expertise_areas: Optional[str] = None
    availability_for_mentoring: Optional[bool] = None
    willingness_to_speak: Optional[bool] = None
    status: Optional[AlumniStatus] = None
    career_highlights: Optional[str] = None
    networking_interests: Optional[str] = None

class AlumniProfile(AlumniProfileBase):
    id: int
    user_id: int
    profile_completeness_score: int = Field(default=0)
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Job Opportunity Schemas
class JobOpportunityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    company: str = Field(..., min_length=1, max_length=255, description="Company name")
    location: Optional[str] = Field(None, max_length=255, description="Job location")
    employment_type: Optional[str] = Field(None, description="Employment type")
    experience_level: Optional[str] = Field(None, description="Experience level")
    salary_range_min: Optional[int] = Field(None, ge=0, description="Minimum salary")
    salary_range_max: Optional[int] = Field(None, ge=0, description="Maximum salary")
    currency: str = Field(default="USD", description="Salary currency")
    description: Optional[str] = Field(None, description="Job description")
    requirements: Optional[str] = Field(None, description="Job requirements")
    application_url: Optional[str] = Field(None, description="Application URL")
    application_deadline: Optional[datetime] = Field(None, description="Application deadline")
    is_remote: bool = Field(default=False, description="Remote work available")
    tags: Optional[str] = Field(None, description="Tags as JSON array")

class JobOpportunityCreate(JobOpportunityBase):
    pass

class JobOpportunity(JobOpportunityBase):
    id: int
    posted_by: int
    status: str = Field(default="active")
    views_count: int = Field(default=0)
    applications_count: int = Field(default=0)
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Job Application Schemas
class JobApplicationBase(BaseModel):
    job_opportunity_id: int = Field(..., description="Job opportunity ID")
    cover_letter: Optional[str] = Field(None, description="Cover letter")
    portfolio_url: Optional[str] = Field(None, description="Portfolio URL")

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplication(JobApplicationBase):
    id: int
    applicant_id: int
    resume_url: Optional[str] = None
    status: str = Field(default="pending")
    application_date: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Community Dashboard Schemas
class CommunityDashboard(BaseModel):
    total_events_this_month: int
    active_study_groups: int
    upcoming_office_hours: int
    active_alumni: int
    job_opportunities_posted: int
    study_group_participants: int
    event_registrations: int
    office_hour_attendance: int

# Event Analytics Schemas
class EventAnalytics(BaseModel):
    event_id: int
    title: str
    total_registrations: int
    actual_attendance: int
    attendance_rate: float
    average_feedback_rating: float
    total_feedback_count: int
    certificates_issued: int

# Study Group Analytics Schemas
class StudyGroupAnalytics(BaseModel):
    study_group_id: int
    name: str
    total_members: int
    active_members: int
    sessions_held: int
    average_attendance: float
    completion_rate: float

# Alumni Network Analytics Schemas
class AlumniNetworkAnalytics(BaseModel):
    total_alumni: int
    active_alumni: int
    available_mentors: int
    willing_speakers: int
    profile_completeness_average: float
    recent_graduates: int
    job_placement_rate: float