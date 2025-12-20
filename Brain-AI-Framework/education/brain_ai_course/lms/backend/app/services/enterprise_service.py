"""
Enterprise Service
Provides enterprise features including team management, custom curriculum, analytics, and white-label options
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from enum import Enum
import json
import logging

from app.database import get_db
from app.models.user import User, UserRole
from app.models.lms_models import (
    Course, CourseEnrollment, Progress, EnterpriseProfile, LearningPath
)
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

class TeamRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    LEARNER = "learner"
    VIEWER = "viewer"

class CurriculumType(Enum):
    STANDARD = "standard"
    CUSTOM = "custom"
    INDUSTRY_SPECIFIC = "industry_specific"
    ROLE_BASED = "role_based"

class AnalyticsPeriod(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class EnterpriseTeam:
    """Enterprise team structure"""
    team_id: str
    enterprise_id: int
    name: str
    description: str
    department: str
    manager_id: int
    members: List[int]
    custom_curriculum_id: Optional[str]
    learning_paths: List[str]
    budget_allocated: float
    budget_used: float
    created_at: datetime
    settings: Dict[str, Any]

@dataclass
class CustomCurriculum:
    """Custom curriculum for enterprise clients"""
    curriculum_id: str
    enterprise_id: int
    name: str
    description: str
    curriculum_type: CurriculumType
    target_roles: List[str]
    industry: str
    duration_weeks: int
    courses: List[Dict[str, Any]]  # course_id, order, customizations
    assessments: List[Dict[str, Any]]
    certification_requirements: Dict[str, Any]
    created_by: int
    created_at: datetime
    is_active: bool
    customization_settings: Dict[str, Any]

@dataclass
class EnterpriseAnalytics:
    """Enterprise analytics data"""
    enterprise_id: int
    period: AnalyticsPeriod
    date_range: Tuple[datetime, datetime]
    total_learners: int
    active_learners: int
    completed_learners: int
    total_courses: int
    average_completion_rate: float
    total_learning_hours: int
    engagement_metrics: Dict[str, float]
    skill_assessments: Dict[str, Any]
    business_impact: Dict[str, Any]
    roi_metrics: Dict[str, float]
    generated_at: datetime

@dataclass
class WhiteLabelConfig:
    """White-label configuration for enterprise clients"""
    config_id: str
    enterprise_id: int
    domain: str
    brand_name: str
    logo_url: str
    primary_color: str
    secondary_color: str
    accent_color: str
    custom_css: str
    custom_domain_settings: Dict[str, Any]
    feature_flags: Dict[str, bool]
    api_branding: Dict[str, str]
    email_templates: Dict[str, str]
    created_at: datetime
    is_active: bool

class EnterpriseService:
    """Service managing enterprise features and functionality"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService()
        self.active_teams: Dict[str, EnterpriseTeam] = {}
        self.custom_curricula: Dict[str, CustomCurriculum] = {}
        self.white_label_configs: Dict[str, WhiteLabelConfig] = {}
    
    # Team Management
    async def create_enterprise_team(
        self,
        enterprise_id: int,
        name: str,
        description: str,
        department: str,
        manager_id: int,
        budget_allocated: float = 0.0,
        settings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new enterprise team"""
        
        team_id = str(uuid.uuid4())
        
        # Validate enterprise and manager
        enterprise = self.db.query(EnterpriseProfile).filter(
            EnterpriseProfile.id == enterprise_id
        ).first()
        
        if not enterprise:
            return {"success": False, "error": "Enterprise profile not found"}
        
        manager = self.db.query(User).filter(User.id == manager_id).first()
        if not manager:
            return {"success": False, "error": "Manager not found"}
        
        # Create team
        team = EnterpriseTeam(
            team_id=team_id,
            enterprise_id=enterprise_id,
            name=name,
            description=description,
            department=department,
            manager_id=manager_id,
            members=[manager_id],  # Manager is initially a member
            custom_curriculum_id=None,
            learning_paths=[],
            budget_allocated=budget_allocated,
            budget_used=0.0,
            created_at=datetime.utcnow(),
            settings=settings or {}
        )
        
        # Store team
        await self._store_enterprise_team(team)
        
        # Track analytics
        await self.analytics_service.track_event(
            user_id=manager_id,
            event_type="enterprise_team_created",
            event_data={
                "team_id": team_id,
                "enterprise_id": enterprise_id,
                "department": department,
                "budget_allocated": budget_allocated
            }
        )
        
        return {
            "success": True,
            "team_id": team_id,
            "team": {
                "id": team_id,
                "name": name,
                "department": department,
                "manager_id": manager_id,
                "member_count": 1,
                "budget_allocated": budget_allocated
            }
        }
    
    async def add_team_member(
        self,
        team_id: str,
        user_id: int,
        role: TeamRole = TeamRole.LEARNER
    ) -> Dict[str, Any]:
        """Add member to enterprise team"""
        
        team = await self._get_enterprise_team(team_id)
        if not team:
            return {"success": False, "error": "Team not found"}
        
        #
        user = self.db.query(User).filter(User.id == Check if user exists user_id).first user:
            return()
        if not {"success": False, "error": "User not found"}
        
        # Check if already a member
        if user_id in team.members:
            return {"success": False, "error": "User is already a team member"}
        
        # Add member
        team.members.append(user_id)
        await self._update_enterprise_team(team)
        
        # Update user enterprise profile if needed
        await self._update_user_enterprise_profile(user_id, team.enterprise_id, role)
        
        # Send welcome notification
        await self._send_team_welcome_notification(user_id, team_id)
        
        return {
            "success": True,
            "team_id": team_id,
            "user_id": user_id,
            "role": role.value
        }
    
    async def get_team_dashboard(self, team_id: str) -> Dict[str, Any]:
        """Get comprehensive team dashboard"""
        
        team = await self._get_enterprise_team(team_id)
        if not team:
            return {"success": False, "error": "Team not found"}
        
        # Get team member details
        members = await self._get_team_members(team_id)
        
        # Get learning progress for team
        team_progress = await self._get_team_learning_progress(team_id)
        
        # Get team analytics
        team_analytics = await self._get_team_analytics(team_id)
        
        # Calculate team metrics
        total_members = len(members)
        active_members = sum(1 for member in members if member.get("is_active", False))
        completed_courses = sum(member.get("completed_courses", 0) for member in members)
        total_learning_hours = sum(member.get("total_learning_hours", 0) for member in members)
        average_completion_rate = sum(member.get("completion_rate", 0) for member in members) / total_members if total_members > 0 else 0
        
        return {
            "success": True,
            "team": {
                "id": team_id,
                "name": team.name,
                "department": team.department,
                "description": team.description,
                "manager_id": team.manager_id,
                "created_at": team.created_at.isoformat()
            },
            "metrics": {
                "total_members": total_members,
                "active_members": active_members,
                "completed_courses": completed_courses,
                "total_learning_hours": total_learning_hours,
                "average_completion_rate": average_completion_rate,
                "budget_utilization": (team.budget_used / team.budget_allocated * 100) if team.budget_allocated > 0 else 0
            },
            "members": members,
            "progress": team_progress,
            "analytics": team_analytics
        }
    
    # Custom Curriculum
    async def create_custom_curriculum(
        self,
        enterprise_id: int,
        name: str,
        description: str,
        curriculum_type: CurriculumType,
        target_roles: List[str],
        industry: str,
        duration_weeks: int,
        created_by: int
    ) -> Dict[str, Any]:
        """Create custom curriculum for enterprise"""
        
        curriculum_id = str(uuid.uuid4())
        
        # Validate enterprise
        enterprise = self.db.query(EnterpriseProfile).filter(
            EnterpriseProfile.id == enterprise_id
        ).first()
        
        if not enterprise:
            return {"success": False, "error": "Enterprise profile not found"}
        
        # Create curriculum
        curriculum = CustomCurriculum(
            curriculum_id=curriculum_id,
            enterprise_id=enterprise_id,
            name=name,
            description=description,
            curriculum_type=curriculum_type,
            target_roles=target_roles,
            industry=industry,
            duration_weeks=duration_weeks,
            courses=[],
            assessments=[],
            certification_requirements={},
            created_by=created_by,
            created_at=datetime.utcnow(),
            is_active=True,
            customization_settings={}
        )
        
        # Store curriculum
        await self._store_custom_curriculum(curriculum)
        
        return {
            "success": True,
            "curriculum_id": curriculum_id,
            "curriculum": {
                "id": curriculum_id,
                "name": name,
                "type": curriculum_type.value,
                "target_roles": target_roles,
                "industry": industry,
                "duration_weeks": duration_weeks
            }
        }
    
    async def add_course_to_curriculum(
        self,
        curriculum_id: str,
        course_id: int,
        order_index: int,
        customizations: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Add course to custom curriculum"""
        
        curriculum = await self._get_custom_curriculum(curriculum_id)
        if not curriculum:
            return {"success": False, "error": "Curriculum not found"}
        
        # Validate course exists
        course = self.db.query(Course).filter(Course.id == course_id).first()
        if not course:
            return {"success": False, "error": "Course not found"}
        
        # Add course to curriculum
        course_entry = {
            "course_id": course_id,
            "order_index": order_index,
            "customizations": customizations or {},
            "prerequisites": [],  # Would be set based on curriculum structure
            "estimated_hours": course.duration_hours,
            "assessment_requirements": {}
        }
        
        curriculum.courses.append(course_entry)
        curriculum.courses.sort(key=lambda x: x["order_index"])
        
        await self._update_custom_curriculum(curriculum)
        
        return {
            "success": True,
            "curriculum_id": curriculum_id,
            "course_id": course_id,
            "order_index": order_index
        }
    
    async def get_curriculum_builder(self, curriculum_id: str) -> Dict[str, Any]:
        """Get curriculum builder interface data"""
        
        curriculum = await self._get_custom_curriculum(curriculum_id)
        if not curriculum:
            return {"success": False, "error": "Curriculum not found"}
        
        # Get all available courses
        available_courses = self.db.query(Course).filter(
            Course.is_published == True
        ).all()
        
        # Get current curriculum courses with details
        curriculum_courses = []
        for course_entry in curriculum.courses:
            course = next((c for c in available_courses if c.id == course_entry["course_id"]), None)
            if course:
                curriculum_courses.append({
                    "course_id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "duration_hours": course.duration_hours,
                    "level": course.level,
                    "order_index": course_entry["order_index"],
                    "customizations": course_entry["customizations"]
                })
        
        return {
            "success": True,
            "curriculum": {
                "id": curriculum_id,
                "name": curriculum.name,
                "description": curriculum.description,
                "type": curriculum.curriculum_type.value,
                "target_roles": curriculum.target_roles,
                "industry": curriculum.industry,
                "duration_weeks": curriculum.duration_weeks,
                "courses": curriculum_courses,
                "assessments": curriculum.assessments,
                "certification_requirements": curriculum.certification_requirements
            },
            "available_courses": [
                {
                    "id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "duration_hours": course.duration_hours,
                    "level": course.level,
                    "category": course.category,
                    "difficulty_rating": course.difficulty_rating
                }
                for course in available_courses
            ]
        }
    
    # Enterprise Analytics
    async def get_enterprise_analytics(
        self,
        enterprise_id: int,
        period: AnalyticsPeriod,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comprehensive enterprise analytics"""
        
        # Validate enterprise
        enterprise = self.db.query(EnterpriseProfile).filter(
            EnterpriseProfile.id == enterprise_id
        ).first()
        
        if not enterprise:
            return {"success": False, "error": "Enterprise profile not found"}
        
        # Get all teams for enterprise
        teams = await self._get_enterprise_teams(enterprise_id)
        
        # Aggregate data across all teams
        total_learners = 0
        active_learners = 0
        completed_learners = 0
        total_courses = 0
        total_learning_hours = 0
        
        team_analytics = []
        
        for team in teams:
            team_data = await self._get_team_analytics(team.team_id, start_date, end_date)
            team_analytics.append(team_data)
            
            total_learners += team_data["total_learners"]
            active_learners += team_data["active_learners"]
            completed_learners += team_data["completed_learners"]
            total_courses += team_data["total_courses"]
            total_learning_hours += team_data["total_learning_hours"]
        
        # Calculate enterprise metrics
        average_completion_rate = (completed_learners / total_learners * 100) if total_learners > 0 else 0
        
        # Get skill assessments
        skill_assessments = await self._get_enterprise_skill_assessments(enterprise_id, start_date, end_date)
        
        # Calculate business impact
        business_impact = await self._calculate_business_impact(enterprise_id, start_date, end_date)
        
        # Calculate ROI metrics
        roi_metrics = await self._calculate_roi_metrics(enterprise_id, start_date, end_date)
        
        # Create analytics object
        analytics = EnterpriseAnalytics(
            enterprise_id=enterprise_id,
            period=period,
            date_range=(start_date, end_date),
            total_learners=total_learners,
            active_learners=active_learners,
            completed_learners=completed_learners,
            total_courses=total_courses,
            average_completion_rate=average_completion_rate,
            total_learning_hours=total_learning_hours,
            engagement_metrics={},  # Would calculate detailed engagement metrics
            skill_assessments=skill_assessments,
            business_impact=business_impact,
            roi_metrics=roi_metrics,
            generated_at=datetime.utcnow()
        )
        
        return {
            "success": True,
            "analytics": {
                "enterprise_id": enterprise_id,
                "period": period.value,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summary": {
                    "total_learners": total_learners,
                    "active_learners": active_learners,
                    "completed_learners": completed_learners,
                    "total_courses": total_courses,
                    "average_completion_rate": average_completion_rate,
                    "total_learning_hours": total_learning_hours
                },
                "team_analytics": team_analytics,
                "skill_assessments": skill_assessments,
                "business_impact": business_impact,
                "roi_metrics": roi_metrics,
                "generated_at": analytics.generated_at.isoformat()
            }
        }
    
    async def get_analytics_dashboard(self, enterprise_id: int) -> Dict[str, Any]:
        """Get enterprise analytics dashboard"""
        
        # Get current period analytics
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_analytics = await self.get_enterprise_analytics(
            enterprise_id, AnalyticsPeriod.MONTHLY, start_of_month, now
        )
        
        # Get year-to-date analytics
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        yearly_analytics = await self.get_enterprise_analytics(
            enterprise_id, AnalyticsPeriod.YEARLY, start_of_year, now
        )
        
        # Get trend data
        trend_data = await self._get_analytics_trends(enterprise_id, start_of_year, now)
        
        # Get top performing teams
        top_teams = await self._get_top_performing_teams(enterprise_id)
        
        # Get skill gap analysis
        skill_gaps = await self._get_skill_gap_analysis(enterprise_id)
        
        return {
            "success": True,
            "dashboard": {
                "enterprise_id": enterprise_id,
                "current_metrics": monthly_analytics["analytics"]["summary"],
                "year_to_date": yearly_analytics["analytics"]["summary"],
                "trends": trend_data,
                "top_teams": top_teams,
                "skill_gaps": skill_gaps,
                "alerts": await self._get_enterprise_alerts(enterprise_id),
                "recommendations": await self._get_analytics_recommendations(enterprise_id)
            }
        }
    
    # White Label Configuration
    async def create_white_label_config(
        self,
        enterprise_id: int,
        domain: str,
        brand_name: str,
        logo_url: str,
        color_scheme: Dict[str, str],
        created_by: int
    ) -> Dict[str, Any]:
        """Create white-label configuration for enterprise"""
        
        config_id = str(uuid.uuid4())
        
        # Validate enterprise
        enterprise = self.db.query(EnterpriseProfile).filter(
            EnterpriseProfile.id == enterprise_id
        ).first()
        
        if not enterprise:
            return {"success": False, "error": "Enterprise profile not found"}
        
        # Create configuration
        config = WhiteLabelConfig(
            config_id=config_id,
            enterprise_id=enterprise_id,
            domain=domain,
            brand_name=brand_name,
            logo_url=logo_url,
            primary_color=color_scheme.get("primary", "#3b82f6"),
            secondary_color=color_scheme.get("secondary", "#64748b"),
            accent_color=color_scheme.get("accent", "#10b981"),
            custom_css="",  # Would be built through UI
            custom_domain_settings={},
            feature_flags={
                "custom_branding": True,
                "private_labeling": True,
                "sso_integration": True,
                "api_access": True,
                "advanced_analytics": True
            },
            api_branding={},
            email_templates={},
            created_at=datetime.utcnow(),
            is_active=False
        )
        
        # Store configuration
        await self._store_white_label_config(config)
        
        # Generate custom CSS
        custom_css = await self._generate_custom_css(config)
        config.custom_css = custom_css
        
        await self._update_white_label_config(config)
        
        return {
            "success": True,
            "config_id": config_id,
            "status": "created",
            "preview_url": f"https://{domain}.brainai.com/preview"
        }
    
    async def get_white_label_preview(self, config_id: str) -> Dict[str, Any]:
        """Get white-label configuration preview"""
        
        config = await self._get_white_label_config(config_id)
        if not config:
            return {"success": False, "error": "Configuration not found"}
        
        return {
            "success": True,
            "preview": {
                "brand_name": config.brand_name,
                "logo_url": config.logo_url,
                "color_scheme": {
                    "primary": config.primary_color,
                    "secondary": config.secondary_color,
                    "accent": config.accent_color
                },
                "custom_css": config.custom_css,
                "domain": config.domain,
                "feature_flags": config.feature_flags
            }
        }
    
    async def activate_white_label_config(self, config_id: str) -> Dict[str, Any]:
        """Activate white-label configuration"""
        
        config = await self._get_white_label_config(config_id)
        if not config:
            return {"success": False, "error": "Configuration not found"}
        
        # Deactivate any existing configurations for this enterprise
        await self._deactivate_enterprise_configs(config.enterprise_id)
        
        # Activate this configuration
        config.is_active = True
        await self._update_white_label_config(config)
        
        # Apply configuration (would involve updating DNS, SSL, etc.)
        await self._apply_white_label_configuration(config)
        
        return {
            "success": True,
            "config_id": config_id,
            "status": "active",
            "domain": config.domain,
            "activation_time": datetime.utcnow().isoformat()
        }
    
    # Helper Methods
    async def _store_enterprise_team(self, team: EnterpriseTeam):
        """Store enterprise team"""
        self.active_teams[team.team_id] = team
    
    async def _get_enterprise_team(self, team_id: str) -> Optional[EnterpriseTeam]:
        """Get enterprise team by ID"""
        return self.active_teams.get(team_id)
    
    async def _update_enterprise_team(self, team: EnterpriseTeam):
        """Update enterprise team"""
        self.active_teams[team.team_id] = team
    
    async def _store_custom_curriculum(self, curriculum: CustomCurriculum):
        """Store custom curriculum"""
        self.custom_curricula[curriculum.curriculum_id] = curriculum
    
    async def _get_custom_curriculum(self, curriculum_id: str) -> Optional[CustomCurriculum]:
        """Get custom curriculum by ID"""
        return self.custom_curricula.get(curriculum_id)
    
    async def _update_custom_curriculum(self, curriculum: CustomCurriculum):
        """Update custom curriculum"""
        self.custom_curricula[curriculum.curriculum_id] = curriculum
    
    async def _store_white_label_config(self, config: WhiteLabelConfig):
        """Store white-label configuration"""
        self.white_label_configs[config.config_id] = config
    
    async def _get_white_label_config(self, config_id: str) -> Optional[WhiteLabelConfig]:
        """Get white-label configuration by ID"""
        return self.white_label_configs.get(config_id)
    
    async def _update_white_label_config(self, config: WhiteLabelConfig):
        """Update white-label configuration"""
        self.white_label_configs[config.config_id] = config
    
    # Database helper methods (would be implemented with proper models)
    async def _get_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """Get team member details"""
        return []  # Would query database
    
    async def _get_team_learning_progress(self, team_id: str) -> Dict[str, Any]:
        """Get team learning progress"""
        return {}  # Would query database
    
    async def _get_team_analytics(self, team_id: str, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get team analytics"""
        return {}  # Would query database
    
    async def _update_user_enterprise_profile(self, user_id: int, enterprise_id: int, role: TeamRole):
        """Update user enterprise profile"""
        pass  # Would update database
    
    async def _send_team_welcome_notification(self, user_id: int, team_id: str):
        """Send welcome notification to new team member"""
        pass  # Would send notification
    
    async def _get_enterprise_teams(self, enterprise_id: int) -> List[EnterpriseTeam]:
        """Get all teams for enterprise"""
        return [team for team in self.active_teams.values() if team.enterprise_id == enterprise_id]
    
    async def _get_enterprise_skill_assessments(self, enterprise_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get enterprise skill assessments"""
        return {}  # Would query database
    
    async def _calculate_business_impact(self, enterprise_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate business impact metrics"""
        return {
            "productivity_improvement": 15.0,
            "employee_retention": 92.0,
            "innovation_index": 8.5,
            "time_to_competency": 30.0
        }
    
    async def _calculate_roi_metrics(self, enterprise_id: int, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Calculate ROI metrics"""
        return {
            "training_roi": 3.5,
            "cost_per_learner": 2500.0,
            "revenue_impact": 150000.0,
            "savings": 75000.0
        }
    
    async def _get_analytics_trends(self, enterprise_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get analytics trends"""
        return {
            "enrollment_trend": [100, 120, 145, 180, 210],
            "completion_trend": [75, 82, 88, 91, 94],
            "engagement_trend": [6.5, 7.2, 7.8, 8.1, 8.4]
        }
    
    async def _get_top_performing_teams(self, enterprise_id: int) -> List[Dict[str, Any]]:
        """Get top performing teams"""
        return []  # Would query database
    
    async def _get_skill_gap_analysis(self, enterprise_id: int) -> Dict[str, Any]:
        """Get skill gap analysis"""
        return {
            "machine_learning": {"current": 65, "required": 85, "gap": 20},
            "data_science": {"current": 70, "required": 80, "gap": 10},
            "ai_engineering": {"current": 55, "required": 75, "gap": 20}
        }
    
    async def _get_enterprise_alerts(self, enterprise_id: int) -> List[Dict[str, Any]]:
        """Get enterprise alerts"""
        return [
            {
                "type": "warning",
                "message": "Team Alpha has low engagement this week",
                "action": "Schedule intervention call"
            }
        ]
    
    async def _get_analytics_recommendations(self, enterprise_id: int) -> List[str]:
        """Get analytics-based recommendations"""
        return [
            "Consider implementing peer learning for Team Beta",
            "Increase budget allocation for advanced AI courses",
            "Schedule follow-up training for recent hires"
        ]
    
    async def _deactivate_enterprise_configs(self, enterprise_id: int):
        """Deactivate existing white-label configurations"""
        for config in self.white_label_configs.values():
            if config.enterprise_id == enterprise_id:
                config.is_active = False
    
    async def _apply_white_label_configuration(self, config: WhiteLabelConfig):
        """Apply white-label configuration"""
        # Would handle DNS, SSL, CDN configuration, etc.
        pass
    
    async def _generate_custom_css(self, config: WhiteLabelConfig) -> str:
        """Generate custom CSS for white-label configuration"""
        return f"""
/* Custom White Label CSS for {config.brand_name} */
:root {{
    --primary-color: {config.primary_color};
    --secondary-color: {config.secondary_color};
    --accent-color: {config.accent_color};
}}

.brand-primary {{ color: var(--primary-color); }}
.bg-brand-primary {{ background-color: var(--primary-color); }}
.border-brand-primary {{ border-color: var(--primary-color); }}
"""