"""
Community Features API Router for Brain AI LMS
Handles events, study groups, office hours, alumni network, and job opportunities
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..services.community_service import CommunityService
from ..schemas.community_schemas import (
    EventCreate, EventUpdate, Event as EventSchema,
    EventRegistrationCreate, EventRegistration as EventRegistrationSchema,
    StudyGroupCreate, StudyGroupUpdate, StudyGroup as StudyGroupSchema,
    StudyGroupMemberCreate, StudyGroupMember as StudyGroupMemberSchema,
    StudySessionCreate, StudySession as StudySessionSchema,
    OfficeHourCreate, OfficeHour as OfficeHourSchema,
    OfficeHourRegistrationCreate, OfficeHourRegistration as OfficeHourRegistrationSchema,
    AlumniProfileCreate, AlumniProfileUpdate, AlumniProfile as AlumniProfileSchema,
    JobOpportunityCreate, JobOpportunity as JobOpportunitySchema,
    JobApplicationCreate, JobApplication as JobApplicationSchema,
    CommunityDashboard, EventAnalytics, StudyGroupAnalytics, AlumniNetworkAnalytics
)

router = APIRouter(prefix="/community", tags=["community"])
logger = logging.getLogger(__name__)

# Dependency to get community service
def get_community_service(db: Session = Depends(get_db)) -> CommunityService:
    return CommunityService(db)

# Event Management Endpoints
@router.post("/events", response_model=EventSchema, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Create a new event"""
    try:
        return await service.create_event(event_data, current_user_id)
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events/{event_id}", response_model=EventSchema)
async def get_event(
    event_id: int,
    service: CommunityService = Depends(get_community_service)
):
    """Get event by ID"""
    event = await service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/events", response_model=List[EventSchema])
async def list_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    status: Optional[str] = Query(None, description="Filter by event status"),
    upcoming_only: bool = Query(False, description="Show only upcoming events"),
    limit: int = Query(50, ge=1, le=100, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: CommunityService = Depends(get_community_service)
):
    """List events with filters"""
    events = await service.list_events(event_type, status, upcoming_only)
    return events[offset:offset + limit]

@router.put("/events/{event_id}", response_model=EventSchema)
async def update_event(
    event_id: int,
    update_data: EventUpdate,
    service: CommunityService = Depends(get_community_service)
):
    """Update event"""
    event = await service.update_event(event_id, update_data)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("/events/{event_id}/register", response_model=EventRegistrationSchema, status_code=status.HTTP_201_CREATED)
