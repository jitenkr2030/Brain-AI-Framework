"""
Community Features Service for Brain AI LMS
Handles events, study groups, office hours, alumni network, and job opportunities
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
from .models.community_models import (
    Event, EventRegistration, StudyGroup, StudyGroupMember, StudySession,
    StudySessionAttendance, OfficeHour, OfficeHourRegistration,
    AlumniProfile, AlumniConnection, JobOpportunity, JobApplication
)
from .schemas.community_schemas import (
    EventCreate, EventUpdate, EventRegistrationCreate,
    StudyGroupCreate, StudyGroupUpdate, StudyGroupMemberCreate,
    StudySessionCreate, OfficeHourCreate, OfficeHourRegistrationCreate,
    AlumniProfileCreate, AlumniProfileUpdate, JobOpportunityCreate,
    JobApplicationCreate, CommunityDashboard, EventAnalytics,
    StudyGroupAnalytics, AlumniNetworkAnalytics
)

class CommunityService:
    """Service for managing community features and engagement"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Event Management
    async def create_event(self, event_data: EventCreate, created_by: int) -> Event:
        """Create a new event"""
        event = Event(**event_data.dict(), created_by=created_by)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    async def get_event(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        return self.db.query(Event).filter(Event.id == event_id).first()
    
    async def list_events(self, event_type: Optional[str] = None, status: Optional[str] = None, 
                         upcoming_only: bool = False) -> List[Event]:
        """List events with filters"""
        query = self.db.query(Event)
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if status:
            query = query.filter(Event.status == status)
        if upcoming_only:
            query = query.filter(Event.start_datetime > datetime.utcnow())
        
        return query.order_by(Event.start_datetime).all()
    
    async def update_event(self, event_id: int, update_data: EventUpdate) -> Optional[Event]:
        """Update event"""
        event = await self.get_event(event_id)
        if not event:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(event, field, value)
        
        self.db.commit()
        self.db.refresh(event)
        return event
    
    async def register_for_event(self, registration_data: EventRegistrationCreate, user_id: int) -> EventRegistration:
        """Register user for event"""
        # Check if event exists and has capacity
        event = await self.get_event(registration_data.event_id)
        if not event:
            raise ValueError("Event not found")
        
        if event.max_attendees and event.current_attendees >= event.max_attendees:
            raise ValueError("Event is full")
        
        # Check if user is already registered
        existing_registration = self.db.query(EventRegistration).filter(
            and_(
                EventRegistration.event_id == registration_data.event_id,
                EventRegistration.user_id == user_id
            )
        ).first()
        
        if existing_registration:
            raise ValueError("User already registered for this event")
        
        # Create registration
        registration = EventRegistration(
            **registration_data.dict(),
            user_id=user_id
        )
        self.db.add(registration)
        
        # Update event attendee count
        event.current_attendees += 1
        
        self.db.commit()
        self.db.refresh(registration)
        return registration
    
    async def confirm_event_attendance(self, event_id: int, user_id: int) -> Optional[EventRegistration]:
        """Confirm user attendance for event"""
        registration = self.db.query(EventRegistration).filter(
            and_(
                EventRegistration.event_id == event_id,
                EventRegistration.user_id == user_id
            )
        ).first()
        
        if registration:
            registration.attendance_confirmed = True
            self.db.commit()
            self.db.refresh(registration)
        
        return registration
    
    # Study Group Management
    async def create_study_group(self, group_data: StudyGroupCreate, created_by: int) -> StudyGroup:
        """Create a new study group"""
        group = StudyGroup(**group_data.dict(), created_by=created_by)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group
    
    async def get_study_group(self, group_id: int) -> Optional[StudyGroup]:
        """Get study group by ID"""
        return self.db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    
    async def list_study_groups(self, privacy_level: Optional[str] = None, 
                               status: Optional[str] = None) -> List[StudyGroup]:
        """List study groups with filters"""
        query = self.db.query(StudyGroup)
        
        if privacy_level:
            query = query.filter(StudyGroup.privacy_level == privacy_level)
        if status:
            query = query.filter(StudyGroup.status == status)
        
        return query.order_by(StudyGroup.created_at.desc()).all()
    
    async def join_study_group(self, group_id: int, user_id: int) -> StudyGroupMember:
        """Join a study group"""
        group = await self.get_study_group(group_id)
        if not group:
            raise ValueError("Study group not found")
        
        if group.current_members >= group.max_members:
            raise ValueError("Study group is full")
        
        # Check if user is already a member
        existing_member = self.db.query(StudyGroupMember).filter(
            and_(
                StudyGroupMember.study_group_id == group_id,
                StudyGroupMember.user_id == user_id,
                StudyGroupMember.is_active == True
            )
        ).first()
        
        if existing_member:
            raise ValueError("User already member of this study group")
        
        # Add member
        member = StudyGroupMember(
            study_group_id=group_id,
            user_id=user_id,
            role="member"
        )
        self.db.add(member)
        
        # Update member count
        group.current_members += 1
        
        self.db.commit()
        self.db.refresh(member)
        return member
    
    async def create_study_session(self, session_data: StudySessionCreate, created_by: int) -> StudySession:
        """Create a new study session"""
        session = StudySession(**session_data.dict(), created_by=created_by)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    async def record_session_attendance(self, session_id: int, user_id: int) -> StudySessionAttendance:
        """Record attendance for study session"""
        # Check if session exists
        session = self.db.query(StudySession).filter(StudySession.id == session_id).first()
        if not session:
            raise ValueError("Study session not found")
        
        # Check if user is member of the study group
        group_member = self.db.query(StudyGroupMember).filter(
            and_(
                StudyGroupMember.study_group_id == session.study_group_id,
                StudyGroupMember.user_id == user_id,
                StudyGroupMember.is_active == True
            )
        ).first()
        
        if not group_member:
            raise ValueError("User must be a member of the study group to attend sessions")
        
        # Record attendance
        attendance = StudySessionAttendance(
            session_id=session_id,
            user_id=user_id,
            joined_at=datetime.utcnow()
        )
        self.db.add(attendance)
        
        # Update session attendance count
        session.attendance_count += 1
        
        self.db.commit()
        self.db.refresh(attendance)
        return attendance
    
    # Office Hours Management
    async def create_office_hour(self, hour_data: OfficeHourCreate, expert_id: int) -> OfficeHour:
        """Create a new office hour session"""
        office_hour = OfficeHour(**hour_data.dict(), expert_id=expert_id)
        self.db.add(office_hour)
        self.db.commit()
        self.db.refresh(office_hour)
        return office_hour
    
    async def register_for_office_hour(self, registration_data: OfficeHourRegistrationCreate, user_id: int) -> OfficeHourRegistration:
        """Register for office hour"""
        office_hour = self.db.query(OfficeHour).filter(
            OfficeHour.id == registration_data.office_hour_id
        ).first()
        
        if not office_hour:
            raise ValueError("Office hour not found")
        
        if office_hour.current_participants >= office_hour.max_participants:
            raise ValueError("Office hour is full")
        
        # Check if user is already registered
        existing_registration = self.db.query(OfficeHourRegistration).filter(
            and_(
                OfficeHourRegistration.office_hour_id == registration_data.office_hour_id,
                OfficeHourRegistration.user_id == user_id
            )
        ).first()
        
        if existing_registration:
            raise ValueError("User already registered for this office hour")
        
        # Create registration
        registration = OfficeHourRegistration(
            **registration_data.dict(),
            user_id=user_id
        )
        self.db.add(registration)
        
        # Update participant count
        office_hour.current_participants += 1
        
        self.db.commit()
        self.db.refresh(registration)
        return registration
    
    # Alumni Network Management
    async def create_alumni_profile(self, profile_data: AlumniProfileCreate, user_id: int) -> AlumniProfile:
        """Create alumni profile"""
        profile = AlumniProfile(**profile_data.dict(), user_id=user_id)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    async def update_alumni_profile(self, profile_id: int, update_data: AlumniProfileUpdate) -> Optional[AlumniProfile]:
        """Update alumni profile"""
        profile = self.db.query(AlumniProfile).filter(AlumniProfile.id == profile_id).first()
        if not profile:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(profile, field, value)
        
        # Calculate profile completeness score
        profile.profile_completeness_score = self._calculate_profile_completeness(profile)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def _calculate_profile_completeness(self, profile: AlumniProfile) -> int:
        """Calculate profile completeness score (0-100)"""
        fields_to_check = [
            profile.graduation_date, profile.current_job_title, profile.current_company,
            profile.linkedin_url, profile.portfolio_url, profile.bio,
            profile.expertise_areas, profile.career_highlights
        ]
        
        completed_fields = sum(1 for field in fields_to_check if field)
        return int((completed_fields / len(fields_to_check)) * 100)
    
    async def search_alumni(self, expertise_areas: Optional[List[str]] = None,
                           availability_mentoring: Optional[bool] = None) -> List[AlumniProfile]:
        """Search alumni profiles"""
        query = self.db.query(AlumniProfile)
        
        if availability_mentoring is not None:
            query = query.filter(AlumniProfile.availability_for_mentoring == availability_mentoring)
        
        # For expertise areas, we'd need to parse JSON and search (simplified here)
        if expertise_areas:
            # This would need more sophisticated JSON searching in production
            pass
        
        return query.order_by(AlumniProfile.profile_completeness_score.desc()).all()
    
    async def connect_with_alumni(self, alumni_profile_id: int, connected_user_id: int, 
                                 connection_type: str = "network", message: str = None) -> AlumniConnection:
        """Create connection request with alumni"""
        connection = AlumniConnection(
            alumni_profile_id=alumni_profile_id,
            connected_user_id=connected_user_id,
            connection_type=connection_type,
            message=message
        )
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection
    
    # Job Opportunities Management
    async def create_job_opportunity(self, job_data: JobOpportunityCreate, posted_by: int) -> JobOpportunity:
        """Create job opportunity posting"""
        job = JobOpportunity(**job_data.dict(), posted_by=posted_by)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    async def list_job_opportunities(self, status: Optional[str] = None, 
                                   employment_type: Optional[str] = None,
                                   is_remote: Optional[bool] = None) -> List[JobOpportunity]:
        """List job opportunities"""
        query = self.db.query(JobOpportunity)
        
        if status:
            query = query.filter(JobOpportunity.status == status)
        if employment_type:
            query = query.filter(JobOpportunity.employment_type == employment_type)
        if is_remote is not None:
            query = query.filter(JobOpportunity.is_remote == is_remote)
        
        return query.order_by(JobOpportunity.created_at.desc()).all()
    
    async def apply_for_job(self, application_data: JobApplicationCreate, applicant_id: int) -> JobApplication:
        """Apply for job opportunity"""
        job = self.db.query(JobOpportunity).filter(
            JobOpportunity.id == application_data.job_opportunity_id
        ).first()
        
        if not job:
            raise ValueError("Job opportunity not found")
        
        # Check if already applied
        existing_application = self.db.query(JobApplication).filter(
            and_(
                JobApplication.job_opportunity_id == application_data.job_opportunity_id,
                JobApplication.applicant_id == applicant_id
            )
        ).first()
        
        if existing_application:
            raise ValueError("Already applied for this job")
        
        # Create application
        application = JobApplication(
            **application_data.dict(),
            applicant_id=applicant_id
        )
        self.db.add(application)
        
        # Update job application count
        job.applications_count += 1
        
        self.db.commit()
        self.db.refresh(application)
        return application
    
    # Analytics and Dashboard
    async def get_community_dashboard(self) -> CommunityDashboard:
        """Get community dashboard metrics"""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate metrics
        total_events_this_month = self.db.query(func.count(Event.id)).filter(
            Event.created_at >= month_start
        ).scalar() or 0
        
        active_study_groups = self.db.query(func.count(StudyGroup.id)).filter(
            StudyGroup.status == "active"
        ).scalar() or 0
        
        upcoming_office_hours = self.db.query(func.count(OfficeHour.id)).filter(
            OfficeHour.scheduled_date > now,
            OfficeHour.status == "scheduled"
        ).scalar() or 0
        
        active_alumni = self.db.query(func.count(AlumniProfile.id)).filter(
            AlumniProfile.status == "active"
        ).scalar() or 0
        
        job_opportunities_posted = self.db.query(func.count(JobOpportunity.id)).filter(
            JobOpportunity.created_at >= month_start
        ).scalar() or 0
        
        study_group_participants = self.db.query(func.count(StudyGroupMember.id)).filter(
            StudyGroupMember.is_active == True
        ).scalar() or 0
        
        event_registrations = self.db.query(func.count(EventRegistration.id)).filter(
            EventRegistration.registration_date >= month_start
        ).scalar() or 0
        
        office_hour_attendance = self.db.query(func.count(OfficeHourRegistration.id)).filter(
            OfficeHourRegistration.registration_date >= month_start
        ).scalar() or 0
        
        return CommunityDashboard(
            total_events_this_month=total_events_this_month,
            active_study_groups=active_study_groups,
            upcoming_office_hours=upcoming_office_hours,
            active_alumni=active_alumni,
            job_opportunities_posted=job_opportunities_posted,
            study_group_participants=study_group_participants,
            event_registrations=event_registrations,
            office_hour_attendance=office_hour_attendance
        )
    
    async def get_event_analytics(self, event_id: int) -> Optional[EventAnalytics]:
        """Get analytics for specific event"""
        event = await self.get_event(event_id)
        if not event:
            return None
        
        registrations = self.db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id
        ).all()
        
        total_registrations = len(registrations)
        actual_attendance = sum(1 for reg in registrations if reg.attendance_confirmed)
        attendance_rate = (actual_attendance / total_registrations * 100) if total_registrations > 0 else 0
        
        # Calculate average feedback rating
        feedback_ratings = [reg.feedback_rating for reg in registrations if reg.feedback_rating]
        average_feedback_rating = sum(feedback_ratings) / len(feedback_ratings) if feedback_ratings else 0
        
        total_feedback_count = len(feedback_ratings)
        certificates_issued = sum(1 for reg in registrations if reg.certificate_issued)
        
        return EventAnalytics(
            event_id=event_id,
            title=event.title,
            total_registrations=total_registrations,
            actual_attendance=actual_attendance,
            attendance_rate=attendance_rate,
            average_feedback_rating=average_feedback_rating,
            total_feedback_count=total_feedback_count,
            certificates_issued=certificates_issued
        )
    
    async def get_study_group_analytics(self, group_id: int) -> Optional[StudyGroupAnalytics]:
        """Get analytics for specific study group"""
        group = await self.get_study_group(group_id)
        if not group:
            return None
        
        members = self.db.query(StudyGroupMember).filter(
            StudyGroupMember.study_group_id == group_id,
            StudyGroupMember.is_active == True
        ).all()
        
        sessions = self.db.query(StudySession).filter(
            StudySession.study_group_id == group_id
        ).all()
        
        total_members = len(members)
        active_members = total_members  # Simplified - all active members are considered active
        
        sessions_held = len(sessions)
        
        # Calculate average attendance
        if sessions:
            total_attendance = sum(session.attendance_count for session in sessions)
            average_attendance = total_attendance / sessions_held
        else:
            average_attendance = 0
        
        # Simplified completion rate calculation
        completion_rate = 85.0  # Mock value
        
        return StudyGroupAnalytics(
            study_group_id=group_id,
            name=group.name,
            total_members=total_members,
            active_members=active_members,
            sessions_held=sessions_held,
            average_attendance=average_attendance,
            completion_rate=completion_rate
        )
    
    async def get_alumni_network_analytics(self) -> AlumniNetworkAnalytics:
        """Get alumni network analytics"""
        total_alumni = self.db.query(func.count(AlumniProfile.id)).scalar() or 0
        active_alumni = self.db.query(func.count(AlumniProfile.id)).filter(
            AlumniProfile.status == "active"
        ).scalar() or 0
        available_mentors = self.db.query(func.count(AlumniProfile.id)).filter(
            AlumniProfile.availability_for_mentoring == True
        ).scalar() or 0
        willing_speakers = self.db.query(func.count(AlumniProfile.id)).filter(
            AlumniProfile.willingness_to_speak == True
        ).scalar() or 0
        
        # Calculate average profile completeness
        avg_completeness = self.db.query(func.avg(AlumniProfile.profile_completeness_score)).scalar() or 0
        
        # Mock values for other metrics
        recent_graduates = 25
        job_placement_rate = 78.5
        
        return AlumniNetworkAnalytics(
            total_alumni=total_alumni,
            active_alumni=active_alumni,
            available_mentors=available_mentors,
            willing_speakers=willing_speakers,
            profile_completeness_average=avg_completeness,
            recent_graduates=recent_graduates,
            job_placement_rate=job_placement_rate
        )