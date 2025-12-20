"""
Project Management Application with Brain AI Framework
Intelligent project planning, resource allocation, and progress tracking
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import os
import sys

# Add the brain_ai_framework to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain_ai_framework import BrainAI, MemoryNode, SparseActivation

class ProjectStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

@dataclass
class TeamMember:
    id: str
    name: str
    role: str
    skills: List[str]
    availability: float  # 0.0 to 1.0
    current_workload: float  # 0.0 to 1.0
    email: str

@dataclass
class Task:
    id: str
    title: str
    description: str
    assignee_id: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    estimated_hours: float
    actual_hours: float
    dependencies: List[str]
    created_at: datetime
    due_date: datetime
    completed_at: Optional[datetime]
    tags: List[str]

@dataclass
class Project:
    id: str
    name: str
    description: str
    status: ProjectStatus
    start_date: datetime
    end_date: datetime
    budget: float
    team_members: List[str]  # team member IDs
    tasks: List[str]  # task IDs
    milestones: List[Dict]
    progress: float  # 0.0 to 1.0
    risk_score: float  # 0.0 to 1.0
    created_at: datetime

class ProjectManagementSystem:
    def __init__(self):
        self.brain_ai = BrainAI(memory_capacity=10000)
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.team_members: Dict[str, TeamMember] = {}
        self.connections: List[WebSocket] = []
        
        # Initialize demo data
        self._initialize_demo_data()
        
        # Initialize AI patterns
        self._initialize_ai_patterns()

    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Demo team members
        demo_team = [
            TeamMember("tm1", "Alice Johnson", "Project Manager", ["leadership", "planning", "communication"], 1.0, 0.7, "alice@company.com"),
            TeamMember("tm2", "Bob Smith", "Senior Developer", ["python", "react", "aws"], 0.9, 0.8, "bob@company.com"),
            TeamMember("tm3", "Carol Davis", "UX Designer", ["figma", "user_research", "prototyping"], 1.0, 0.6, "carol@company.com"),
            TeamMember("tm4", "David Wilson", "DevOps Engineer", ["kubernetes", "docker", "ci_cd"], 0.8, 0.9, "david@company.com"),
            TeamMember("tm5", "Eva Rodriguez", "QA Engineer", ["testing", "automation", "bug_tracking"], 1.0, 0.5, "eva@company.com")
        ]
        
        for member in demo_team:
            self.team_members[member.id] = member
        
        # Demo project
        project = Project(
            id="proj1",
            name="E-Commerce Platform Redesign",
            description="Complete redesign of our e-commerce platform with modern UX/UI and improved performance",
            status=ProjectStatus.ACTIVE,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=60),
            budget=150000,
            team_members=["tm1", "tm2", "tm3", "tm4", "tm5"],
            tasks=[],
            milestones=[
                {"name": "Design Phase", "date": datetime.now() - timedelta(days=10), "completed": True},
                {"name": "Development Phase", "date": datetime.now() + timedelta(days=20), "completed": False},
                {"name": "Testing Phase", "date": datetime.now() + timedelta(days=40), "completed": False},
                {"name": "Launch", "date": datetime.now() + timedelta(days=60), "completed": False}
            ],
            progress=0.45,
            risk_score=0.3,
            created_at=datetime.now() - timedelta(days=30)
        )
        
        self.projects[project.id] = project
        
        # Demo tasks
        demo_tasks = [
            Task("task1", "User Research & Analysis", "Conduct comprehensive user research and competitive analysis", "tm3", TaskPriority.HIGH, TaskStatus.DONE, 40, 45, [], datetime.now() - timedelta(days=25), datetime.now() - timedelta(days=15), datetime.now() - timedelta(days=12), ["research", "analysis"]),
            Task("task2", "Design System Creation", "Create comprehensive design system with components", "tm3", TaskPriority.HIGH, TaskStatus.IN_PROGRESS, 60, 35, ["task1"], datetime.now() - timedelta(days=20), datetime.now() + timedelta(days=5), None, ["design", "components"]),
            Task("task3", "Backend API Development", "Develop RESTful APIs for user management and products", "tm2", TaskPriority.HIGH, TaskStatus.IN_PROGRESS, 120, 80, [], datetime.now() - timedelta(days=15), datetime.now() + timedelta(days=25), None, ["backend", "api"]),
            Task("task4", "Frontend Component Development", "Build React components for the new interface", "tm2", TaskPriority.MEDIUM, TaskStatus.TODO, 100, 0, ["task2", "task3"], datetime.now() - timedelta(days=10), datetime.now() + timedelta(days=30), None, ["frontend", "react"]),
            Task("task5", "Infrastructure Setup", "Set up CI/CD pipeline and cloud infrastructure", "tm4", TaskPriority.MEDIUM, TaskStatus.IN_PROGRESS, 80, 60, [], datetime.now() - timedelta(days=12), datetime.now() + timedelta(days=15), None, ["devops", "infrastructure"]),
            Task("task6", "Quality Assurance Testing", "Comprehensive testing of all system components", "tm5", TaskPriority.HIGH, TaskStatus.TODO, 80, 0, ["task4"], datetime.now() + timedelta(days=5), datetime.now() + timedelta(days=45), None, ["testing", "qa"]),
            Task("task7", "Performance Optimization", "Optimize application performance and load times", "tm2", TaskPriority.LOW, TaskStatus.TODO, 40, 0, ["task4"], datetime.now() + timedelta(days=10), datetime.now() + timedelta(days=50), None, ["performance", "optimization"])
        ]
        
        for task in demo_tasks:
            self.tasks[task.id] = task
        
        project.tasks = [task.id for task in demo_tasks]

    def _initialize_ai_patterns(self):
        """Initialize AI learning patterns for project management"""
        # Pattern: Resource allocation based on skills and workload
        self.brain_ai.learn(
            "resource_allocation_pattern",
            "When allocating tasks, consider team member skills match, current workload, and availability. High-priority tasks should go to available high-skill members.",
            importance=0.9
        )
        
        # Pattern: Risk assessment based on task dependencies and deadlines
        self.brain_ai.learn(
            "risk_assessment_pattern", 
            "Projects with many dependencies, tight deadlines, and high task complexity have elevated risk scores. Monitor blocked tasks and deadline pressure.",
            importance=0.8
        )
        
        # Pattern: Progress tracking and prediction
        self.brain_ai.learn(
            "progress_prediction_pattern",
            "Project progress can be predicted by analyzing completed vs planned tasks, team velocity, and milestone achievement. Account for resource constraints.",
            importance=0.7
        )

    async def analyze_resource_allocation(self, project_id: str) -> Dict[str, Any]:
        """Analyze resource allocation using Brain AI"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Collect current allocation data
        allocation_data = {
            "team_size": len(project.team_members),
            "skills_coverage": {},
            "workload_distribution": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Analyze skills coverage
        all_skills = set()
        for member_id in project.team_members:
            member = self.team_members.get(member_id)
            if member:
                all_skills.update(member.skills)
                allocation_data["skills_coverage"][member_id] = member.skills
        
        # Analyze workload distribution
        for member_id in project.team_members:
            member = self.team_members.get(member_id)
            if member:
                allocation_data["workload_distribution"][member_id] = {
                    "current_workload": member.current_workload,
                    "availability": member.availability,
                    "effective_capacity": member.availability * (1 - member.current_workload)
                }
        
        # Identify bottlenecks (high workload + critical skills)
        for member_id in project.team_members:
            member = self.team_members.get(member_id)
            if member and member.current_workload > 0.8:
                allocation_data["bottlenecks"].append({
                    "member_id": member_id,
                    "member_name": member.name,
                    "workload": member.current_workload,
                    "skills": member.skills
                })
        
        # Generate AI recommendations
        prompt = f"""
        Analyze this project resource allocation:
        Team size: {allocation_data['team_size']}
        Bottlenecks: {len(allocation_data['bottlenecks'])}
        Skills coverage: {len(allocation_data['skills_coverage'])}
        
        Provide recommendations for optimizing resource allocation.
        Consider workload balancing, skills matching, and capacity planning.
        """
        
        ai_response = await self.brain_ai.think(prompt, context="resource_allocation_pattern")
        
        allocation_data["ai_analysis"] = ai_response
        allocation_data["recommendations"].extend(ai_response.get("recommendations", []))
        
        return allocation_data

    async def predict_project_risks(self, project_id: str) -> Dict[str, Any]:
        """Predict project risks using Brain AI"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        risk_analysis = {
            "current_risk_score": project.risk_score,
            "risk_factors": [],
            "timeline_risks": [],
            "resource_risks": [],
            "technical_risks": [],
            "mitigation_strategies": [],
            "predictions": {}
        }
        
        # Analyze timeline risks
        now = datetime.now()
        days_remaining = (project.end_date - now).days
        tasks_remaining = len([t for t in project.tasks if self.tasks.get(t) and self.tasks[t].status != TaskStatus.DONE])
        
        if days_remaining < 0:
            risk_analysis["timeline_risks"].append("Project is past deadline")
        elif tasks_remaining > 0 and days_remaining < 7:
            risk_analysis["timeline_risks"].append("Very tight deadline with remaining tasks")
        
        # Analyze resource risks
        allocation_data = await self.analyze_resource_allocation(project_id)
        if allocation_data["bottlenecks"]:
            risk_analysis["resource_risks"].append("Team member bottlenecks identified")
        
        # Analyze task dependencies
        dependency_risks = 0
        for task_id in project.tasks:
            task = self.tasks.get(task_id)
            if task and len(task.dependencies) > 2:
                dependency_risks += 1
        
        if dependency_risks > len(project.tasks) * 0.3:
            risk_analysis["technical_risks"].append("High task dependency complexity")
        
        # Generate AI risk prediction
        risk_context = f"""
        Project: {project.name}
        Status: {project.status.value}
        Days remaining: {days_remaining}
        Tasks remaining: {tasks_remaining}
        Current progress: {project.progress:.1%}
        Resource bottlenecks: {len(allocation_data['bottlenecks'])}
        """
        
        ai_response = await self.brain_ai.think(
            f"Analyze project risks for: {risk_context}",
            context="risk_assessment_pattern"
        )
        
        risk_analysis["ai_analysis"] = ai_response
        risk_analysis["predictions"] = ai_response.get("predictions", {})
        risk_analysis["mitigation_strategies"] = ai_response.get("mitigation_strategies", [])
        
        return risk_analysis

    async def optimize_project_schedule(self, project_id: str) -> Dict[str, Any]:
        """Optimize project schedule using Brain AI"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        schedule_data = {
            "critical_path": [],
            "resource_conflicts": [],
            "schedule_optimizations": [],
            "milestone_analysis": {},
            "recommendations": []
        }
        
        # Analyze critical path (simplified)
        incomplete_tasks = []
        for task_id in project.tasks:
            task = self.tasks.get(task_id)
            if task and task.status != TaskStatus.DONE:
                incomplete_tasks.append(task)
        
        # Sort by due date to identify potential critical path
        incomplete_tasks.sort(key=lambda t: t.due_date)
        schedule_data["critical_path"] = [task.id for task in incomplete_tasks[:5]]
        
        # Analyze milestone progress
        for milestone in project.milestones:
            days_until = (milestone["date"] - datetime.now()).days
            schedule_data["milestone_analysis"][milestone["name"]] = {
                "days_until": days_until,
                "on_track": days_until >= 0 and not milestone["completed"],
                "status": "completed" if milestone["completed"] else "upcoming"
            }
        
        # Generate AI schedule optimization
        prompt = f"""
        Optimize project schedule for: {project.name}
        Tasks remaining: {len(incomplete_tasks)}
        Critical path: {len(schedule_data['critical_path'])} tasks
        End date: {project.end_date.strftime('%Y-%m-%d')}
        
        Provide schedule optimization recommendations considering dependencies, resources, and deadlines.
        """
        
        ai_response = await self.brain_ai.think(prompt, context="progress_prediction_pattern")
        
        schedule_data["ai_analysis"] = ai_response
        schedule_data["schedule_optimizations"] = ai_response.get("optimizations", [])
        schedule_data["recommendations"] = ai_response.get("recommendations", [])
        
        return schedule_data

    async def get_team_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive team performance analytics"""
        analytics = {
            "team_overview": {},
            "productivity_metrics": {},
            "skill_distribution": {},
            "workload_analysis": {},
            "performance_predictions": {}
        }
        
        # Team overview
        total_members = len(self.team_members)
        avg_workload = sum(m.current_workload for m in self.team_members.values()) / total_members
        avg_availability = sum(m.availability for m in self.team_members.values()) / total_members
        
        analytics["team_overview"] = {
            "total_members": total_members,
            "average_workload": avg_workload,
            "average_availability": avg_availability,
            "utilization_rate": avg_workload / avg_availability if avg_availability > 0 else 0
        }
        
        # Skill distribution
        skill_counts = {}
        for member in self.team_members.values():
            for skill in member.skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        analytics["skill_distribution"] = skill_counts
        
        # Workload analysis
        workload_categories = {"low": 0, "medium": 0, "high": 0, "overloaded": 0}
        for member in self.team_members.values():
            workload = member.current_workload
            if workload < 0.3:
                workload_categories["low"] += 1
            elif workload < 0.6:
                workload_categories["medium"] += 1
            elif workload < 0.9:
                workload_categories["high"] += 1
            else:
                workload_categories["overloaded"] += 1
        
        analytics["workload_analysis"] = workload_categories
        
        # Generate AI performance predictions
        prompt = f"""
        Analyze team performance with:
        Total members: {total_members}
        Average workload: {avg_workload:.2f}
        Average availability: {avg_availability:.2f}
        Utilization rate: {analytics['team_overview']['utilization_rate']:.2f}
        Skill distribution: {skill_counts}
        
        Provide performance predictions and recommendations.
        """
        
        ai_response = await self.brain_ai.think(prompt, context="resource_allocation_pattern")
        analytics["ai_analysis"] = ai_response
        analytics["performance_predictions"] = ai_response.get("predictions", {})
        
        return analytics

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        dashboard = {
            "projects_summary": {},
            "tasks_summary": {},
            "team_summary": {},
            "recent_activity": [],
            "upcoming_deadlines": [],
            "ai_insights": {}
        }
        
        # Projects summary
        total_projects = len(self.projects)
        active_projects = len([p for p in self.projects.values() if p.status == ProjectStatus.ACTIVE])
        completed_projects = len([p for p in self.projects.values() if p.status == ProjectStatus.COMPLETED])
        
        dashboard["projects_summary"] = {
            "total": total_projects,
            "active": active_projects,
            "completed": completed_projects,
            "on_hold": len([p for p in self.projects.values() if p.status == ProjectStatus.ON_HOLD])
        }
        
        # Tasks summary
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.DONE])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        
        dashboard["tasks_summary"] = {
            "total": total_tasks,
            "completed": completed_tasks,
            "in_progress": in_progress_tasks,
            "todo": len([t for t in self.tasks.values() if t.status == TaskStatus.TODO]),
            "blocked": len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED])
        }
        
        # Team summary
        dashboard["team_summary"] = {
            "total_members": len(self.team_members),
            "average_workload": sum(m.current_workload for m in self.team_members.values()) / len(self.team_members),
            "skills_coverage": len(set(skill for member in self.team_members.values() for skill in member.skills))
        }
        
        # Upcoming deadlines (next 7 days)
        now = datetime.now()
        upcoming_tasks = [t for t in self.tasks.values() if 
                         t.due_date <= now + timedelta(days=7) and 
                         t.status != TaskStatus.DONE]
        upcoming_tasks.sort(key=lambda t: t.due_date)
        
        dashboard["upcoming_deadlines"] = [
            {
                "task_id": task.id,
                "title": task.title,
                "assignee": self.team_members.get(task.assignee_id, {}).name if task.assignee_id else "Unassigned",
                "due_date": task.due_date.isoformat(),
                "priority": task.priority.name
            }
            for task in upcoming_tasks[:10]
        ]
        
        # Generate AI insights
        prompt = f"""
        Generate project management insights:
        Projects: {dashboard['projects_summary']}
        Tasks: {dashboard['tasks_summary']}
        Team: {dashboard['team_summary']}
        
        Provide actionable insights and recommendations for improving project outcomes.
        """
        
        ai_response = await self.brain_ai.think(prompt)
        dashboard["ai_insights"] = ai_response
        
        return dashboard

    async def create_task(self, task_data: Dict) -> Task:
        """Create a new task with AI analysis"""
        task = Task(
            id=str(uuid.uuid4()),
            title=task_data["title"],
            description=task_data["description"],
            assignee_id=task_data.get("assignee_id"),
            priority=TaskPriority(task_data["priority"]),
            status=TaskStatus.TODO,
            estimated_hours=task_data["estimated_hours"],
            actual_hours=0,
            dependencies=task_data.get("dependencies", []),
            created_at=datetime.now(),
            due_date=datetime.fromisoformat(task_data["due_date"]),
            completed_at=None,
            tags=task_data.get("tags", [])
        )
        
        self.tasks[task.id] = task
        
        # Learn from task creation pattern
        self.brain_ai.learn(
            f"task_creation_{task.id}",
            f"Created task '{task.title}' with priority {task.priority.name}, estimated {task.estimated_hours} hours",
            importance=0.6
        )
        
        return task

    async def update_task_status(self, task_id: str, status: TaskStatus, actual_hours: Optional[float] = None) -> Task:
        """Update task status with AI analysis"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        old_status = task.status
        task.status = status
        
        if actual_hours is not None:
            task.actual_hours = actual_hours
        
        if status == TaskStatus.DONE:
            task.completed_at = datetime.now()
        
        # Learn from status change pattern
        self.brain_ai.learn(
            f"task_status_change_{task_id}",
            f"Task '{task.title}' changed from {old_status.value} to {status.value}",
            importance=0.7
        )
        
        return task

    async def assign_task(self, task_id: str, assignee_id: str) -> Task:
        """Assign task to team member with AI recommendation"""
        task = self.tasks.get(task_id)
        assignee = self.team_members.get(assignee_id)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        if not assignee:
            raise ValueError(f"Assignee {assignee_id} not found")
        
        task.assignee_id = assignee_id
        
        # Learn from assignment pattern
        self.brain_ai.learn(
            f"task_assignment_{task_id}",
            f"Task '{task.title}' assigned to {assignee.name} with skills {assignee.skills}",
            importance=0.6
        )
        
        return task

    # WebSocket connection management
    async def connect_websocket(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect_websocket(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast_update(self, message: str, data: Any = None):
        """Broadcast update to all connected clients"""
        update = {
            "type": "update",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        disconnected = []
        for connection in self.connections:
            try:
                await connection.send_json(update)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect_websocket(connection)

# Initialize the system
project_mgmt = ProjectManagementSystem()

# FastAPI application
app = FastAPI(title="Project Management with Brain AI", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Management - Brain AI</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #2d3748;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #4a5568;
            text-align: center;
            font-size: 1.1rem;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #2d3748;
            font-size: 1.4rem;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .stat {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .stat:last-child {
            border-bottom: none;
        }
        
        .stat-label {
            color: #4a5568;
            font-weight: 500;
        }
        
        .stat-value {
            color: #2d3748;
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .ai-insights {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            grid-column: span 2;
        }
        
        .ai-insights h3 {
            color: white;
        }
        
        .insight-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .insight-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .insight-content {
            opacity: 0.9;
            line-height: 1.5;
        }
        
        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .action-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
            display: block;
        }
        
        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .progress-bar {
            background: #e2e8f0;
            border-radius: 10px;
            height: 8px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 10px;
            transition: width 0.3s ease;
        }
        
        .priority-badge {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .priority-low { background: #48bb78; color: white; }
        .priority-medium { background: #ed8936; color: white; }
        .priority-high { background: #f56565; color: white; }
        .priority-critical { background: #9f7aea; color: white; }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-todo { background: #a0aec0; }
        .status-in-progress { background: #4299e1; }
        .status-review { background: #ed8936; }
        .status-done { background: #48bb78; }
        .status-blocked { background: #f56565; }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .ai-insights {
                grid-column: span 1;
            }
            
            .actions-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Project Management with Brain AI</h1>
            <p>Intelligent project planning, resource allocation, and progress tracking</p>
        </div>
        
        <div class="dashboard-grid" id="dashboard">
            <div class="card">
                <h3>📊 Projects Overview</h3>
                <div class="stat">
                    <span class="stat-label">Total Projects</span>
                    <span class="stat-value" id="total-projects">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Active Projects</span>
                    <span class="stat-value" id="active-projects">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Completed Projects</span>
                    <span class="stat-value" id="completed-projects">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">On Hold</span>
                    <span class="stat-value" id="on-hold-projects">-</span>
                </div>
            </div>
            
            <div class="card">
                <h3>✅ Tasks Overview</h3>
                <div class="stat">
                    <span class="stat-label">Total Tasks</span>
                    <span class="stat-value" id="total-tasks">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Completed</span>
                    <span class="stat-value" id="completed-tasks">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">In Progress</span>
                    <span class="stat-value" id="in-progress-tasks">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Blocked</span>
                    <span class="stat-value" id="blocked-tasks">-</span>
                </div>
            </div>
            
            <div class="card">
                <h3>👥 Team Overview</h3>
                <div class="stat">
                    <span class="stat-label">Team Members</span>
                    <span class="stat-value" id="team-members">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Average Workload</span>
                    <span class="stat-value" id="avg-workload">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Skills Coverage</span>
                    <span class="stat-value" id="skills-coverage">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Utilization Rate</span>
                    <span class="stat-value" id="utilization-rate">-</span>
                </div>
            </div>
            
            <div class="ai-insights card">
                <h3>🧠 AI Insights & Recommendations</h3>
                <div id="ai-insights">
                    <div class="insight-item">
                        <div class="insight-title">Loading AI Analysis...</div>
                        <div class="insight-content">Brain AI is analyzing project patterns and generating insights...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>⏰ Upcoming Deadlines</h3>
            <div id="upcoming-deadlines">
                <p>Loading upcoming deadlines...</p>
            </div>
        </div>
        
        <div class="actions-grid">
            <a href="#" class="action-btn" onclick="showResourceAllocation()">📋 Resource Allocation Analysis</a>
            <a href="#" class="action-btn" onclick="showRiskAnalysis()">⚠️ Risk Assessment</a>
            <a href="#" class="action-btn" onclick="showScheduleOptimization()">📅 Schedule Optimization</a>
            <a href="#" class="action-btn" onclick="showTeamAnalytics()">📈 Team Performance Analytics</a>
            <a href="#" class="action-btn" onclick="createNewTask()">➕ Create New Task</a>
            <a href="#" class="action-btn" onclick="viewAllProjects()">📁 View All Projects</a>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'update') {
                console.log('Update received:', data);
                loadDashboard();
            }
        };
        
        ws.onclose = function() {
            console.log('WebSocket connection closed');
        };
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                // Update projects overview
                document.getElementById('total-projects').textContent = data.projects_summary.total;
                document.getElementById('active-projects').textContent = data.projects_summary.active;
                document.getElementById('completed-projects').textContent = data.projects_summary.completed;
                document.getElementById('on-hold-projects').textContent = data.projects_summary.on_hold;
                
                // Update tasks overview
                document.getElementById('total-tasks').textContent = data.tasks_summary.total;
                document.getElementById('completed-tasks').textContent = data.tasks_summary.completed;
                document.getElementById('in-progress-tasks').textContent = data.tasks_summary.in_progress;
                document.getElementById('blocked-tasks').textContent = data.tasks_summary.blocked;
                
                // Update team overview
                document.getElementById('team-members').textContent = data.team_summary.total_members;
                document.getElementById('avg-workload').textContent = (data.team_summary.average_workload * 100).toFixed(0) + '%';
                document.getElementById('skills-coverage').textContent = data.team_summary.skills_coverage;
                
                // Calculate utilization rate
                const utilization = (data.team_summary.average_workload * 100).toFixed(0);
                document.getElementById('utilization-rate').textContent = utilization + '%';
                
                // Update AI insights
                updateAIInsights(data.ai_insights);
                
                // Update upcoming deadlines
                updateUpcomingDeadlines(data.upcoming_deadlines);
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        function updateAIInsights(aiInsights) {
            const container = document.getElementById('ai-insights');
            
            if (aiInsights && aiInsights.summary) {
                container.innerHTML = '';
                
                const insightItem = document.createElement('div');
                insightItem.className = 'insight-item';
                insightItem.innerHTML = `
                    <div class="insight-title">AI Analysis Summary</div>
                    <div class="insight-content">${aiInsights.summary}</div>
                `;
                container.appendChild(insightItem);
                
                if (aiInsights.recommendations && aiInsights.recommendations.length > 0) {
                    aiInsights.recommendations.forEach(rec => {
                        const recItem = document.createElement('div');
                        recItem.className = 'insight-item';
                        recItem.innerHTML = `
                            <div class="insight-title">Recommendation</div>
                            <div class="insight-content">${rec}</div>
                        `;
                        container.appendChild(recItem);
                    });
                }
            } else {
                container.innerHTML = `
                    <div class="insight-item">
                        <div class="insight-title">AI Analysis</div>
                        <div class="insight-content">Generating insights...</div>
                    </div>
                `;
            }
        }
        
        function updateUpcomingDeadlines(deadlines) {
            const container = document.getElementById('upcoming-deadlines');
            
            if (deadlines && deadlines.length > 0) {
                container.innerHTML = '';
                
                deadlines.forEach(deadline => {
                    const deadlineItem = document.createElement('div');
                    deadlineItem.className = 'deadline-item';
                    deadlineItem.style.cssText = 'padding: 10px 0; border-bottom: 1px solid #e2e8f0;';
                    
                    const dueDate = new Date(deadline.due_date);
                    const daysUntil = Math.ceil((dueDate - new Date()) / (1000 * 60 * 60 * 24));
                    
                    deadlineItem.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>${deadline.title}</strong><br>
                                <small>Assigned to: ${deadline.assignee}</small>
                            </div>
                            <div style="text-align: right;">
                                <span class="priority-badge priority-${deadline.priority.toLowerCase()}">${deadline.priority}</span><br>
                                <small>${daysUntil} days remaining</small>
                            </div>
                        </div>
                    `;
                    container.appendChild(deadlineItem);
                });
            } else {
                container.innerHTML = '<p>No upcoming deadlines in the next 7 days.</p>';
            }
        }
        
        // Action functions
        async function showResourceAllocation() {
            const response = await fetch('/api/resource-allocation/proj1');
            const data = await response.json();
            alert('Resource Allocation Analysis:\\n\\n' + JSON.stringify(data, null, 2));
        }
        
        async function showRiskAnalysis() {
            const response = await fetch('/api/risk-analysis/proj1');
            const data = await response.json();
            alert('Risk Analysis:\\n\\n' + JSON.stringify(data, null, 2));
        }
        
        async function showScheduleOptimization() {
            const response = await fetch('/api/schedule-optimization/proj1');
            const data = await response.json();
            alert('Schedule Optimization:\\n\\n' + JSON.stringify(data, null, 2));
        }
        
        async function showTeamAnalytics() {
            const response = await fetch('/api/team-analytics');
            const data = await response.json();
            alert('Team Performance Analytics:\\n\\n' + JSON.stringify(data, null, 2));
        }
        
        function createNewTask() {
            alert('Task creation feature would open a modal or new page with form fields.');
        }
        
        function viewAllProjects() {
            alert('Project list view would display all projects with detailed information.');
        }
        
        // Load dashboard on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
            
            // Refresh dashboard every 30 seconds
            setInterval(loadDashboard, 30000);
        });
    </script>
</body>
</html>
    """

@app.get("/api/dashboard")
async def get_dashboard():
    """Get dashboard data"""
    try:
        data = await project_mgmt.get_dashboard_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resource-allocation/{project_id}")
async def get_resource_allocation(project_id: str):
    """Get resource allocation analysis"""
    try:
        data = await project_mgmt.analyze_resource_allocation(project_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-analysis/{project_id}")
async def get_risk_analysis(project_id: str):
    """Get risk analysis"""
    try:
        data = await project_mgmt.predict_project_risks(project_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/schedule-optimization/{project_id}")
async def get_schedule_optimization(project_id: str):
    """Get schedule optimization"""
    try:
        data = await project_mgmt.optimize_project_schedule(project_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/team-analytics")
async def get_team_analytics():
    """Get team performance analytics"""
    try:
        data = await project_mgmt.get_team_performance_analytics()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
async def get_projects():
    """Get all projects"""
    projects_data = []
    for project in project_mgmt.projects.values():
        projects_data.append(asdict(project))
    return projects_data

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get specific project"""
    project = project_mgmt.projects.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return asdict(project)

@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks"""
    tasks_data = []
    for task in project_mgmt.tasks.values():
        task_dict = asdict(task)
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['due_date'] = task.due_date.isoformat()
        if task.completed_at:
            task_dict['completed_at'] = task.completed_at.isoformat()
        tasks_data.append(task_dict)
    return tasks_data

@app.get("/api/team")
async def get_team():
    """Get team members"""
    team_data = []
    for member in project_mgmt.team_members.values():
        team_data.append(asdict(member))
    return team_data

@app.post("/api/tasks")
async def create_task_endpoint(task_data: dict):
    """Create new task"""
    try:
        task = await project_mgmt.create_task(task_data)
        task_dict = asdict(task)
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['due_date'] = task.due_date.isoformat()
        
        await project_mgmt.broadcast_update("New task created", {"task": task_dict})
        return task_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{task_id}/status")
async def update_task_status_endpoint(task_id: str, status_data: dict):
    """Update task status"""
    try:
        status = TaskStatus(status_data["status"])
        actual_hours = status_data.get("actual_hours")
        
        task = await project_mgmt.update_task_status(task_id, status, actual_hours)
        task_dict = asdict(task)
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['due_date'] = task.due_date.isoformat()
        if task.completed_at:
            task_dict['completed_at'] = task.completed_at.isoformat()
        
        await project_mgmt.broadcast_update("Task status updated", {"task": task_dict})
        return task_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tasks/{task_id}/assign")
async def assign_task_endpoint(task_id: str, assignment_data: dict):
    """Assign task to team member"""
    try:
        assignee_id = assignment_data["assignee_id"]
        task = await project_mgmt.assign_task(task_id, assignee_id)
        task_dict = asdict(task)
        task_dict['created_at'] = task.created_at.isoformat()
        task_dict['due_date'] = task.due_date.isoformat()
        if task.completed_at:
            task_dict['completed_at'] = task.completed_at.isoformat()
        
        await project_mgmt.broadcast_update("Task assigned", {"task": task_dict})
        return task_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await project_mgmt.connect_websocket(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        project_mgmt.disconnect_websocket(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "project-management-brain-ai"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)