async def register_for_event(
    event_id: int,
    registration_data: EventRegistrationCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Register for event"""
    try:
        registration_data.event_id = event_id
        return await service.register_for_event(registration_data, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering for event: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/events/{event_id}/attendance", response_model=EventRegistrationSchema)
async def confirm_event_attendance(
    event_id: int,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Confirm attendance for event"""
    registration = await service.confirm_event_attendance(event_id, current_user_id)
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration

# Study Group Management Endpoints
@router.post("/study-groups", response_model=StudyGroupSchema, status_code=status.HTTP_201_CREATED)
async def create_study_group(
    group_data: StudyGroupCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Create a new study group"""
    try:
        return await service.create_study_group(group_data, current_user_id)
    except Exception as e:
        logger.error(f"Error creating study group: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/study-groups/{group_id}", response_model=StudyGroupSchema)
async def get_study_group(
    group_id: int,
    service: CommunityService = Depends(get_community_service)
):
    """Get study group by ID"""
    group = await service.get_study_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")
    return group

@router.get("/study-groups", response_model=List[StudyGroupSchema])
async def list_study_groups(
    privacy_level: Optional[str] = Query(None, description="Filter by privacy level"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: CommunityService = Depends(get_community_service)
):
    """List study groups with filters"""
    groups = await service.list_study_groups(privacy_level, status)
    return groups[offset:offset + limit]

@router.post("/study-groups/{group_id}/join", response_model=StudyGroupMemberSchema, status_code=status.HTTP_201_CREATED)
async def join_study_group(
    group_id: int,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Join a study group"""
    try:
        return await service.join_study_group(group_id, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error joining study group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to join study group")

@router.post("/study-sessions", response_model=StudySessionSchema, status_code=status.HTTP_201_CREATED)
async def create_study_session(
    session_data: StudySessionCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Create a new study session"""
    try:
        return await service.create_study_session(session_data, current_user_id)
    except Exception as e:
        logger.error(f"Error creating study session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/study-sessions/{session_id}/attendance")
async def record_session_attendance(
    session_id: int,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Record attendance for study session"""
    try:
        attendance = await service.record_session_attendance(session_id, current_user_id)
        return {"message": "Attendance recorded successfully", "attendance_id": attendance.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error recording attendance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to record attendance")

# Office Hours Management Endpoints
@router.post("/office-hours", response_model=OfficeHourSchema, status_code=status.HTTP_201_CREATED)
async def create_office_hour(
    hour_data: OfficeHourCreate,
    current_user_id: int = 1,  # This should come from authentication (expert)
    service: CommunityService = Depends(get_community_service)
):
    """Create office hour session (experts only)"""
    try:
        return await service.create_office_hour(hour_data, current_user_id)
    except Exception as e:
        logger.error(f"Error creating office hour: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/office-hours", response_model=List[OfficeHourSchema])
async def list_office_hours(
    upcoming_only: bool = Query(True, description="Show only upcoming sessions"),
    limit: int = Query(50, ge=1, le=100, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: CommunityService = Depends(get_community_service)
):
    """List office hours"""
    now = datetime.utcnow()
    if upcoming_only:
        office_hours = service.db.query(OfficeHour).filter(
            OfficeHour.scheduled_date > now,
            OfficeHour.status == "scheduled"
        ).order_by(OfficeHour.scheduled_date).all()
    else:
        office_hours = service.db.query(OfficeHour).order_by(OfficeHour.scheduled_date.desc()).all()
    
    return office_hours[offset:offset + limit]

@router.post("/office-hours/{hour_id}/register", response_model=OfficeHourRegistrationSchema, status_code=status.HTTP_201_CREATED)
async def register_for_office_hour(
    hour_id: int,
    registration_data: OfficeHourRegistrationCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Register for office hour"""
    try:
        registration_data.office_hour_id = hour_id
        return await service.register_for_office_hour(registration_data, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering for office hour: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

# Alumni Network Management Endpoints
@router.post("/alumni-profile", response_model=AlumniProfileSchema, status_code=status.HTTP_201_CREATED)
async def create_alumni_profile(
    profile_data: AlumniProfileCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Create alumni profile"""
    try:
        return await service.create_alumni_profile(profile_data, current_user_id)
    except Exception as e:
        logger.error(f"Error creating alumni profile: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/alumni-profile/{profile_id}", response_model=AlumniProfileSchema)
async def update_alumni_profile(
    profile_id: int,
    update_data: AlumniProfileUpdate,
    service: CommunityService = Depends(get_community_service)
):
    """Update alumni profile"""
    profile = await service.update_alumni_profile(profile_id, update_data)
    if not profile:
        raise HTTPException(status_code=404, detail="Alumni profile not found")
    return profile

@router.get("/alumni-profile/{profile_id}", response_model=AlumniProfileSchema)
async def get_alumni_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """Get alumni profile by ID"""
    from ..models.community_models import AlumniProfile
    profile = db.query(AlumniProfile).filter(AlumniProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Alumni profile not found")
    return profile

@router.get("/alumni/search", response_model=List[AlumniProfileSchema])
async def search_alumni(
    expertise_areas: Optional[str] = Query(None, description="Expertise areas (JSON array)"),
    availability_mentoring: Optional[bool] = Query(None, description="Filter by mentoring availability"),
    service: CommunityService = Depends(get_community_service)
):
    """Search alumni profiles"""
    expertise_list = None
    if expertise_areas:
        try:
            import json
            expertise_list = json.loads(expertise_areas)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid expertise areas format")
    
    return await service.search_alumni(expertise_list, availability_mentoring)

@router.post("/alumni/{profile_id}/connect")
async def connect_with_alumni(
    profile_id: int,
    connection_type: str = Query("network", description="Connection type: network, mentorship, collaboration"),
    message: Optional[str] = Query(None, description="Connection message"),
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Create connection request with alumni"""
    try:
        connection = await service.connect_with_alumni(profile_id, current_user_id, connection_type, message)
        return {"message": "Connection request sent successfully", "connection_id": connection.id}
    except Exception as e:
        logger.error(f"Error creating alumni connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create connection")

# Job Opportunities Endpoints
@router.post("/jobs", response_model=JobOpportunitySchema, status_code=status.HTTP_201_CREATED)
async def create_job_opportunity(
    job_data: JobOpportunityCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Create job opportunity posting"""
    try:
        return await service.create_job_opportunity(job_data, current_user_id)
    except Exception as e:
        logger.error(f"Error creating job opportunity: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs", response_model=List[JobOpportunitySchema])
async def list_job_opportunities(
    status: Optional[str] = Query(None, description="Filter by status"),
    employment_type: Optional[str] = Query(None, description="Filter by employment type"),
    is_remote: Optional[bool] = Query(None, description="Filter by remote work availability"),
    limit: int = Query(50, ge=1, le=100, description="Limit results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    service: CommunityService = Depends(get_community_service)
):
    """List job opportunities"""
    jobs = await service.list_job_opportunities(status, employment_type, is_remote)
    return jobs[offset:offset + limit]

@router.post("/jobs/{job_id}/apply", response_model=JobApplicationSchema, status_code=status.HTTP_201_CREATED)
async def apply_for_job(
    job_id: int,
    application_data: JobApplicationCreate,
    current_user_id: int = 1,  # This should come from authentication
    service: CommunityService = Depends(get_community_service)
):
    """Apply for job opportunity"""
    try:
        application_data.job_opportunity_id = job_id
        return await service.apply_for_job(application_data, current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying for job: {str(e)}")
        raise HTTPException(status_code=500, detail="Application failed")

@router.get("/jobs/{job_id}/applications", response_model=List[JobApplicationSchema])
async def list_job_applications(
    job_id: int,
    db: Session = Depends(get_db)
):
    """List applications for a job (job poster only)"""
    from ..models.community_models import JobApplication
    return db.query(JobApplication).filter(JobApplication.job_opportunity_id == job_id).all()

# Analytics and Dashboard Endpoints
@router.get("/dashboard", response_model=CommunityDashboard)
async def get_community_dashboard(
    service: CommunityService = Depends(get_community_service)
):
    """Get community dashboard metrics"""
    try:
        return await service.get_community_dashboard()
    except Exception as e:
        logger.error(f"Error getting community dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@router.get("/events/{event_id}/analytics", response_model=EventAnalytics)
async def get_event_analytics(
    event_id: int,
    service: CommunityService = Depends(get_community_service)
):
    """Get analytics for specific event"""
    analytics = await service.get_event_analytics(event_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Event not found or no analytics available")
    return analytics

@router.get("/study-groups/{group_id}/analytics", response_model=StudyGroupAnalytics)
async def get_study_group_analytics(
    group_id: int,
    service: CommunityService = Depends(get_community_service)
):
    """Get analytics for specific study group"""
    analytics = await service.get_study_group_analytics(group_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Study group not found or no analytics available")
    return analytics

@router.get("/alumni/analytics", response_model=AlumniNetworkAnalytics)
async def get_alumni_network_analytics(
    service: CommunityService = Depends(get_community_service)
):
    """Get alumni network analytics"""
    try:
        return await service.get_alumni_network_analytics()
    except Exception as e:
        logger.error(f"Error getting alumni analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alumni analytics")

# Community Engagement Endpoints
@router.get("/engagement/metrics")
async def get_engagement_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    service: CommunityService = Depends(get_community_service)
):
    """Get community engagement metrics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get various engagement metrics
    dashboard = await service.get_community_dashboard()
    
    return {
        "period_days": days,
        "events_this_period": dashboard.total_events_this_month,
        "study_groups_active": dashboard.active_study_groups,
        "office_hours_this_period": dashboard.upcoming_office_hours,
        "alumni_engagement": dashboard.active_alumni,
        "job_opportunities_this_period": dashboard.job_opportunities_posted,
        "total_participants": (
            dashboard.study_group_participants + 
            dashboard.event_registrations + 
            dashboard.office_hour_attendance
        ),
        "generated_at": datetime.utcnow().isoformat()
    }

# Health Check Endpoint
@router.get("/health")
async def community_health_check():
    """Health check for community service"""
    return {
        "status": "healthy",
        "service": "community",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "event_management",
            "study_groups",
            "office_hours",
            "alumni_network",
            "job_opportunities",
            "community_analytics"
        ]
    }