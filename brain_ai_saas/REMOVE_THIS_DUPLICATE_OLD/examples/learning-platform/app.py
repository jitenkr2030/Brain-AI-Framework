#!/usr/bin/env python3
"""
Learning Platform System - Brain AI Example
Intelligent adaptive learning and skill development platform
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainAI:
    """Brain AI Framework - Learning Platform Core"""
    
    def __init__(self):
        self.learner_profiles = {}
        self.course_content = {}
        self.learning_paths = {}
        self.assessment_data = {}
        self.knowledge_graph = {}
        self.learning_analytics = {}
        self.adaptive_algorithms = {}
        self.content_recommendations = {}
        
    async def create_learner_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and analyze learner profile"""
        learner_id = str(uuid.uuid4())
        
        # Extract learning preferences
        learning_style = await self._analyze_learning_style(profile_data)
        skill_assessment = await self._assess_current_skills(profile_data)
        learning_goals = await self._extract_learning_goals(profile_data)
        learning_history = await self._analyze_learning_history(profile_data)
        
        # Calculate learning readiness
        readiness_score = await self._calculate_learning_readiness(
            profile_data, learning_style, skill_assessment
        )
        
        # Create learner profile
        learner_profile = {
            "id": learner_id,
            "basic_info": {
                "name": profile_data.get("name", ""),
                "email": profile_data.get("email", ""),
                "role": profile_data.get("role", ""),
                "experience_years": profile_data.get("experience_years", 0)
            },
            "learning_profile": {
                "learning_style": learning_style,
                "current_skills": skill_assessment,
                "learning_goals": learning_goals,
                "learning_history": learning_history,
                "readiness_score": readiness_score,
                "preferred_pace": profile_data.get("preferred_pace", "moderate"),
                "available_time": profile_data.get("available_time", 10),  # hours per week
                "learning_method": profile_data.get("learning_method", "mixed")
            },
            "progress": {
                "total_courses_completed": 0,
                "total_learning_time": 0,
                "skills_acquired": [],
                "certifications_earned": [],
                "current_streak": 0,
                "longest_streak": 0
            },
            "preferences": {
                "content_types": profile_data.get("content_types", ["videos", "articles"]),
                "difficulty_preference": profile_data.get("difficulty_preference", "progressive"),
                "feedback_frequency": profile_data.get("feedback_frequency", "weekly"),
                "collaboration_preference": profile_data.get("collaboration_preference", "optional")
            },
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Store learner profile
        self.learner_profiles[learner_id] = learner_profile
        
        # Update learning analytics
        await self._update_learning_analytics(learner_profile)
        
        # Generate initial recommendations
        await self._generate_initial_recommendations(learner_id)
        
        return learner_profile
    
    async def _analyze_learning_style(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learner's preferred learning style"""
        # Simulate learning style assessment
        visual_score = random.uniform(0.3, 0.9)
        auditory_score = random.uniform(0.3, 0.9)
        kinesthetic_score = random.uniform(0.3, 0.9)
        reading_writing_score = random.uniform(0.3, 0.9)
        
        # Determine dominant style
        scores = {
            "visual": visual_score,
            "auditory": auditory_score,
            "kinesthetic": kinesthetic_score,
            "reading_writing": reading_writing_score
        }
        
        dominant_style = max(scores, key=scores.get)
        
        return {
            "primary_style": dominant_style,
            "scores": scores,
            "description": f"Learns best through {dominant_style.replace('_', ' ')} methods",
            "recommended_content": self._get_content_recommendations(dominant_style),
            "adaptation_level": random.choice(["beginner", "intermediate", "advanced"])
        }
    
    def _get_content_recommendations(self, learning_style: str) -> List[str]:
        """Get content recommendations based on learning style"""
        recommendations = {
            "visual": ["infographics", "diagrams", "videos", "mind maps", "color-coded notes"],
            "auditory": ["podcasts", "audio lectures", "discussions", "verbal explanations", "music cues"],
            "kinesthetic": ["hands-on projects", "simulations", "labs", "interactive exercises", "real-world practice"],
            "reading_writing": ["textbooks", "articles", "written notes", "essays", "documentation"]
        }
        
        return recommendations.get(learning_style, ["mixed media"])
    
    async def _assess_current_skills(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess learner's current skill levels"""
        skill_categories = {
            "technical_skills": profile_data.get("technical_skills", []),
            "soft_skills": profile_data.get("soft_skills", []),
            "domain_knowledge": profile_data.get("domain_knowledge", []),
            "tools_proficiency": profile_data.get("tools_proficiency", [])
        }
        
        assessed_skills = {}
        
        for category, skills in skill_categories.items():
            assessed_skills[category] = []
            for skill in skills:
                # Simulate skill level assessment
                level = random.choice(["beginner", "intermediate", "advanced", "expert"])
                confidence = random.uniform(0.6, 0.95)
                last_used = random.choice(["recently", "few_months_ago", "over_a_year_ago"])
                
                assessed_skills[category].append({
                    "skill": skill,
                    "level": level,
                    "confidence": confidence,
                    "last_used": last_used,
                    "needs_improvement": level in ["beginner", "intermediate"]
                })
        
        return assessed_skills
    
    async def _extract_learning_goals(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and categorize learning goals"""
        goals = []
        
        # Extract from provided goals
        provided_goals = profile_data.get("learning_goals", [])
        for goal in provided_goals:
            goals.append({
                "goal": goal,
                "category": self._categorize_goal(goal),
                "priority": random.choice(["high", "medium", "low"]),
                "timeline": random.choice(["immediate", "short_term", "long_term"]),
                "measurable": True
            })
        
        # Generate goals based on role and experience
        role = profile_data.get("role", "").lower()
        experience_years = profile_data.get("experience_years", 0)
        
        if "developer" in role:
            goals.extend([
                {"goal": "Master advanced programming concepts", "category": "technical", "priority": "high", "timeline": "short_term"},
                {"goal": "Learn new programming languages", "category": "technical", "priority": "medium", "timeline": "long_term"}
            ])
        elif "manager" in role:
            goals.extend([
                {"goal": "Improve leadership skills", "category": "leadership", "priority": "high", "timeline": "ongoing"},
                {"goal": "Enhance team management capabilities", "category": "management", "priority": "high", "timeline": "short_term"}
            ])
        
        return goals
    
    def _categorize_goal(self, goal: str) -> str:
        """Categorize learning goal"""
        goal_lower = goal.lower()
        
        if any(word in goal_lower for word in ["technical", "programming", "development", "coding"]):
            return "technical"
        elif any(word in goal_lower for word in ["leadership", "management", "team"]):
            return "leadership"
        elif any(word in goal_lower for word in ["communication", "presentation", "writing"]):
            return "communication"
        elif any(word in goal_lower for word in ["data", "analysis", "analytics"]):
            return "analytical"
        else:
            return "general"
    
    async def _analyze_learning_history(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learner's past learning experiences"""
        courses_completed = profile_data.get("courses_completed", [])
        certifications = profile_data.get("certifications", [])
        
        learning_patterns = {
            "completion_rate": random.uniform(0.6, 0.95),
            "preferred_time": random.choice(["morning", "afternoon", "evening", "night"]),
            "session_duration": random.choice([15, 30, 60, 120]),  # minutes
            "break_frequency": random.choice([30, 60, 120]),  # minutes
            "difficulty_progression": random.choice(["gradual", "steady", "challenging"]),
            "engagement_factors": ["practical_examples", "real_world_applications", "peer_interaction"]
        }
        
        return {
            "courses_completed": courses_completed,
            "certifications": certifications,
            "patterns": learning_patterns,
            "success_factors": self._identify_success_factors(learning_patterns),
            "struggle_areas": self._identify_struggle_areas(learning_patterns)
        }
    
    def _identify_success_factors(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify factors that contribute to learner's success"""
        factors = []
        
        if patterns["completion_rate"] > 0.8:
            factors.append("High course completion rate indicates strong motivation")
        
        if patterns["session_duration"] >= 60:
            factors.append("Can maintain focus for extended periods")
        
        if patterns["difficulty_progression"] == "gradual":
            factors.append("Benefits from progressive difficulty increases")
        
        return factors
    
    def _identify_struggle_areas(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify potential areas of difficulty"""
        struggles = []
        
        if patterns["completion_rate"] < 0.7:
            struggles.append("May benefit from shorter, more focused sessions")
        
        if patterns["session_duration"] < 30:
            struggles.append("Prefers shorter learning sessions")
        
        if patterns["difficulty_progression"] == "challenging":
            struggles.append("May need additional support for difficult concepts")
        
        return struggles
    
    async def _calculate_learning_readiness(self, profile_data: Dict[str, Any], 
                                          learning_style: Dict[str, Any],
                                          skill_assessment: Dict[str, Any]) -> float:
        """Calculate learner's readiness for new learning"""
        readiness = 0.0
        
        # Motivation factor (30%)
        goals = profile_data.get("learning_goals", [])
        if goals:
            readiness += 0.3
        
        # Time availability (25%)
        available_time = profile_data.get("available_time", 0)
        if available_time >= 10:  # 10+ hours per week
            readiness += 0.25
        elif available_time >= 5:
            readiness += 0.15
        
        # Experience foundation (20%)
        experience_years = profile_data.get("experience_years", 0)
        if experience_years > 0:
            readiness += min(experience_years * 0.02, 0.2)
        
        # Learning style clarity (15%)
        style_score = max(learning_style["scores"].values())
        if style_score > 0.7:
            readiness += 0.15
        
        # Past success (10%)
        courses_completed = len(profile_data.get("courses_completed", []))
        if courses_completed > 0:
            readiness += 0.1
        
        return min(readiness, 1.0)
    
    async def create_learning_path(self, path_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized learning path"""
        path_id = str(uuid.uuid4())
        learner_id = path_data.get("learner_id")
        
        if learner_id not in self.learner_profiles:
            raise ValueError("Learner not found")
        
        learner_profile = self.learner_profiles[learner_id]
        
        # Analyze learning objectives
        objectives = await self._analyze_learning_objectives(path_data["objectives"])
        
        # Design optimal learning sequence
        learning_sequence = await self._design_learning_sequence(
            learner_profile, objectives
        )
        
        # Calculate path metrics
        path_metrics = await self._calculate_path_metrics(
            learner_profile, learning_sequence
        )
        
        # Create learning path
        learning_path = {
            "id": path_id,
            "learner_id": learner_id,
            "title": path_data.get("title", "Personalized Learning Path"),
            "description": path_data.get("description", ""),
            "objectives": objectives,
            "learning_sequence": learning_sequence,
            "estimated_duration": path_metrics["estimated_duration"],
            "difficulty_progression": path_metrics["difficulty_progression"],
            "milestones": await self._create_milestones(learning_sequence),
            "adaptation_rules": await self._create_adaptation_rules(learner_profile),
            "status": "active",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Store learning path
        self.learning_paths[path_id] = learning_path
        
        # Update learner profile
        learner_profile["active_learning_paths"] = learner_profile.get("active_learning_paths", [])
        learner_profile["active_learning_paths"].append(path_id)
        
        return learning_path
    
    async def _analyze_learning_objectives(self, objectives: List[str]) -> List[Dict[str, Any]]:
        """Analyze and structure learning objectives"""
        analyzed_objectives = []
        
        for objective in objectives:
            # Determine objective type
            obj_type = self._classify_objective_type(objective)
            
            # Assess complexity
            complexity = self._assess_objective_complexity(objective)
            
            # Estimate time required
            estimated_time = self._estimate_objective_time(objective, complexity)
            
            # Identify prerequisite skills
            prerequisites = self._identify_prerequisites(objective)
            
            analyzed_objectives.append({
                "objective": objective,
                "type": obj_type,
                "complexity": complexity,
                "estimated_time": estimated_time,
                "prerequisites": prerequisites,
                "success_criteria": self._define_success_criteria(objective),
                "assessment_methods": self._suggest_assessment_methods(obj_type)
            })
        
        return analyzed_objectives
    
    def _classify_objective_type(self, objective: str) -> str:
        """Classify the type of learning objective"""
        objective_lower = objective.lower()
        
        if any(word in objective_lower for word in ["understand", "learn", "know", "comprehend"]):
            return "knowledge"
        elif any(word in objective_lower for word in ["apply", "use", "implement", "practice"]):
            return "skill"
        elif any(word in objective_lower for word in ["analyze", "evaluate", "critique", "assess"]):
            return "analysis"
        elif any(word in objective_lower for word in ["create", "design", "build", "develop"]):
            return "creation"
        else:
            return "mixed"
    
    def _assess_objective_complexity(self, objective: str) -> str:
        """Assess the complexity level of an objective"""
        complexity_indicators = {
            "simple": ["basic", "intro", "fundamental", "beginner"],
            "intermediate": ["intermediate", "moderate", "standard", "practical"],
            "advanced": ["advanced", "complex", "sophisticated", "expert", "master"]
        }
        
        objective_lower = objective.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in objective_lower for indicator in indicators):
                return level
        
        return "intermediate"  # default
    
    def _estimate_objective_time(self, objective: str, complexity: str) -> int:
        """Estimate time required to achieve objective (in hours)"""
        base_times = {
            "simple": 2,
            "intermediate": 8,
            "advanced": 20
        }
        
        base_time = base_times.get(complexity, 8)
        
        # Adjust based on objective length and keywords
        if len(objective.split()) > 10:
            base_time *= 1.2
        
        if any(word in objective.lower() for word in ["master", "comprehensive", "complete"]):
            base_time *= 1.5
        
        return int(base_time)
    
    def _identify_prerequisites(self, objective: str) -> List[str]:
        """Identify prerequisite skills for objective"""
        # Simulate prerequisite identification
        prerequisites = []
        
        objective_lower = objective.lower()
        
        if "programming" in objective_lower:
            prerequisites.extend(["basic computer skills", "logical thinking"])
        
        if "data analysis" in objective_lower:
            prerequisites.extend(["basic math", "statistical concepts"])
        
        if "leadership" in objective_lower:
            prerequisites.extend(["communication skills", "teamwork experience"])
        
        return prerequisites
    
    def _define_success_criteria(self, objective: str) -> List[str]:
        """Define success criteria for learning objective"""
        criteria = []
        
        if "understand" in objective.lower():
            criteria.extend([
                "Can explain concepts clearly",
                "Can answer related questions accurately",
                "Can teach the concept to others"
            ])
        
        if "apply" in objective.lower():
            criteria.extend([
                "Can use knowledge in practical situations",
                "Can solve related problems independently",
                "Can adapt knowledge to new contexts"
            ])
        
        if "create" in objective.lower():
            criteria.extend([
                "Can produce original work",
                "Can demonstrate creative application",
                "Can receive and implement feedback"
            ])
        
        return criteria
    
    def _suggest_assessment_methods(self, objective_type: str) -> List[str]:
        """Suggest appropriate assessment methods"""
        methods = {
            "knowledge": ["quiz", "written test", "oral examination"],
            "skill": ["practical test", "project work", "demonstration"],
            "analysis": ["case study analysis", "research project", "critical review"],
            "creation": ["portfolio", "project submission", "peer review"],
            "mixed": ["comprehensive assessment", "multi-modal evaluation"]
        }
        
        return methods.get(objective_type, ["standard assessment"])
    
    async def _design_learning_sequence(self, learner_profile: Dict[str, Any], 
                                      objectives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Design optimal learning sequence for learner"""
        sequence = []
        
        # Sort objectives by complexity and prerequisites
        sorted_objectives = sorted(objectives, key=lambda x: (
            x["complexity"] == "simple",
            len(x["prerequisites"]),
            x["estimated_time"]
        ))
        
        for i, objective in enumerate(sorted_objectives):
            # Create learning module
            module = {
                "module_id": str(uuid.uuid4()),
                "sequence_position": i + 1,
                "objective": objective["objective"],
                "type": objective["type"],
                "complexity": objective["complexity"],
                "estimated_duration": objective["estimated_time"],
                "content_recommendations": await self._recommend_content(learner_profile, objective),
                "activities": await self._design_activities(learner_profile, objective),
                "assessment": await self._design_assessment(objective),
                "adaptation_triggers": await self._define_adaptation_triggers(objective)
            }
            
            sequence.append(module)
        
        return sequence
    
    async def _recommend_content(self, learner_profile: Dict[str, Any], 
                               objective: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend content based on learner profile and objective"""
        recommendations = []
        
        learning_style = learner_profile["learning_profile"]["learning_style"]
        content_types = learner_profile["preferences"]["content_types"]
        
        # Generate content recommendations based on learning style
        style_recommendations = learning_style["recommended_content"]
        
        for content_type in content_types:
            for style_content in style_recommendations:
                if content_type.lower() in style_content.lower() or style_content.lower() in content_type.lower():
                    recommendations.append({
                        "type": content_type,
                        "format": style_content,
                        "priority": random.choice(["high", "medium", "low"]),
                        "estimated_time": random.randint(30, 120)
                    })
        
        # Add objective-specific content
        if objective["type"] == "skill":
            recommendations.append({
                "type": "practice",
                "format": "hands-on exercises",
                "priority": "high",
                "estimated_time": 60
            })
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _design_activities(self, learner_profile: Dict[str, Any], 
                               objective: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design learning activities for objective"""
        activities = []
        
        # Base activities based on objective type
        if objective["type"] == "knowledge":
            activities.extend([
                {"type": "reading", "description": "Study relevant materials", "duration": 45},
                {"type": "discussion", "description": "Participate in group discussions", "duration": 30},
                {"type": "quiz", "description": "Complete knowledge check quiz", "duration": 15}
            ])
        elif objective["type"] == "skill":
            activities.extend([
                {"type": "demonstration", "description": "Watch skill demonstration", "duration": 20},
                {"type": "practice", "description": "Practice skill with guidance", "duration": 60},
                {"type": "application", "description": "Apply skill in real scenario", "duration": 45}
            ])
        
        # Adapt activities based on learning style
        learning_style = learner_profile["learning_profile"]["learning_style"]["primary_style"]
        
        if learning_style == "visual":
            activities.append({"type": "visualization", "description": "Create mind maps or diagrams", "duration": 30})
        elif learning_style == "auditory":
            activities.append({"type": "listening", "description": "Listen to audio explanations", "duration": 25})
        elif learning_style == "kinesthetic":
            activities.append({"type": "hands-on", "description": "Physical manipulation exercises", "duration": 40})
        
        return activities
    
    async def _design_assessment(self, objective: Dict[str, Any]) -> Dict[str, Any]:
        """Design assessment for objective"""
        assessment_methods = objective["assessment_methods"]
        
        primary_method = assessment_methods[0] if assessment_methods else "quiz"
        
        assessment = {
            "primary_method": primary_method,
            "criteria": objective["success_criteria"],
            "passing_threshold": 0.7,
            "feedback_provided": True,
            "retake_allowed": True,
            "time_limit": random.choice([30, 60, 90, 120])  # minutes
        }
        
        return assessment
    
    async def _define_adaptation_triggers(self, objective: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define triggers for adaptive learning"""
        triggers = [
            {
                "condition": "performance < 0.6",
                "action": "provide_additional_support",
                "description": "Provide extra resources and slower pace"
            },
            {
                "condition": "performance > 0.9",
                "action": "accelerate_learning",
                "description": "Skip to advanced content"
            },
            {
                "condition": "engagement < 0.5",
                "action": "change_content_format",
                "description": "Switch to different content types"
            }
        ]
        
        return triggers
    
    async def _calculate_path_metrics(self, learner_profile: Dict[str, Any], 
                                    sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for learning path"""
        total_duration = sum(module["estimated_duration"] for module in sequence)
        
        # Calculate difficulty progression
        complexity_levels = [module["complexity"] for module in sequence]
        progression_type = self._analyze_difficulty_progression(complexity_levels)
        
        return {
            "estimated_duration": total_duration,
            "difficulty_progression": progression_type,
            "total_modules": len(sequence),
            "estimated_completion_time": total_duration / learner_profile["learning_profile"]["available_time"],
            "adaptive_points": sum(len(module["adaptation_triggers"]) for module in sequence)
        }
    
    def _analyze_difficulty_progression(self, complexity_levels: List[str]) -> str:
        """Analyze the difficulty progression pattern"""
        complexity_order = {"simple": 1, "intermediate": 2, "advanced": 3}
        
        progression_scores = [complexity_order.get(level, 2) for level in complexity_levels]
        
        if progression_scores == sorted(progression_scores):
            return "increasing"
        elif progression_scores == sorted(progression_scores, reverse=True):
            return "decreasing"
        else:
            return "mixed"
    
    async def _create_milestones(self, sequence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create learning milestones"""
        milestones = []
        total_modules = len(sequence)
        
        # Create milestone at 25%, 50%, 75%, and 100%
        milestone_percentages = [0.25, 0.5, 0.75, 1.0]
        
        for percentage in milestone_percentages:
            module_index = int(total_modules * percentage) - 1
            if module_index >= 0:
                milestone = {
                    "milestone_id": str(uuid.uuid4()),
                    "sequence_position": module_index + 1,
                    "title": f"Milestone: {percentage * 100:.0f}% Complete",
                    "description": f"Complete module {module_index + 1} to reach this milestone",
                    "reward": self._suggest_milestone_reward(percentage),
                    "assessment_required": percentage >= 0.5
                }
                milestones.append(milestone)
        
        return milestones
    
    def _suggest_milestone_reward(self, percentage: float) -> str:
        """Suggest reward for milestone completion"""
        rewards = {
            0.25: "Badge: Getting Started",
            0.50: "Badge: Halfway There",
            0.75: "Badge: Almost There",
            1.0: "Badge: Learning Champion + Certificate"
        }
        
        return rewards.get(percentage, "Badge: Progress Maker")
    
    async def _create_adaptation_rules(self, learner_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create adaptation rules for the learning path"""
        rules = []
        
        # Learning pace adaptation
        preferred_pace = learner_profile["learning_profile"]["preferred_pace"]
        if preferred_pace == "slow":
            rules.append({
                "trigger": "difficulty_level > intermediate",
                "action": "extend_time_allowances",
                "factor": 1.5
            })
        elif preferred_pace == "fast":
            rules.append({
                "trigger": "performance > 0.8",
                "action": "skip_optional_content",
                "factor": 0.8
            })
        
        # Learning style adaptation
        learning_style = learner_profile["learning_profile"]["learning_style"]["primary_style"]
        rules.append({
            "trigger": "engagement < 0.6",
            "action": f"emphasize_{learning_style}_content",
            "factor": 1.0
        })
        
        return rules
    
    async def generate_content_recommendations(self, learner_id: str, 
                                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized content recommendations"""
        if learner_id not in self.learner_profiles:
            raise ValueError("Learner not found")
        
        learner_profile = self.learner_profiles[learner_id]
        
        # Analyze current context
        current_skill_level = context.get("current_skill_level", "beginner")
        learning_goal = context.get("learning_goal", "")
        time_available = context.get("time_available", 60)  # minutes
        preferred_difficulty = context.get("difficulty", "moderate")
        
        # Generate recommendations based on multiple factors
        recommendations = []
        
        # Skill gap analysis
        skill_gaps = await self._identify_skill_gaps(learner_profile, learning_goal)
        for skill_gap in skill_gaps:
            recommendation = await self._create_skill_recommendation(
                learner_profile, skill_gap, time_available, preferred_difficulty
            )
            recommendations.append(recommendation)
        
        # Interest-based recommendations
        interest_recommendations = await self._generate_interest_recommendations(
            learner_profile, time_available, preferred_difficulty
        )
        recommendations.extend(interest_recommendations)
        
        # Trending/popular content
        trending_recommendations = await self._generate_trending_recommendations(
            learner_profile, time_available
        )
        recommendations.extend(trending_recommendations)
        
        # Sort and filter recommendations
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        return recommendations[:10]  # Return top 10 recommendations
    
    async def _identify_skill_gaps(self, learner_profile: Dict[str, Any], 
                                 learning_goal: str) -> List[Dict[str, Any]]:
        """Identify skill gaps relative to learning goal"""
        skill_gaps = []
        
        # Analyze current skills
        current_skills = learner_profile["learning_profile"]["current_skills"]
        
        # Define target skills for the learning goal
        target_skills = await self._define_target_skills(learning_goal)
        
        # Find gaps
        for target_skill in target_skills:
            skill_found = False
            current_level = "none"
            
            for category_skills in current_skills.values():
                for skill in category_skills:
                    if target_skill["skill"].lower() in skill["skill"].lower():
                        skill_found = True
                        current_level = skill["level"]
                        break
                if skill_found:
                    break
            
            if not skill_found or self._assess_skill_level(current_level) < target_skill["required_level"]:
                skill_gaps.append({
                    "skill": target_skill["skill"],
                    "current_level": current_level,
                    "required_level": target_skill["required_level"],
                    "priority": target_skill["priority"],
                    "category": target_skill["category"]
                })
        
        return skill_gaps
    
    async def _define_target_skills(self, learning_goal: str) -> List[Dict[str, Any]]:
        """Define target skills for a learning goal"""
        # Simulate target skill definition based on learning goal
        if "programming" in learning_goal.lower():
            return [
                {"skill": "problem solving", "required_level": "intermediate", "priority": "high", "category": "analytical"},
                {"skill": "code debugging", "required_level": "intermediate", "priority": "high", "category": "technical"},
                {"skill": "software design", "required_level": "beginner", "priority": "medium", "category": "technical"}
            ]
        elif "leadership" in learning_goal.lower():
            return [
                {"skill": "communication", "required_level": "advanced", "priority": "high", "category": "soft"},
                {"skill": "team management", "required_level": "intermediate", "priority": "high", "category": "leadership"},
                {"skill": "decision making", "required_level": "intermediate", "priority": "medium", "category": "leadership"}
            ]
        else:
            return [
                {"skill": "general knowledge", "required_level": "beginner", "priority": "medium", "category": "general"}
            ]
    
    def _assess_skill_level(self, level: str) -> int:
        """Convert skill level to numeric score"""
        levels = {"none": 0, "beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        return levels.get(level, 0)
    
    async def _create_skill_recommendation(self, learner_profile: Dict[str, Any], 
                                         skill_gap: Dict[str, Any],
                                         time_available: int,
                                         preferred_difficulty: str) -> Dict[str, Any]:
        """Create recommendation for addressing skill gap"""
        learning_style = learner_profile["learning_profile"]["learning_style"]["primary_style"]
        
        # Calculate recommendation score
        priority_score = {"high": 1.0, "medium": 0.7, "low": 0.4}[skill_gap["priority"]]
        style_match_score = 0.8 if learning_style else 0.5
        time_suitability_score = 1.0 if time_available >= 60 else 0.6
        
        relevance_score = (priority_score + style_match_score + time_suitability_score) / 3
        
        return {
            "type": "skill_development",
            "title": f"Develop {skill_gap['skill']} Skills",
            "description": f"Improve your {skill_gap['skill']} from {skill_gap['current_level']} to {skill_gap['required_level']}",
            "skill_focus": skill_gap["skill"],
            "current_level": skill_gap["current_level"],
            "target_level": skill_gap["required_level"],
            "estimated_duration": random.choice([30, 60, 120]),
            "difficulty": preferred_difficulty,
            "learning_style_match": learning_style,
            "relevance_score": relevance_score,
            "content_types": self._get_content_recommendations(learning_style),
            "priority": skill_gap["priority"]
        }
    
    async def _generate_interest_recommendations(self, learner_profile: Dict[str, Any], 
                                               time_available: int,
                                               preferred_difficulty: str) -> List[Dict[str, Any]]:
        """Generate recommendations based on learner interests"""
        recommendations = []
        
        # Simulate interest-based content
        interest_topics = [
            {"topic": "Emerging Technologies", "interest_level": 0.8},
            {"topic": "Industry Best Practices", "interest_level": 0.7},
            {"topic": "Case Studies", "interest_level": 0.6}
        ]
        
        for topic in interest_topics:
            recommendation = {
                "type": "interest_based",
                "title": f"Explore {topic['topic']}",
                "description": f"Discover insights about {topic['topic'].lower()}",
                "topic": topic["topic"],
                "estimated_duration": random.choice([15, 30, 45]),
                "difficulty": preferred_difficulty,
                "interest_level": topic["interest_level"],
                "relevance_score": topic["interest_level"] * 0.8,
                "content_format": random.choice(["article", "video", "infographic"])
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_trending_recommendations(self, learner_profile: Dict[str, Any], 
                                               time_available: int) -> List[Dict[str, Any]]:
        """Generate recommendations for trending content"""
        recommendations = []
        
        # Simulate trending topics
        trending_topics = [
            {"topic": "AI and Machine Learning", "trend_score": 0.9},
            {"topic": "Remote Work Best Practices", "trend_score": 0.8},
            {"topic": "Sustainable Business Practices", "trend_score": 0.7}
        ]
        
        for topic in trending_topics:
            recommendation = {
                "type": "trending",
                "title": f"Trending: {topic['topic']}",
                "description": f"Stay current with {topic['topic'].lower()}",
                "topic": topic["topic"],
                "estimated_duration": random.choice([20, 40, 60]),
                "trend_score": topic["trend_score"],
                "relevance_score": topic["trend_score"] * 0.7,
                "content_format": random.choice(["video", "podcast", "article"]),
                "urgency": "high" if topic["trend_score"] > 0.8 else "medium"
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    async def track_learning_progress(self, learner_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze learning progress"""
        if learner_id not in self.learner_profiles:
            raise ValueError("Learner not found")
        
        learner_profile = self.learner_profiles[learner_id]
        
        # Update activity data
        activity_id = str(uuid.uuid4())
        activity = {
            "id": activity_id,
            "learner_id": learner_id,
            "activity_type": activity_data.get("activity_type", "content_consumption"),
            "content_id": activity_data.get("content_id", ""),
            "duration": activity_data.get("duration", 0),
            "completion_status": activity_data.get("completion_status", "incomplete"),
            "score": activity_data.get("score", 0.0),
            "timestamp": datetime.now().isoformat(),
            "context": activity_data.get("context", {})
        }
        
        # Store activity
        if "activities" not in learner_profile:
            learner_profile["activities"] = []
        learner_profile["activities"].append(activity)
        
        # Calculate progress metrics
        progress_metrics = await self._calculate_progress_metrics(learner_profile)
        
        # Update learner profile
        learner_profile["progress"].update(progress_metrics)
        learner_profile["last_activity"] = datetime.now().isoformat()
        
        # Generate insights
        insights = await self._generate_learning_insights(learner_profile, activity)
        
        return {
            "activity": activity,
            "progress_metrics": progress_metrics,
            "insights": insights,
            "recommendations": await self._generate_progress_recommendations(learner_profile, activity)
        }
    
    async def _calculate_progress_metrics(self, learner_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate learning progress metrics"""
        activities = learner_profile.get("activities", [])
        
        # Calculate total learning time
        total_time = sum(activity.get("duration", 0) for activity in activities)
        
        # Calculate completion rate
        completed_activities = [a for a in activities if a.get("completion_status") == "completed"]
        completion_rate = len(completed_activities) / len(activities) if activities else 0
        
        # Calculate average score
        scored_activities = [a for a in activities if a.get("score", 0) > 0]
        average_score = sum(a.get("score", 0) for a in scored_activities) / len(scored_activities) if scored_activities else 0
        
        # Calculate streak
        streak = self._calculate_learning_streak(activities)
        
        # Update progress
        current_progress = learner_profile.get("progress", {})
        current_progress.update({
            "total_learning_time": current_progress.get("total_learning_time", 0) + total_time,
            "total_courses_completed": current_progress.get("total_courses_completed", 0) + len(completed_activities),
            "current_streak": streak["current"],
            "longest_streak": max(streak["current"], current_progress.get("longest_streak", 0)),
            "completion_rate": completion_rate,
            "average_score": average_score,
            "last_updated": datetime.now().isoformat()
        })
        
        return current_progress
    
    def _calculate_learning_streak(self, activities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate learning streak"""
        if not activities:
            return {"current": 0, "longest": 0}
        
        # Sort activities by timestamp
        sorted_activities = sorted(activities, key=lambda x: x.get("timestamp", ""))
        
        current_streak = 1
        longest_streak = 1
        
        for i in range(1, len(sorted_activities)):
            prev_date = datetime.fromisoformat(sorted_activities[i-1]["timestamp"]).date()
            curr_date = datetime.fromisoformat(sorted_activities[i]["timestamp"]).date()
            
            if (curr_date - prev_date).days <= 1:  # Consecutive days
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        return {"current": current_streak, "longest": longest_streak}
    
    async def _generate_learning_insights(self, learner_profile: Dict[str, Any], 
                                        activity: Dict[str, Any]) -> List[str]:
        """Generate learning insights based on progress"""
        insights = []
        
        progress = learner_profile.get("progress", {})
        
        # Learning consistency insight
        if progress.get("current_streak", 0) >= 7:
            insights.append("Great job maintaining a learning streak! Consistency is key to mastery.")
        elif progress.get("current_streak", 0) == 0:
            insights.append("Consider setting a regular learning schedule to build momentum.")
        
        # Performance insight
        if progress.get("average_score", 0) > 0.8:
            insights.append("You're performing exceptionally well! Consider challenging yourself with advanced content.")
        elif progress.get("average_score", 0) < 0.6:
            insights.append("Take time to review fundamentals before moving to more complex topics.")
        
        # Time management insight
        total_time = progress.get("total_learning_time", 0)
        if total_time > 50:  # 50+ hours
            insights.append("Impressive learning dedication! You're building substantial expertise.")
        
        # Learning style insight
        learning_style = learner_profile["learning_profile"]["learning_style"]["primary_style"]
        if learning_style == "kinesthetic" and progress.get("completion_rate", 0) < 0.7:
            insights.append("Try incorporating more hands-on activities to improve engagement.")
        
        return insights
    
    async def _generate_progress_recommendations(self, learner_profile: Dict[str, Any], 
                                               activity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on progress"""
        recommendations = []
        
        progress = learner_profile.get("progress", {})
        
        # Completion rate recommendations
        completion_rate = progress.get("completion_rate", 0)
        if completion_rate < 0.5:
            recommendations.append({
                "type": "engagement",
                "title": "Improve Course Completion",
                "description": "Break courses into smaller, manageable chunks",
                "priority": "high"
            })
        
        # Score-based recommendations
        average_score = progress.get("average_score", 0)
        if average_score < 0.6:
            recommendations.append({
                "type": "skill_building",
                "title": "Strengthen Foundation",
                "description": "Review basic concepts before advancing",
                "priority": "high"
            })
        
        # Streak-based recommendations
        if progress.get("current_streak", 0) >= 7:
            recommendations.append({
                "type": "advancement",
                "title": "Leverage Momentum",
                "description": "Continue with advanced topics while maintaining streak",
                "priority": "medium"
            })
        
        return recommendations
    
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive learning analytics"""
        if not self.learner_profiles:
            return {"message": "No learning data available"}
        
        analytics = {
            "learner_metrics": await self._calculate_learner_metrics(),
            "content_performance": await self._analyze_content_performance(),
            "learning_patterns": await self._analyze_learning_patterns(),
            "skill_development": await self._analyze_skill_development(),
            "recommendations": await self._generate_platform_recommendations()
        }
        
        return analytics
    
    async def _calculate_learner_metrics(self) -> Dict[str, Any]:
        """Calculate learner-related metrics"""
        learners = list(self.learner_profiles.values())
        
        total_learners = len(learners)
        active_learners = len([l for l in learners if self._is_learner_active(l)])
        
        # Calculate average metrics
        avg_completion_rate = sum(l.get("progress", {}).get("completion_rate", 0) for l in learners) / total_learners
        avg_score = sum(l.get("progress", {}).get("average_score", 0) for l in learners) / total_learners
        avg_learning_time = sum(l.get("progress", {}).get("total_learning_time", 0) for l in learners) / total_learners
        
        # Learning style distribution
        style_distribution = {}
        for learner in learners:
            style = learner["learning_profile"]["learning_style"]["primary_style"]
            style_distribution[style] = style_distribution.get(style, 0) + 1
        
        return {
            "total_learners": total_learners,
            "active_learners": active_learners,
            "engagement_rate": active_learners / total_learners if total_learners > 0 else 0,
            "average_completion_rate": avg_completion_rate,
            "average_score": avg_score,
            "average_learning_time": avg_learning_time,
            "learning_style_distribution": style_distribution
        }
    
    def _is_learner_active(self, learner: Dict[str, Any]) -> bool:
        """Check if learner is currently active"""
        last_activity = learner.get("last_activity")
        if not last_activity:
            return False
        
        last_activity_date = datetime.fromisoformat(last_activity).date()
        current_date = datetime.now().date()
        
        return (current_date - last_activity_date).days <= 7  # Active within last week
    
    async def _analyze_content_performance(self) -> Dict[str, Any]:
        """Analyze content performance metrics"""
        # Simulate content performance analysis
        return {
            "most_popular_topics": [
                {"topic": "Programming Fundamentals", "engagement": 0.85},
                {"topic": "Data Analysis", "engagement": 0.78},
                {"topic": "Leadership Skills", "engagement": 0.72}
            ],
            "completion_rates_by_type": {
                "video": 0.75,
                "article": 0.68,
                "interactive": 0.82,
                "quiz": 0.70
            },
            "average_scores_by_difficulty": {
                "beginner": 0.85,
                "intermediate": 0.72,
                "advanced": 0.61
            }
        }
    
    async def _analyze_learning_patterns(self) -> Dict[str, Any]:
        """Analyze learning patterns across all learners"""
        # Simulate learning pattern analysis
        return {
            "peak_learning_hours": ["10:00-12:00", "14:00-16:00", "19:00-21:00"],
            "preferred_session_duration": 45,  # minutes
            "optimal_break_frequency": 60,  # minutes
            "weekend_vs_weekday_preference": 0.3,  # 30% prefer weekends
            "mobile_vs_desktop": 0.6  # 60% use mobile
        }
    
    async def _analyze_skill_development(self) -> Dict[str, Any]:
        """Analyze skill development trends"""
        # Simulate skill development analysis
        return {
            "most_developed_skills": [
                {"skill": "Programming", "proficiency_increase": 0.35},
                {"skill": "Data Analysis", "proficiency_increase": 0.28},
                {"skill": "Communication", "proficiency_increase": 0.22}
            ],
            "skill_gap_analysis": [
                {"skill": "Cloud Computing", "gap_size": 0.45},
                {"skill": "AI/ML", "gap_size": 0.42},
                {"skill": "Cybersecurity", "gap_size": 0.38}
            ],
            "emerging_skill_demand": [
                {"skill": "Blockchain", "demand_growth": 0.65},
                {"skill": "IoT Development", "demand_growth": 0.58},
                {"skill": "Quantum Computing", "demand_growth": 0.45}
            ]
        }
    
    async def _generate_platform_recommendations(self) -> List[Dict[str, Any]]:
        """Generate platform-level recommendations"""
        return [
            {
                "area": "content_diversity",
                "recommendation": "Add more interactive and hands-on content to improve engagement",
                "priority": "high",
                "impact": "medium"
            },
            {
                "area": "personalization",
                "recommendation": "Enhance adaptive learning algorithms based on learning style analysis",
                "priority": "medium",
                "impact": "high"
            },
            {
                "area": "mobile_experience",
                "recommendation": "Optimize mobile interface for on-the-go learning",
                "priority": "medium",
                "impact": "medium"
            }
        ]
    
    async def _update_learning_analytics(self, learner_profile: Dict[str, Any]):
        """Update learning analytics with new learner data"""
        if not self.learning_analytics:
            self.learning_analytics = {
                "total_learners": 0,
                "average_readiness_score": 0.0,
                "learning_style_distribution": {},
                "goal_categories": {}
            }
        
        analytics = self.learning_analytics
        
        # Update total learners
        analytics["total_learners"] += 1
        
        # Update average readiness score
        current_avg = analytics["average_readiness_score"]
        new_score = learner_profile["learning_profile"]["readiness_score"]
        analytics["average_readiness_score"] = (
            (current_avg * (analytics["total_learners"] - 1) + new_score) / analytics["total_learners"]
        )
        
        # Update learning style distribution
        style = learner_profile["learning_profile"]["learning_style"]["primary_style"]
        analytics["learning_style_distribution"][style] = analytics["learning_style_distribution"].get(style, 0) + 1
        
        # Update goal categories
        for goal in learner_profile["learning_profile"]["learning_goals"]:
            category = goal.get("category", "general")
            analytics["goal_categories"][category] = analytics["goal_categories"].get(category, 0) + 1
    
    async def _generate_initial_recommendations(self, learner_id: str):
        """Generate initial content recommendations for new learner"""
        learner_profile = self.learner_profiles[learner_id]
        
        # Generate initial recommendations based on profile
        initial_recommendations = await self.generate_content_recommendations(
            learner_id, 
            {
                "current_skill_level": "beginner",
                "learning_goal": "skill_development",
                "time_available": 60,
                "difficulty": "moderate"
            }
        )
        
        # Store recommendations
        self.content_recommendations[learner_id] = initial_recommendations

# Initialize Brain AI
brain_ai = BrainAI()

# Pydantic models
class LearnerProfile(BaseModel):
    name: str
    email: str
    role: Optional[str] = ""
    experience_years: int = 0
    learning_goals: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    domain_knowledge: List[str] = []
    tools_proficiency: List[str] = []
    preferred_pace: str = "moderate"
    available_time: int = 10  # hours per week
    learning_method: str = "mixed"
    content_types: List[str] = ["videos", "articles"]
    difficulty_preference: str = "progressive"
    feedback_frequency: str = "weekly"
    collaboration_preference: str = "optional"
    courses_completed: List[str] = []
    certifications: List[str] = []

class LearningPathRequest(BaseModel):
    learner_id: str
    title: str
    description: str
    objectives: List[str]

class ProgressTrackingRequest(BaseModel):
    learner_id: str
    activity_type: str
    content_id: Optional[str] = ""
    duration: int = 0
    completion_status: str = "incomplete"
    score: Optional[float] = 0.0
    context: Dict[str, Any] = {}

class RecommendationRequest(BaseModel):
    learner_id: str
    current_skill_level: str = "beginner"
    learning_goal: str = ""
    time_available: int = 60
    difficulty: str = "moderate"

# Initialize FastAPI app
app = FastAPI(title="Brain AI Learning Platform", version="1.0.0")

# Demo data generator
async def generate_demo_data():
    """Generate demo learners and learning content"""
    # Demo learners
    demo_learners = [
        {
            "name": "Alice Chen",
            "email": "alice.chen@email.com",
            "role": "Software Developer",
            "experience_years": 3,
            "learning_goals": ["Master Python programming", "Learn machine learning", "Improve system design"],
            "technical_skills": ["Python", "JavaScript", "React", "Git"],
            "soft_skills": ["Problem solving", "Communication", "Teamwork"],
            "domain_knowledge": ["Web development", "API design"],
            "tools_proficiency": ["VS Code", "Docker", "Postman"],
            "preferred_pace": "moderate",
            "available_time": 15,
            "learning_method": "hands_on",
            "content_types": ["videos", "interactive", "projects"],
            "courses_completed": ["JavaScript Fundamentals", "Git Basics"],
            "certifications": []
        },
        {
            "name": "Bob Johnson",
            "email": "bob.johnson@email.com",
            "role": "Product Manager",
            "experience_years": 5,
            "learning_goals": ["Develop leadership skills", "Learn data analytics", "Master agile methodologies"],
            "technical_skills": ["SQL", "Excel", "Tableau"],
            "soft_skills": ["Leadership", "Strategic thinking", "Communication"],
            "domain_knowledge": ["Product management", "Market research"],
            "tools_proficiency": ["Jira", "Confluence", "Figma"],
            "preferred_pace": "fast",
            "available_time": 10,
            "learning_method": "mixed",
            "content_types": ["articles", "case studies", "webinars"],
            "courses_completed": ["Agile Fundamentals", "Data Visualization"],
            "certifications": ["PMP"]
        },
        {
            "name": "Carol Smith",
            "email": "carol.smith@email.com",
            "role": "Data Analyst",
            "experience_years": 2,
            "learning_goals": ["Advance statistical analysis", "Learn Python for data science", "Master visualization tools"],
            "technical_skills": ["Excel", "R", "SQL", "Python"],
            "soft_skills": ["Analytical thinking", "Attention to detail", "Documentation"],
            "domain_knowledge": ["Statistics", "Data visualization"],
            "tools_proficiency": ["Tableau", "Power BI", "Jupyter"],
            "preferred_pace": "slow",
            "available_time": 8,
            "learning_method": "structured",
            "content_types": ["tutorials", "quizzes", "reading"],
            "courses_completed": ["Statistics 101", "Excel Advanced"],
            "certifications": []
        }
    ]
    
    for learner_data in demo_learners:
        await brain_ai.create_learner_profile(learner_data)
    
    # Demo learning paths
    demo_paths = [
        {
            "learner_id": list(brain_ai.learner_profiles.keys())[0],  # Alice
            "title": "Full-Stack Developer Path",
            "description": "Comprehensive path to become a full-stack developer",
            "objectives": ["Master frontend frameworks", "Learn backend development", "Understand database design", "Deploy applications"]
        },
        {
            "learner_id": list(brain_ai.learner_profiles.keys())[1],  # Bob
            "title": "Leadership Excellence Path",
            "description": "Develop leadership and management skills",
            "objectives": ["Build team leadership skills", "Master strategic planning", "Improve stakeholder management", "Learn change management"]
        }
    ]
    
    for path_data in demo_paths:
        await brain_ai.create_learning_path(path_data)

# Generate demo data on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Brain AI Learning Platform...")
    await generate_demo_data()
    logger.info(f"Demo data loaded. {len(brain_ai.learner_profiles)} learners, {len(brain_ai.learning_paths)} learning paths.")

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main dashboard page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Brain AI Learning Platform</title>
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
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                padding: 30px;
            }
            
            .learner-section, .path-section, .progress-section, .recommendations-section {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            .section-title {
                font-size: 1.3em;
                color: #2c3e50;
                margin-bottom: 15px;
                font-weight: 600;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
                color: #2c3e50;
            }
            
            .form-control {
                width: 100%;
                padding: 10px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            
            .form-control:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            textarea.form-control {
                height: 80px;
                resize: vertical;
            }
            
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.3s ease;
                margin-right: 10px;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            
            .btn-secondary {
                background: #6c757d;
            }
            
            .btn-success {
                background: #28a745;
            }
            
            .results {
                grid-column: 1 / -1;
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                border: 1px solid #e9ecef;
            }
            
            .learner-card, .path-card, .progress-card, .recommendation-card {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }
            
            .learner-name, .path-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            
            .learner-info, .path-info {
                color: #495057;
                margin-bottom: 10px;
                line-height: 1.5;
            }
            
            .learner-meta, .path-meta {
                display: flex;
                gap: 15px;
                font-size: 12px;
                color: #6c757d;
                flex-wrap: wrap;
            }
            
            .score-badge {
                background: #28a745;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
            }
            
            .readiness-badge {
                background: #007bff;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
            }
            
            .skills {
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
                margin-top: 8px;
            }
            
            .skill-tag {
                background: #e9ecef;
                color: #495057;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 11px;
            }
            
            .analytics-section {
                grid-column: 1 / -1;
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            .analytics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .analytics-card {
                background: white;
                padding: 15px;
                border-radius: 6px;
                border: 1px solid #dee2e6;
                text-align: center;
            }
            
            .analytics-number {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            
            .analytics-label {
                color: #6c757d;
                font-size: 0.9em;
                margin-top: 5px;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #6c757d;
            }
            
            .loading.show {
                display: block;
            }
            
            select.form-control {
                appearance: none;
                background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
                background-position: right 0.5rem center;
                background-repeat: no-repeat;
                background-size: 1.5em 1.5em;
                padding-right: 2.5rem;
            }
            
            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }
                
                .header h1 {
                    font-size: 2em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Brain AI Learning Platform</h1>
                <p>Intelligent adaptive learning and skill development platform</p>
            </div>
            
            <div class="main-content">
                <div class="learner-section">
                    <div class="section-title">Create Learner Profile</div>
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="learnerName" class="form-control" placeholder="Full name">
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" id="learnerEmail" class="form-control" placeholder="email@domain.com">
                    </div>
                    <div class="form-group">
                        <label>Role:</label>
                        <input type="text" id="learnerRole" class="form-control" placeholder="Job role">
                    </div>
                    <div class="form-group">
                        <label>Experience Years:</label>
                        <input type="number" id="learnerExperience" class="form-control" min="0" max="50">
                    </div>
                    <div class="form-group">
                        <label>Learning Goals (comma-separated):</label>
                        <input type="text" id="learningGoals" class="form-control" placeholder="Goal 1, Goal 2, Goal 3">
                    </div>
                    <div class="form-group">
                        <label>Technical Skills (comma-separated):</label>
                        <input type="text" id="technicalSkills" class="form-control" placeholder="Python, JavaScript, React">
                    </div>
                    <div class="form-group">
                        <label>Available Time (hours/week):</label>
                        <input type="number" id="availableTime" class="form-control" value="10" min="1" max="40">
                    </div>
                    <button class="btn" onclick="createLearner()">Create Profile</button>
                </div>
                
                <div class="path-section">
                    <div class="section-title">Create Learning Path</div>
                    <div class="form-group">
                        <label>Select Learner:</label>
                        <select id="pathLearner" class="form-control">
                            <option value="">Select a learner...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Path Title:</label>
                        <input type="text" id="pathTitle" class="form-control" placeholder="Learning path title">
                    </div>
                    <div class="form-group">
                        <label>Description:</label>
                        <textarea id="pathDescription" class="form-control" placeholder="Brief description"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Objectives (comma-separated):</label>
                        <input type="text" id="pathObjectives" class="form-control" placeholder="Objective 1, Objective 2">
                    </div>
                    <button class="btn btn-success" onclick="createLearningPath()">Create Path</button>
                </div>
                
                <div class="progress-section">
                    <div class="section-title">Track Progress</div>
                    <div class="form-group">
                        <label>Select Learner:</label>
                        <select id="progressLearner" class="form-control">
                            <option value="">Select a learner...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Activity Type:</label>
                        <select id="activityType" class="form-control">
                            <option value="content_consumption">Content Consumption</option>
                            <option value="assessment">Assessment</option>
                            <option value="project">Project Work</option>
                            <option value="discussion">Discussion</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Duration (minutes):</label>
                        <input type="number" id="activityDuration" class="form-control" value="30" min="1">
                    </div>
                    <div class="form-group">
                        <label>Completion Status:</label>
                        <select id="completionStatus" class="form-control">
                            <option value="completed">Completed</option>
                            <option value="incomplete">Incomplete</option>
                            <option value="in_progress">In Progress</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Score (0-1):</label>
                        <input type="number" id="activityScore" class="form-control" value="0.8" min="0" max="1" step="0.1">
                    </div>
                    <button class="btn btn-success" onclick="trackProgress()">Track Progress</button>
                </div>
                
                <div class="recommendations-section">
                    <div class="section-title">Get Recommendations</div>
                    <div class="form-group">
                        <label>Select Learner:</label>
                        <select id="recommendationLearner" class="form-control">
                            <option value="">Select a learner...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Current Skill Level:</label>
                        <select id="skillLevel" class="form-control">
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Learning Goal:</label>
                        <input type="text" id="recommendationGoal" class="form-control" placeholder="Skill development focus">
                    </div>
                    <div class="form-group">
                        <label>Time Available (minutes):</label>
                        <input type="number" id="timeAvailable" class="form-control" value="60" min="15">
                    </div>
                    <button class="btn" onclick="getRecommendations()">Get Recommendations</button>
                </div>
                
                <div class="analytics-section">
                    <div class="section-title">Learning Analytics</div>
                    <button class="btn" onclick="loadAnalytics()">Refresh Analytics</button>
                    <div id="analyticsContent" style="margin-top: 15px;">
                        <p style="color: #6c757d;">Click "Refresh Analytics" to view learning insights</p>
                    </div>
                </div>
                
                <div class="results" id="resultsSection" style="display: none;">
                    <div class="section-title">Results</div>
                    <div id="resultsContent"></div>
                    <div class="loading" id="loadingIndicator">
                        <p>Processing...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function createLearner() {
                const name = document.getElementById('learnerName').value.trim();
                const email = document.getElementById('learnerEmail').value.trim();
                const role = document.getElementById('learnerRole').value.trim();
                const experience = parseInt(document.getElementById('learnerExperience').value) || 0;
                const goals = document.getElementById('learningGoals').value.split(',').map(g => g.trim()).filter(g => g);
                const skills = document.getElementById('technicalSkills').value.split(',').map(s => s.trim()).filter(s => s);
                const availableTime = parseInt(document.getElementById('availableTime').value) || 10;
                
                if (!name || !email) {
                    alert('Please provide name and email');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/learners', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: name,
                            email: email,
                            role: role,
                            experience_years: experience,
                            learning_goals: goals,
                            technical_skills: skills,
                            soft_skills: [],
                            domain_knowledge: [],
                            tools_proficiency: [],
                            available_time: availableTime
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="learner-card">
                                <div class="learner-name">${data.basic_info.name}</div>
                                <div class="learner-info">Role: ${data.basic_info.role || 'Not specified'}</div>
                                <div class="learner-info">Experience: ${data.basic_info.experience_years} years</div>
                                <div class="learner-meta">
                                    <span class="readiness-badge">Learning Readiness: ${(data.learning_profile.readiness_score * 100).toFixed(1)}%</span>
                                    <span class="score-badge">Learning Style: ${data.learning_profile.learning_style.primary_style.replace('_', ' ')}</span>
                                    <span>Available Time: ${data.learning_profile.available_time}h/week</span>
                                </div>
                                <div class="skills">
                                    ${data.learning_profile.learning_goals.map(goal => `<span class="skill-tag">${goal}</span>`).join('')}
                                </div>
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('learnerName').value = '';
                        document.getElementById('learnerEmail').value = '';
                        document.getElementById('learnerRole').value = '';
                        document.getElementById('learnerExperience').value = '';
                        document.getElementById('learningGoals').value = '';
                        document.getElementById('technicalSkills').value = '';
                        
                        // Update dropdowns
                        loadLearners();
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error creating learner profile. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error creating learner profile. Please try again.</p>';
                    console.error('Create learner error:', error);
                }
            }
            
            async function createLearningPath() {
                const learnerId = document.getElementById('pathLearner').value;
                const title = document.getElementById('pathTitle').value.trim();
                const description = document.getElementById('pathDescription').value.trim();
                const objectives = document.getElementById('pathObjectives').value.split(',').map(o => o.trim()).filter(o => o);
                
                if (!learnerId || !title || objectives.length === 0) {
                    alert('Please fill in all required fields');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/learning-paths', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            learner_id: learnerId,
                            title: title,
                            description: description,
                            objectives: objectives
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="path-card">
                                <div class="path-title">${data.title}</div>
                                <div class="path-info">${data.description || 'No description provided'}</div>
                                <div class="path-info"><strong>Objectives:</strong> ${data.objectives.map(obj => obj.objective).join(', ')}</div>
                                <div class="learner-meta">
                                    <span class="score-badge">Duration: ${data.estimated_duration} hours</span>
                                    <span>Modules: ${data.learning_sequence.length}</span>
                                    <span>Difficulty: ${data.difficulty_progression}</span>
                                </div>
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('pathLearner').value = '';
                        document.getElementById('pathTitle').value = '';
                        document.getElementById('pathDescription').value = '';
                        document.getElementById('pathObjectives').value = '';
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error creating learning path. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error creating learning path. Please try again.</p>';
                    console.error('Create learning path error:', error);
                }
            }
            
            async function trackProgress() {
                const learnerId = document.getElementById('progressLearner').value;
                const activityType = document.getElementById('activityType').value;
                const duration = parseInt(document.getElementById('activityDuration').value) || 30;
                const completionStatus = document.getElementById('completionStatus').value;
                const score = parseFloat(document.getElementById('activityScore').value) || 0.0;
                
                if (!learnerId) {
                    alert('Please select a learner');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/progress', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            learner_id: learnerId,
                            activity_type: activityType,
                            duration: duration,
                            completion_status: completionStatus,
                            score: score
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="progress-card">
                                <div class="learner-name">Progress Tracked</div>
                                <div class="learner-info">Activity: ${data.activity.activity_type}</div>
                                <div class="learner-info">Duration: ${data.activity.duration} minutes</div>
                                <div class="learner-info">Status: ${data.activity.completion_status}</div>
                                <div class="learner-meta">
                                    <span class="score-badge">Completion Rate: ${(data.progress_metrics.completion_rate * 100).toFixed(1)}%</span>
                                    <span class="score-badge">Average Score: ${(data.progress_metrics.average_score * 100).toFixed(1)}%</span>
                                    <span>Current Streak: ${data.progress_metrics.current_streak} days</span>
                                </div>
                                <div style="margin-top: 15px;">
                                    <strong>Insights:</strong>
                                    <ul style="margin-top: 5px; margin-left: 20px;">
                                        ${data.insights.map(insight => `<li>${insight}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('progressLearner').value = '';
                        document.getElementById('activityDuration').value = '30';
                        document.getElementById('activityScore').value = '0.8';
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error tracking progress. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error tracking progress. Please try again.</p>';
                    console.error('Track progress error:', error);
                }
            }
            
            async function getRecommendations() {
                const learnerId = document.getElementById('recommendationLearner').value;
                const skillLevel = document.getElementById('skillLevel').value;
                const goal = document.getElementById('recommendationGoal').value.trim();
                const timeAvailable = parseInt(document.getElementById('timeAvailable').value) || 60;
                
                if (!learnerId) {
                    alert('Please select a learner');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/recommendations', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            learner_id: learnerId,
                            current_skill_level: skillLevel,
                            learning_goal: goal,
                            time_available: timeAvailable,
                            difficulty: "moderate"
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        if (data.length === 0) {
                            resultsContent.innerHTML = '<p style="color: #6c757d; text-align: center;">No recommendations available.</p>';
                            return;
                        }
                        
                        resultsContent.innerHTML = data.map(rec => `
                            <div class="recommendation-card">
                                <div class="learner-name">${rec.title}</div>
                                <div class="learner-info">${rec.description}</div>
                                <div class="learner-meta">
                                    <span class="score-badge">Type: ${rec.type.replace('_', ' ')}</span>
                                    <span class="score-badge">Relevance: ${(rec.relevance_score * 100).toFixed(1)}%</span>
                                    <span>Duration: ${rec.estimated_duration} min</span>
                                    <span>Priority: ${rec.priority}</span>
                                </div>
                                ${rec.skill_focus ? `<div style="margin-top: 10px;"><strong>Skill Focus:</strong> ${rec.skill_focus}</div>` : ''}
                            </div>
                        `).join('');
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error getting recommendations. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error getting recommendations. Please try again.</p>';
                    console.error('Get recommendations error:', error);
                }
            }
            
            async function loadAnalytics() {
                const analyticsContent = document.getElementById('analyticsContent');
                
                try {
                    const response = await fetch('/api/analytics');
                    const data = await response.json();
                    
                    if (data.message) {
                        analyticsContent.innerHTML = '<p style="color: #6c757d;">No learning data available for analytics.</p>';
                        return;
                    }
                    
                    analyticsContent.innerHTML = `
                        <div class="analytics-grid">
                            <div class="analytics-card">
                                <div class="analytics-number">${data.learner_metrics.total_learners}</div>
                                <div class="analytics-label">Total Learners</div>
                            </div>
                            <div class="analytics-card">
                                <div class="analytics-number">${data.learner_metrics.active_learners}</div>
                                <div class="analytics-label">Active Learners</div>
                            </div>
                            <div class="analytics-card">
                                <div class="analytics-number">${(data.learner_metrics.engagement_rate * 100).toFixed(1)}%</div>
                                <div class="analytics-label">Engagement Rate</div>
                            </div>
                            <div class="analytics-card">
                                <div class="analytics-number">${(data.learner_metrics.average_completion_rate * 100).toFixed(1)}%</div>
                                <div class="analytics-label">Avg Completion Rate</div>
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Learning Style Distribution</h4>
                        <div style="margin-top: 10px;">
                            ${Object.entries(data.learner_metrics.learning_style_distribution).map(([style, count]) => `
                                <span class="skill-tag" style="margin-right: 5px; margin-bottom: 5px;">${style.replace('_', ' ')}: ${count}</span>
                            `).join('')}
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Content Performance</h4>
                        <div style="margin-top: 10px;">
                            <strong>Completion Rates by Type:</strong>
                            <div style="margin-top: 5px;">
                                ${Object.entries(data.content_performance.completion_rates_by_type).map(([type, rate]) => `
                                    <span class="skill-tag" style="margin-right: 5px; margin-bottom: 5px;">${type}: ${(rate * 100).toFixed(1)}%</span>
                                `).join('')}
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Platform Recommendations</h4>
                        <div style="margin-top: 10px;">
                            ${data.recommendations.map(rec => `
                                <div style="background: #fff3cd; padding: 10px; border-radius: 4px; margin-bottom: 5px;">
                                    <strong>${rec.area}:</strong> ${rec.recommendation} (Priority: ${rec.priority})
                                </div>
                            `).join('')}
                        </div>
                    `;
                    
                } catch (error) {
                    analyticsContent.innerHTML = '<p style="color: #dc3545;">Error loading analytics. Please try again.</p>';
                    console.error('Analytics error:', error);
                }
            }
            
            async function loadLearners() {
                try {
                    const response = await fetch('/api/learners');
                    const learners = await response.json();
                    
                    const selects = ['pathLearner', 'progressLearner', 'recommendationLearner'];
                    
                    selects.forEach(selectId => {
                        const select = document.getElementById(selectId);
                        select.innerHTML = '<option value="">Select a learner...</option>';
                        
                        learners.forEach(learner => {
                            const option = document.createElement('option');
                            option.value = learner.id;
                            option.textContent = `${learner.basic_info.name} (${learner.basic_info.role || 'No role'})`;
                            select.appendChild(option);
                        });
                    });
                } catch (error) {
                    console.error('Error loading learners:', error);
                }
            }
            
            // Load initial data
            window.onload = function() {
                loadLearners();
            };
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/learners")
async def create_learner(profile: LearnerProfile):
    """Create new learner profile"""
    try:
        profile_dict = profile.dict()
        result = await brain_ai.create_learner_profile(profile_dict)
        return result
    except Exception as e:
        logger.error(f"Error creating learner profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learners")
async def get_learners():
    """Get all learner profiles"""
    try:
        learners = list(brain_ai.learner_profiles.values())
        return learners
    except Exception as e:
        logger.error(f"Error getting learners: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/learning-paths")
async def create_learning_path(path_request: LearningPathRequest):
    """Create new learning path"""
    try:
        path_dict = path_request.dict()
        result = await brain_ai.create_learning_path(path_dict)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-paths")
async def get_learning_paths():
    """Get all learning paths"""
    try:
        paths = list(brain_ai.learning_paths.values())
        return paths
    except Exception as e:
        logger.error(f"Error getting learning paths: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/progress")
async def track_learning_progress(progress_request: ProgressTrackingRequest):
    """Track learning progress"""
    try:
        progress_dict = progress_request.dict()
        result = await brain_ai.track_learning_progress(
            progress_dict["learner_id"], progress_dict
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error tracking progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations")
async def get_content_recommendations(request: RecommendationRequest):
    """Get personalized content recommendations"""
    try:
        request_dict = request.dict()
        result = await brain_ai.generate_content_recommendations(
            request_dict["learner_id"], request_dict
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_learning_analytics():
    """Get learning analytics and insights"""
    try:
        analytics = await brain_ai.get_learning_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learners/{learner_id}/profile")
async def get_learner_profile(learner_id: str):
    """Get detailed learner profile"""
    try:
        if learner_id not in brain_ai.learner_profiles:
            raise HTTPException(status_code=404, detail="Learner not found")
        
        return brain_ai.learner_profiles[learner_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting learner profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")