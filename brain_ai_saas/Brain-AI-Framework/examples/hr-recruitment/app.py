#!/usr/bin/env python3
"""
HR Recruitment System - Brain AI Example
Intelligent recruitment and talent acquisition platform
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainAI:
    """Brain AI Framework - HR Recruitment Core"""
    
    def __init__(self):
        self.candidate_profiles = {}
        self.job_postings = {}
        self.interview_schedules = {}
        self.evaluation_criteria = {}
        self.talent_insights = {}
        self.recruitment_patterns = {}
        self.success_metrics = {}
        self.bias_detection = {}
        
    async def process_candidate(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze candidate profile"""
        candidate_id = str(uuid.uuid4())
        
        # Extract candidate competencies
        competencies = await self._extract_competencies(profile_data)
        skills = await self._extract_skills(profile_data)
        experience_level = self._assess_experience_level(profile_data)
        cultural_fit = await self._assess_cultural_fit(profile_data)
        
        # Calculate candidate score
        candidate_score = await self._calculate_candidate_score(
            profile_data, competencies, skills, experience_level, cultural_fit
        )
        
        # Detect potential biases
        bias_analysis = await self._analyze_bias_indicators(profile_data)
        
        # Create candidate profile
        candidate_profile = {
            "id": candidate_id,
            "basic_info": {
                "name": profile_data.get("name", ""),
                "email": profile_data.get("email", ""),
                "phone": profile_data.get("phone", ""),
                "location": profile_data.get("location", "")
            },
            "professional_info": {
                "experience_years": profile_data.get("experience_years", 0),
                "previous_roles": profile_data.get("previous_roles", []),
                "education": profile_data.get("education", []),
                "certifications": profile_data.get("certifications", [])
            },
            "competencies": competencies,
            "skills": skills,
            "experience_level": experience_level,
            "cultural_fit_score": cultural_fit,
            "overall_score": candidate_score,
            "bias_analysis": bias_analysis,
            "applied_positions": [],
            "interview_history": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Store candidate profile
        self.candidate_profiles[candidate_id] = candidate_profile
        
        # Update talent insights
        await self._update_talent_insights(candidate_profile)
        
        # Update recruitment patterns
        await self._update_recruitment_patterns(candidate_profile)
        
        return candidate_profile
    
    async def _extract_competencies(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and analyze candidate competencies"""
        competencies = []
        
        # Technical competencies
        tech_skills = profile_data.get("technical_skills", [])
        for skill in tech_skills:
            competencies.append({
                "type": "technical",
                "name": skill,
                "proficiency": random.choice(["beginner", "intermediate", "advanced", "expert"]),
                "years_experience": random.randint(1, 10),
                "verified": random.choice([True, False])
            })
        
        # Soft skills
        soft_skills = profile_data.get("soft_skills", [])
        for skill in soft_skills:
            competencies.append({
                "type": "soft",
                "name": skill,
                "proficiency": random.choice(["basic", "good", "excellent"]),
                "evidence": random.choice(["interview", "reference", "assessment"]),
                "verified": random.choice([True, False])
            })
        
        # Leadership competencies
        leadership_skills = profile_data.get("leadership_skills", [])
        for skill in leadership_skills:
            competencies.append({
                "type": "leadership",
                "name": skill,
                "level": random.choice(["team_member", "team_lead", "manager", "director"]),
                "scope": random.choice(["small_team", "department", "organization"]),
                "verified": random.choice([True, False])
            })
        
        return competencies
    
    async def _extract_skills(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and categorize skills"""
        all_skills = profile_data.get("skills", [])
        
        # Categorize skills
        skill_categories = {
            "technical": [],
            "communication": [],
            "analytical": [],
            "creative": [],
            "leadership": [],
            "domain_specific": []
        }
        
        # Skill categorization logic
        for skill in all_skills:
            skill_lower = skill.lower()
            if any(tech in skill_lower for tech in ["programming", "development", "technical", "software", "coding"]):
                skill_categories["technical"].append(skill)
            elif any(comm in skill_lower for comm in ["communication", "presentation", "writing", "speaking"]):
                skill_categories["communication"].append(skill)
            elif any(anal in skill_lower for anal in ["analysis", "data", "research", "problem"]):
                skill_categories["analytical"].append(skill)
            elif any(creat in skill_lower for creat in ["design", "creative", "innovation", "art"]):
                skill_categories["creative"].append(skill)
            elif any(lead in skill_lower for lead in ["leadership", "management", "team", "mentoring"]):
                skill_categories["leadership"].append(skill)
            else:
                skill_categories["domain_specific"].append(skill)
        
        return skill_categories
    
    def _assess_experience_level(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess candidate's experience level"""
        experience_years = profile_data.get("experience_years", 0)
        
        if experience_years < 2:
            level = "entry"
            description = "Junior level with basic experience"
        elif experience_years < 5:
            level = "mid"
            description = "Mid-level with solid experience"
        elif experience_years < 10:
            level = "senior"
            description = "Senior level with extensive experience"
        else:
            level = "expert"
            description = "Expert level with leadership experience"
        
        # Calculate career progression rate
        roles_count = len(profile_data.get("previous_roles", []))
        progression_rate = min(roles_count / max(experience_years, 1), 2.0)
        
        return {
            "level": level,
            "description": description,
            "years_experience": experience_years,
            "progression_rate": progression_rate,
            "role_stability": random.uniform(0.6, 0.95),
            "career_growth": random.choice(["steady", "accelerated", "exceptional"])
        }
    
    async def _assess_cultural_fit(self, profile_data: Dict[str, Any]) -> float:
        """Assess cultural fit based on profile data"""
        fit_score = 0.0
        
        # Experience stability
        experience_years = profile_data.get("experience_years", 0)
        roles_count = len(profile_data.get("previous_roles", []))
        if experience_years > 0:
            stability = min(roles_count / experience_years, 1.0)
            fit_score += stability * 0.2
        
        # Education alignment
        education = profile_data.get("education", [])
        if education:
            fit_score += 0.15
        
        # Continuous learning
        certifications = profile_data.get("certifications", [])
        if certifications:
            fit_score += len(certifications) * 0.05
        
        # Location compatibility
        location = profile_data.get("location", "")
        if location and location.lower() in ["remote", "hybrid", "flexible"]:
            fit_score += 0.1
        
        # Communication skills
        soft_skills = profile_data.get("soft_skills", [])
        if any(skill.lower() in ["communication", "teamwork", "collaboration"] for skill in soft_skills):
            fit_score += 0.15
        
        # Add some randomness to simulate complex assessment
        fit_score += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, fit_score))
    
    async def _calculate_candidate_score(self, profile_data: Dict[str, Any], 
                                       competencies: List[Dict[str, Any]], 
                                       skills: Dict[str, Any],
                                       experience_level: Dict[str, Any],
                                       cultural_fit: float) -> float:
        """Calculate overall candidate score"""
        score = 0.0
        
        # Experience score (30%)
        experience_score = min(experience_level["years_experience"] / 10.0, 1.0)
        score += experience_score * 0.3
        
        # Skills score (25%)
        total_skills = sum(len(category_skills) for category_skills in skills.values())
        skills_score = min(total_skills / 20.0, 1.0)  # Assuming 20 skills is excellent
        score += skills_score * 0.25
        
        # Competency score (25%)
        advanced_competencies = sum(1 for comp in competencies 
                                  if comp.get("proficiency") in ["advanced", "expert"])
        competency_score = min(len(competencies) / 10.0, 1.0) * (1 + advanced_competencies * 0.1)
        score += min(competency_score, 1.0) * 0.25
        
        # Cultural fit score (15%)
        score += cultural_fit * 0.15
        
        # Education and certifications (5%)
        education_score = len(profile_data.get("education", [])) * 0.02
        cert_score = len(profile_data.get("certifications", [])) * 0.03
        score += min(education_score + cert_score, 0.05)
        
        return min(score, 1.0)
    
    async def _analyze_bias_indicators(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential bias indicators in the candidate profile"""
        bias_indicators = {
            "name_bias_risk": random.uniform(0.0, 0.3),  # Simulated risk based on name analysis
            "education_bias_risk": random.uniform(0.0, 0.2),
            "experience_bias_risk": random.uniform(0.0, 0.25),
            "location_bias_risk": random.uniform(0.0, 0.15),
            "overall_bias_risk": 0.0,
            "recommendations": []
        }
        
        # Calculate overall bias risk
        bias_indicators["overall_bias_risk"] = (
            bias_indicators["name_bias_risk"] * 0.3 +
            bias_indicators["education_bias_risk"] * 0.2 +
            bias_indicators["experience_bias_risk"] * 0.3 +
            bias_indicators["location_bias_risk"] * 0.2
        )
        
        # Generate recommendations
        if bias_indicators["overall_bias_risk"] > 0.6:
            bias_indicators["recommendations"].append("Use structured interview process")
            bias_indicators["recommendations"].append("Include diverse interview panel")
        
        if bias_indicators["name_bias_risk"] > 0.5:
            bias_indicators["recommendations"].append("Blind resume review process")
        
        if bias_indicators["education_bias_risk"] > 0.4:
            bias_indicators["recommendations"].append("Focus on skills-based evaluation")
        
        return bias_indicators
    
    async def create_job_posting(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and analyze job posting"""
        job_id = str(uuid.uuid4())
        
        # Extract job requirements
        required_skills = await self._extract_job_requirements(job_data)
        experience_requirements = self._assess_experience_requirements(job_data)
        competency_requirements = await self._extract_competency_requirements(job_data)
        
        # Calculate job difficulty score
        difficulty_score = await self._calculate_job_difficulty(
            job_data, required_skills, experience_requirements
        )
        
        # Analyze market competitiveness
        market_analysis = await self._analyze_market_competitiveness(job_data)
        
        # Create job posting
        job_posting = {
            "id": job_id,
            "basic_info": {
                "title": job_data.get("title", ""),
                "department": job_data.get("department", ""),
                "location": job_data.get("location", ""),
                "employment_type": job_data.get("employment_type", "full_time"),
                "salary_range": job_data.get("salary_range", {})
            },
            "requirements": {
                "required_skills": required_skills,
                "experience_level": experience_requirements,
                "competencies": competency_requirements,
                "education_requirements": job_data.get("education_requirements", []),
                "certification_requirements": job_data.get("certification_requirements", [])
            },
            "responsibilities": job_data.get("responsibilities", []),
            "benefits": job_data.get("benefits", []),
            "analysis": {
                "difficulty_score": difficulty_score,
                "market_competitiveness": market_analysis,
                "time_to_hire_estimate": self._estimate_time_to_hire(difficulty_score),
                "candidate_pool_size": self._estimate_candidate_pool_size(required_skills, experience_requirements)
            },
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "applications": [],
            "interviews_scheduled": 0
        }
        
        # Store job posting
        self.job_postings[job_id] = job_posting
        
        return job_posting
    
    async def _extract_job_requirements(self, job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and categorize job requirements"""
        requirements = []
        
        # Technical requirements
        tech_requirements = job_data.get("technical_requirements", [])
        for req in tech_requirements:
            requirements.append({
                "category": "technical",
                "skill": req,
                "mandatory": True,
                "priority": random.choice(["high", "medium", "low"]),
                "experience_years": random.randint(1, 5)
            })
        
        # Soft skill requirements
        soft_requirements = job_data.get("soft_requirements", [])
        for req in soft_requirements:
            requirements.append({
                "category": "soft",
                "skill": req,
                "mandatory": random.choice([True, False]),
                "priority": random.choice(["high", "medium", "low"]),
                "assessment_method": random.choice(["interview", "test", "reference"])
            })
        
        return requirements
    
    def _assess_experience_requirements(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess experience requirements for the job"""
        min_experience = job_data.get("min_experience_years", 0)
        max_experience = job_data.get("max_experience_years", min_experience + 5)
        
        if min_experience < 2:
            level = "entry"
        elif min_experience < 5:
            level = "mid"
        elif min_experience < 10:
            level = "senior"
        else:
            level = "expert"
        
        return {
            "level": level,
            "min_years": min_experience,
            "max_years": max_experience,
            "flexibility": random.choice(["strict", "flexible", "very_flexible"]),
            "industry_experience_required": job_data.get("industry_experience_required", False)
        }
    
    async def _extract_competency_requirements(self, job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract competency requirements"""
        competencies = []
        
        # Leadership requirements
        leadership_req = job_data.get("leadership_requirements", {})
        if leadership_req:
            competencies.append({
                "type": "leadership",
                "required": True,
                "level": leadership_req.get("level", "team_member"),
                "scope": leadership_req.get("scope", "individual")
            })
        
        # Communication requirements
        comm_req = job_data.get("communication_requirements", {})
        if comm_req:
            competencies.append({
                "type": "communication",
                "required": comm_req.get("required", True),
                "level": comm_req.get("level", "good"),
                "specific_skills": comm_req.get("specific_skills", [])
            })
        
        return competencies
    
    async def _calculate_job_difficulty(self, job_data: Dict[str, Any], 
                                      required_skills: List[Dict[str, Any]],
                                      experience_requirements: Dict[str, Any]) -> float:
        """Calculate job difficulty score"""
        difficulty = 0.0
        
        # Experience level difficulty
        exp_level = experience_requirements["level"]
        exp_difficulty = {
            "entry": 0.2,
            "mid": 0.5,
            "senior": 0.7,
            "expert": 0.9
        }
        difficulty += exp_difficulty.get(exp_level, 0.5)
        
        # Skills complexity
        tech_skills = [skill for skill in required_skills if skill["category"] == "technical"]
        skill_difficulty = min(len(tech_skills) * 0.1, 0.3)
        difficulty += skill_difficulty
        
        # Education requirements
        education_level = job_data.get("education_level", "bachelors")
        edu_difficulty = {
            "high_school": 0.1,
            "bachelors": 0.2,
            "masters": 0.3,
            "phd": 0.4
        }
        difficulty += edu_difficulty.get(education_level, 0.2)
        
        # Special requirements
        if job_data.get("certification_requirements"):
            difficulty += 0.1
        
        if job_data.get("security_clearance_required"):
            difficulty += 0.2
        
        return min(difficulty, 1.0)
    
    async def _analyze_market_competitiveness(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market competitiveness for the job"""
        # Simulate market analysis
        salary_range = job_data.get("salary_range", {})
        market_salary = random.randint(50000, 150000)
        
        offered_salary_min = salary_range.get("min", market_salary * 0.9)
        offered_salary_max = salary_range.get("max", market_salary * 1.1)
        
        competitiveness = 0.5
        if offered_salary_min > market_salary * 1.1:
            competitiveness = 0.8
        elif offered_salary_min < market_salary * 0.9:
            competitiveness = 0.3
        
        return {
            "market_salary_estimate": market_salary,
            "offer_competitiveness": competitiveness,
            "attractiveness_factors": [
                "competitive salary" if competitiveness > 0.7 else "market-rate salary",
                "growth opportunities",
                "company culture",
                "benefits package"
            ],
            "challenges": [
                "high competition" if competitiveness < 0.4 else "moderate competition",
                "skill shortage in market"
            ] if len(job_data.get("technical_requirements", [])) > 5 else []
        }
    
    def _estimate_time_to_hire(self, difficulty_score: float) -> int:
        """Estimate time to hire in days"""
        base_days = 30
        difficulty_multiplier = 1 + difficulty_score
        
        # Add randomness
        estimated_days = int(base_days * difficulty_multiplier * random.uniform(0.8, 1.2))
        return max(estimated_days, 14)  # Minimum 2 weeks
    
    def _estimate_candidate_pool_size(self, required_skills: List[Dict[str, Any]], 
                                    experience_requirements: Dict[str, Any]) -> int:
        """Estimate size of available candidate pool"""
        base_pool = 1000
        
        # Reduce pool based on experience level
        exp_reduction = {
            "entry": 0.8,
            "mid": 0.6,
            "senior": 0.3,
            "expert": 0.1
        }
        
        reduction_factor = exp_reduction.get(experience_requirements["level"], 0.5)
        
        # Reduce pool based on number of technical skills required
        tech_skills_count = len([skill for skill in required_skills if skill["category"] == "technical"])
        skill_reduction = max(0.1, 1 - (tech_skills_count * 0.1))
        
        estimated_pool = int(base_pool * reduction_factor * skill_reduction)
        return max(estimated_pool, 10)
    
    async def match_candidates_to_job(self, job_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Match candidates to job requirements"""
        if job_id not in self.job_postings:
            raise ValueError("Job not found")
        
        job = self.job_postings[job_id]
        job_requirements = job["requirements"]
        
        matches = []
        
        for candidate_id, candidate in self.candidate_profiles.items():
            # Calculate match score
            match_score = await self._calculate_match_score(candidate, job_requirements)
            
            if match_score > 0.3:  # Only include candidates with reasonable match
                match = {
                    "candidate_id": candidate_id,
                    "candidate": candidate,
                    "match_score": match_score,
                    "match_details": await self._analyze_match_details(candidate, job_requirements),
                    "recommendations": await self._generate_match_recommendations(candidate, job_requirements)
                }
                matches.append(match)
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:limit]
    
    async def _calculate_match_score(self, candidate: Dict[str, Any], 
                                   job_requirements: Dict[str, Any]) -> float:
        """Calculate how well a candidate matches job requirements"""
        score = 0.0
        max_score = 0.0
        
        # Experience match (30%)
        exp_weight = 0.3
        max_score += exp_weight
        
        candidate_exp = candidate["experience_level"]["years_experience"]
        required_exp = job_requirements["experience_level"]["min_years"]
        
        if candidate_exp >= required_exp:
            exp_score = min(candidate_exp / (required_exp + 2), 1.0)
        else:
            exp_score = candidate_exp / required_exp * 0.5
        
        score += exp_score * exp_weight
        
        # Skills match (40%)
        skills_weight = 0.4
        max_score += skills_weight
        
        required_skills = [req["skill"] for req in job_requirements["required_skills"]]
        candidate_skills = []
        for category_skills in candidate["skills"].values():
            candidate_skills.extend(category_skills)
        
        # Calculate skills overlap
        skill_matches = 0
        for req_skill in required_skills:
            for cand_skill in candidate_skills:
                if req_skill.lower() in cand_skill.lower() or cand_skill.lower() in req_skill.lower():
                    skill_matches += 1
                    break
        
        skills_score = min(skill_matches / max(len(required_skills), 1), 1.0)
        score += skills_score * skills_weight
        
        # Cultural fit (20%)
        cultural_weight = 0.2
        max_score += cultural_weight
        score += candidate["cultural_fit_score"] * cultural_weight
        
        # Education match (10%)
        edu_weight = 0.1
        max_score += edu_weight
        
        education = candidate["professional_info"]["education"]
        required_education = job_requirements.get("education_requirements", [])
        
        edu_score = 0.5 if education and required_education else 0.3
        score += edu_score * edu_weight
        
        return min(score / max_score, 1.0) if max_score > 0 else 0.0
    
    async def _analyze_match_details(self, candidate: Dict[str, Any], 
                                    job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze detailed match information"""
        details = {
            "strengths": [],
            "gaps": [],
            "additional_qualifications": [],
            "risk_factors": []
        }
        
        # Analyze skills
        candidate_skills = []
        for category_skills in candidate["skills"].values():
            candidate_skills.extend(category_skills)
        
        required_skills = [req["skill"] for req in job_requirements["required_skills"]]
        
        for req_skill in required_skills:
            found = False
            for cand_skill in candidate_skills:
                if req_skill.lower() in cand_skill.lower():
                    details["strengths"].append(f"Strong in {req_skill}")
                    found = True
                    break
            
            if not found:
                details["gaps"].append(f"Missing {req_skill}")
        
        # Additional qualifications
        if candidate["overall_score"] > 0.8:
            details["additional_qualifications"].append("Above-average overall qualifications")
        
        if candidate["cultural_fit_score"] > 0.8:
            details["strengths"].append("Excellent cultural fit")
        
        # Risk factors
        if candidate["bias_analysis"]["overall_bias_risk"] > 0.5:
            details["risk_factors"].append("Potential bias indicators detected")
        
        experience_years = candidate["experience_level"]["years_experience"]
        required_exp = job_requirements["experience_level"]["min_years"]
        if experience_years < required_exp:
            details["risk_factors"].append("Below required experience level")
        
        return details
    
    async def _generate_match_recommendations(self, candidate: Dict[str, Any], 
                                            job_requirements: Dict[str, Any]) -> List[str]:
        """Generate recommendations for candidate-job match"""
        recommendations = []
        
        if candidate["overall_score"] > 0.8:
            recommendations.append("Highly recommended - strong candidate")
        elif candidate["overall_score"] > 0.6:
            recommendations.append("Good candidate - worth interviewing")
        else:
            recommendations.append("Consider for alternative positions")
        
        # Skills-based recommendations
        candidate_skills = []
        for category_skills in candidate["skills"].values():
            candidate_skills.extend(category_skills)
        
        if len([skill for skill in candidate_skills if "leadership" in skill.lower()]) > 0:
            recommendations.append("Consider for leadership track")
        
        if candidate["cultural_fit_score"] > 0.8:
            recommendations.append("Strong cultural fit - fast-track process")
        
        # Bias mitigation
        if candidate["bias_analysis"]["overall_bias_risk"] > 0.4:
            recommendations.append("Use structured interview to minimize bias")
        
        return recommendations
    
    async def schedule_interview(self, candidate_id: str, job_id: str, 
                               interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule interview for candidate"""
        if candidate_id not in self.candidate_profiles:
            raise ValueError("Candidate not found")
        
        if job_id not in self.job_postings:
            raise ValueError("Job not found")
        
        interview_id = str(uuid.uuid4())
        
        # Create interview schedule
        interview = {
            "id": interview_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "interviewers": interview_data.get("interviewers", []),
            "scheduled_time": interview_data.get("scheduled_time"),
            "duration": interview_data.get("duration", 60),
            "type": interview_data.get("type", "phone"),
            "stage": interview_data.get("stage", "initial"),
            "questions": await self._generate_interview_questions(candidate_id, job_id),
            "evaluation_criteria": await self._create_evaluation_criteria(candidate_id, job_id),
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        # Store interview
        self.interview_schedules[interview_id] = interview
        
        # Update candidate and job
        self.candidate_profiles[candidate_id]["interview_history"].append(interview_id)
        self.job_postings[job_id]["interviews_scheduled"] += 1
        
        return interview
    
    async def _generate_interview_questions(self, candidate_id: str, job_id: str) -> List[Dict[str, Any]]:
        """Generate interview questions based on candidate and job"""
        questions = []
        
        candidate = self.candidate_profiles[candidate_id]
        job = self.job_postings[job_id]
        
        # Behavioral questions
        behavioral_questions = [
            {
                "type": "behavioral",
                "question": "Tell me about a challenging project you worked on and how you overcame obstacles.",
                "competency": "problem_solving",
                "weight": 0.2
            },
            {
                "type": "behavioral",
                "question": "Describe a time when you had to work with a difficult team member. How did you handle it?",
                "competency": "teamwork",
                "weight": 0.2
            }
        ]
        
        # Technical questions based on job requirements
        tech_requirements = job["requirements"]["required_skills"]
        technical_questions = []
        
        for req in tech_requirements[:3]:  # Top 3 requirements
            if req["category"] == "technical":
                technical_questions.append({
                    "type": "technical",
                    "question": f"How would you approach implementing {req['skill']} in a real-world scenario?",
                    "skill": req["skill"],
                    "weight": 0.3
                })
        
        # Culture fit questions
        culture_questions = [
            {
                "type": "cultural",
                "question": "What motivates you in your work, and how do you define success?",
                "competency": "motivation",
                "weight": 0.15
            }
        ]
        
        questions.extend(behavioral_questions)
        questions.extend(technical_questions)
        questions.extend(culture_questions)
        
        return questions
    
    async def _create_evaluation_criteria(self, candidate_id: str, job_id: str) -> List[Dict[str, Any]]:
        """Create evaluation criteria for interview"""
        candidate = self.candidate_profiles[candidate_id]
        job = self.job_postings[job_id]
        
        criteria = [
            {
                "competency": "technical_skills",
                "weight": 0.3,
                "scale": "1-5",
                "description": "Technical knowledge and application"
            },
            {
                "competency": "communication",
                "weight": 0.2,
                "scale": "1-5",
                "description": "Verbal and written communication skills"
            },
            {
                "competency": "problem_solving",
                "weight": 0.2,
                "scale": "1-5",
                "description": "Analytical thinking and solution approach"
            },
            {
                "competency": "cultural_fit",
                "weight": 0.15,
                "scale": "1-5",
                "description": "Alignment with company values and culture"
            },
            {
                "competency": "experience_relevance",
                "weight": 0.15,
                "scale": "1-5",
                "description": "Relevance of past experience to role"
            }
        ]
        
        return criteria
    
    async def get_recruitment_insights(self) -> Dict[str, Any]:
        """Generate recruitment insights and analytics"""
        insights = {
            "candidate_metrics": await self._calculate_candidate_metrics(),
            "job_metrics": await self._calculate_job_metrics(),
            "interview_metrics": await self._calculate_interview_metrics(),
            "bias_analysis": await self._analyze_bias_patterns(),
            "recommendations": await self._generate_recruitment_recommendations()
        }
        
        return insights
    
    async def _calculate_candidate_metrics(self) -> Dict[str, Any]:
        """Calculate candidate-related metrics"""
        if not self.candidate_profiles:
            return {"total_candidates": 0}
        
        candidates = list(self.candidate_profiles.values())
        
        return {
            "total_candidates": len(candidates),
            "average_score": sum(c["overall_score"] for c in candidates) / len(candidates),
            "score_distribution": {
                "excellent": len([c for c in candidates if c["overall_score"] > 0.8]),
                "good": len([c for c in candidates if 0.6 < c["overall_score"] <= 0.8]),
                "average": len([c for c in candidates if 0.4 < c["overall_score"] <= 0.6]),
                "below_average": len([c for c in candidates if c["overall_score"] <= 0.4])
            },
            "top_skills": self._get_top_skills(candidates),
            "experience_distribution": self._get_experience_distribution(candidates)
        }
    
    async def _calculate_job_metrics(self) -> Dict[str, Any]:
        """Calculate job-related metrics"""
        if not self.job_postings:
            return {"total_jobs": 0}
        
        jobs = list(self.job_postings.values())
        
        return {
            "total_jobs": len(jobs),
            "active_jobs": len([j for j in jobs if j["status"] == "active"]),
            "average_difficulty": sum(j["analysis"]["difficulty_score"] for j in jobs) / len(jobs),
            "time_to_hire_estimate": sum(j["analysis"]["time_to_hire_estimate"] for j in jobs) / len(jobs),
            "department_distribution": self._get_department_distribution(jobs),
            "salary_ranges": self._get_salary_ranges(jobs)
        }
    
    async def _calculate_interview_metrics(self) -> Dict[str, Any]:
        """Calculate interview-related metrics"""
        if not self.interview_schedules:
            return {"total_interviews": 0}
        
        interviews = list(self.interview_schedules.values())
        
        return {
            "total_interviews": len(interviews),
            "scheduled": len([i for i in interviews if i["status"] == "scheduled"]),
            "completed": len([i for i in interviews if i["status"] == "completed"]),
            "average_duration": sum(i["duration"] for i in interviews) / len(interviews),
            "stage_distribution": self._get_interview_stage_distribution(interviews)
        }
    
    async def _analyze_bias_patterns(self) -> Dict[str, Any]:
        """Analyze bias patterns in recruitment process"""
        if not self.candidate_profiles:
            return {"bias_analysis": "No data available"}
        
        candidates = list(self.candidate_profiles.values())
        
        # Analyze bias indicators
        avg_bias_risk = sum(c["bias_analysis"]["overall_bias_risk"] for c in candidates) / len(candidates)
        
        bias_recommendations = []
        if avg_bias_risk > 0.5:
            bias_recommendations.append("Implement blind resume screening")
            bias_recommendations.append("Use structured interview processes")
            bias_recommendations.append("Include diverse interview panels")
        
        return {
            "average_bias_risk": avg_bias_risk,
            "high_risk_candidates": len([c for c in candidates if c["bias_analysis"]["overall_bias_risk"] > 0.6]),
            "recommendations": bias_recommendations
        }
    
    async def _generate_recruitment_recommendations(self) -> List[str]:
        """Generate recruitment improvement recommendations"""
        recommendations = []
        
        # Based on candidate metrics
        if self.candidate_profiles:
            candidates = list(self.candidate_profiles.values())
            avg_score = sum(c["overall_score"] for c in candidates) / len(candidates)
            
            if avg_score < 0.6:
                recommendations.append("Consider expanding candidate sourcing channels")
                recommendations.append("Review job requirements for realism")
            
            if avg_score > 0.8:
                recommendations.append("Current sourcing is effective - maintain strategy")
        
        # Based on job metrics
        if self.job_postings:
            jobs = list(self.job_postings.values())
            avg_difficulty = sum(j["analysis"]["difficulty_score"] for j in jobs) / len(jobs)
            
            if avg_difficulty > 0.7:
                recommendations.append("Consider skill development programs for current employees")
                recommendations.append("Review if all requirements are essential")
        
        return recommendations
    
    def _get_top_skills(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get most common skills across candidates"""
        skill_counts = {}
        
        for candidate in candidates:
            for category_skills in candidate["skills"].values():
                for skill in category_skills:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by frequency
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [{"skill": skill, "count": count} for skill, count in top_skills]
    
    def _get_experience_distribution(self, candidates: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of experience levels"""
        distribution = {"entry": 0, "mid": 0, "senior": 0, "expert": 0}
        
        for candidate in candidates:
            level = candidate["experience_level"]["level"]
            distribution[level] += 1
        
        return distribution
    
    def _get_department_distribution(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of jobs by department"""
        distribution = {}
        
        for job in jobs:
            dept = job["basic_info"]["department"]
            distribution[dept] = distribution.get(dept, 0) + 1
        
        return distribution
    
    def _get_salary_ranges(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get salary range analysis"""
        salaries = []
        
        for job in jobs:
            salary_range = job["basic_info"]["salary_range"]
            if salary_range.get("min") and salary_range.get("max"):
                avg_salary = (salary_range["min"] + salary_range["max"]) / 2
                salaries.append(avg_salary)
        
        if not salaries:
            return {"message": "No salary data available"}
        
        return {
            "average_salary": sum(salaries) / len(salaries),
            "min_salary": min(salaries),
            "max_salary": max(salaries),
            "median_salary": sorted(salaries)[len(salaries) // 2]
        }
    
    def _get_interview_stage_distribution(self, interviews: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of interviews by stage"""
        distribution = {}
        
        for interview in interviews:
            stage = interview["stage"]
            distribution[stage] = distribution.get(stage, 0) + 1
        
        return distribution
    
    async def _update_talent_insights(self, candidate_profile: Dict[str, Any]):
        """Update talent insights based on new candidate"""
        if not self.talent_insights:
            self.talent_insights = {
                "talent_trends": {},
                "skill_demand": {},
                "salary_benchmarks": {},
                "retention_factors": {}
            }
        
        # Update skill demand
        for skill_category, skills in candidate_profile["skills"].items():
            for skill in skills:
                if skill not in self.talent_insights["skill_demand"]:
                    self.talent_insights["skill_demand"][skill] = 0
                self.talent_insights["skill_demand"][skill] += 1
    
    async def _update_recruitment_patterns(self, candidate_profile: Dict[str, Any]):
        """Update recruitment patterns based on new candidate"""
        if not self.recruitment_patterns:
            self.recruitment_patterns = {
                "successful_profiles": [],
                "common_characteristics": {},
                "success_factors": {}
            }
        
        # Update successful profiles if candidate score is high
        if candidate_profile["overall_score"] > 0.7:
            self.recruitment_patterns["successful_profiles"].append({
                "score": candidate_profile["overall_score"],
                "experience_level": candidate_profile["experience_level"]["level"],
                "skills": candidate_profile["skills"],
                "cultural_fit": candidate_profile["cultural_fit_score"]
            })
            
            # Keep only last 100 profiles
            if len(self.recruitment_patterns["successful_profiles"]) > 100:
                self.recruitment_patterns["successful_profiles"] = self.recruitment_patterns["successful_profiles"][-100:]

# Initialize Brain AI
brain_ai = BrainAI()

# Pydantic models
class CandidateProfile(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    location: str
    experience_years: int
    previous_roles: List[str] = []
    education: List[str] = []
    certifications: List[str] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    leadership_skills: List[str] = []
    skills: List[str] = []

class JobPosting(BaseModel):
    title: str
    department: str
    location: str
    employment_type: str = "full_time"
    min_experience_years: int
    max_experience_years: Optional[int] = None
    technical_requirements: List[str] = []
    soft_requirements: List[str] = []
    education_level: str = "bachelors"
    education_requirements: List[str] = []
    certification_requirements: List[str] = []
    responsibilities: List[str] = []
    benefits: List[str] = []
    salary_range: Dict[str, Any] = {}

class InterviewSchedule(BaseModel):
    candidate_id: str
    job_id: str
    interviewers: List[str]
    scheduled_time: str
    duration: int = 60
    interview_type: str = "phone"
    stage: str = "initial"

class MatchRequest(BaseModel):
    job_id: str
    limit: int = 10

# Initialize FastAPI app
app = FastAPI(title="Brain AI HR Recruitment System", version="1.0.0")

# Demo data generator
async def generate_demo_data():
    """Generate demo candidates and job postings"""
    # Demo candidates
    demo_candidates = [
        {
            "name": "Alice Johnson",
            "email": "alice.johnson@email.com",
            "location": "New York, NY",
            "experience_years": 5,
            "previous_roles": ["Software Developer", "Junior Developer"],
            "education": ["BS Computer Science"],
            "certifications": ["AWS Certified"],
            "technical_skills": ["Python", "JavaScript", "React", "Node.js"],
            "soft_skills": ["Communication", "Teamwork", "Problem-solving"],
            "leadership_skills": ["Mentoring"],
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Communication", "Teamwork", "Problem-solving", "Mentoring"]
        },
        {
            "name": "Bob Smith",
            "email": "bob.smith@email.com",
            "location": "San Francisco, CA",
            "experience_years": 8,
            "previous_roles": ["Senior Developer", "Tech Lead", "Developer"],
            "education": ["MS Software Engineering"],
            "certifications": ["AWS Solutions Architect"],
            "technical_skills": ["Python", "Java", "Spring", "Microservices", "Docker"],
            "soft_skills": ["Leadership", "Communication", "Strategic thinking"],
            "leadership_skills": ["Team leadership", "Project management"],
            "skills": ["Python", "Java", "Spring", "Microservices", "Docker", "Leadership", "Communication", "Strategic thinking", "Team leadership", "Project management"]
        },
        {
            "name": "Carol Davis",
            "email": "carol.davis@email.com",
            "location": "Austin, TX",
            "experience_years": 3,
            "previous_roles": ["Junior Developer", "Intern"],
            "education": ["BS Computer Science"],
            "certifications": [],
            "technical_skills": ["JavaScript", "HTML", "CSS", "Vue.js"],
            "soft_skills": ["Creativity", "Adaptability", "Collaboration"],
            "leadership_skills": [],
            "skills": ["JavaScript", "HTML", "CSS", "Vue.js", "Creativity", "Adaptability", "Collaboration"]
        }
    ]
    
    for candidate_data in demo_candidates:
        await brain_ai.process_candidate(candidate_data)
    
    # Demo job postings
    demo_jobs = [
        {
            "title": "Senior Software Engineer",
            "department": "Engineering",
            "location": "Remote",
            "employment_type": "full_time",
            "min_experience_years": 5,
            "max_experience_years": 10,
            "technical_requirements": ["Python", "JavaScript", "Microservices", "AWS"],
            "soft_requirements": ["Communication", "Leadership", "Problem-solving"],
            "education_level": "bachelors",
            "responsibilities": ["Lead development projects", "Mentor junior developers", "Architect scalable systems"],
            "benefits": ["Remote work", "Health insurance", "Stock options"],
            "salary_range": {"min": 120000, "max": 160000}
        },
        {
            "title": "Frontend Developer",
            "department": "Engineering",
            "location": "New York, NY",
            "employment_type": "full_time",
            "min_experience_years": 2,
            "max_experience_years": 5,
            "technical_requirements": ["JavaScript", "React", "HTML", "CSS"],
            "soft_requirements": ["Creativity", "Communication", "Attention to detail"],
            "education_level": "bachelors",
            "responsibilities": ["Develop user interfaces", "Collaborate with designers", "Optimize performance"],
            "benefits": ["Hybrid work", "Health insurance", "Learning budget"],
            "salary_range": {"min": 80000, "max": 110000}
        },
        {
            "title": "DevOps Engineer",
            "department": "Engineering",
            "location": "San Francisco, CA",
            "employment_type": "full_time",
            "min_experience_years": 3,
            "max_experience_years": 7,
            "technical_requirements": ["Docker", "Kubernetes", "AWS", "CI/CD"],
            "soft_requirements": ["Problem-solving", "Communication", "Automation mindset"],
            "education_level": "bachelors",
            "responsibilities": ["Manage infrastructure", "Automate deployments", "Monitor systems"],
            "benefits": ["Competitive salary", "Remote options", "Stock options"],
            "salary_range": {"min": 100000, "max": 140000}
        }
    ]
    
    for job_data in demo_jobs:
        await brain_ai.create_job_posting(job_data)

# Generate demo data on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Brain AI HR Recruitment System...")
    await generate_demo_data()
    logger.info(f"Demo data loaded. {len(brain_ai.candidate_profiles)} candidates, {len(brain_ai.job_postings)} jobs.")

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
        <title>Brain AI HR Recruitment System</title>
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
            
            .candidate-section, .job-section, .matching-section, .interview-section {
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
            
            .candidate-card, .job-card, .match-card {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }
            
            .candidate-name, .job-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            
            .candidate-info, .job-info {
                color: #495057;
                margin-bottom: 10px;
                line-height: 1.5;
            }
            
            .candidate-meta, .job-meta {
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
            
            .match-score {
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
            
            .insights-section {
                grid-column: 1 / -1;
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            .insights-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .insight-card {
                background: white;
                padding: 15px;
                border-radius: 6px;
                border: 1px solid #dee2e6;
                text-align: center;
            }
            
            .insight-number {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            
            .insight-label {
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
                <h1>Brain AI HR Recruitment</h1>
                <p>Intelligent recruitment and talent acquisition platform</p>
            </div>
            
            <div class="main-content">
                <div class="candidate-section">
                    <div class="section-title">Add Candidate</div>
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="candidateName" class="form-control" placeholder="Full name">
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" id="candidateEmail" class="form-control" placeholder="email@domain.com">
                    </div>
                    <div class="form-group">
                        <label>Location:</label>
                        <input type="text" id="candidateLocation" class="form-control" placeholder="City, State">
                    </div>
                    <div class="form-group">
                        <label>Experience Years:</label>
                        <input type="number" id="candidateExperience" class="form-control" min="0" max="50">
                    </div>
                    <div class="form-group">
                        <label>Technical Skills (comma-separated):</label>
                        <input type="text" id="candidateSkills" class="form-control" placeholder="Python, JavaScript, React">
                    </div>
                    <div class="form-group">
                        <label>Soft Skills (comma-separated):</label>
                        <input type="text" id="candidateSoftSkills" class="form-control" placeholder="Communication, Leadership">
                    </div>
                    <button class="btn" onclick="addCandidate()">Add Candidate</button>
                </div>
                
                <div class="job-section">
                    <div class="section-title">Create Job Posting</div>
                    <div class="form-group">
                        <label>Job Title:</label>
                        <input type="text" id="jobTitle" class="form-control" placeholder="Software Engineer">
                    </div>
                    <div class="form-group">
                        <label>Department:</label>
                        <select id="jobDepartment" class="form-control">
                            <option value="Engineering">Engineering</option>
                            <option value="Marketing">Marketing</option>
                            <option value="Sales">Sales</option>
                            <option value="HR">HR</option>
                            <option value="Finance">Finance</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Location:</label>
                        <input type="text" id="jobLocation" class="form-control" placeholder="City, State or Remote">
                    </div>
                    <div class="form-group">
                        <label>Min Experience Years:</label>
                        <input type="number" id="jobMinExp" class="form-control" min="0" max="50">
                    </div>
                    <div class="form-group">
                        <label>Required Skills (comma-separated):</label>
                        <input type="text" id="jobSkills" class="form-control" placeholder="Python, JavaScript, AWS">
                    </div>
                    <button class="btn" onclick="createJob()">Create Job</button>
                </div>
                
                <div class="matching-section">
                    <div class="section-title">Match Candidates</div>
                    <div class="form-group">
                        <label>Select Job:</label>
                        <select id="matchJob" class="form-control">
                            <option value="">Select a job...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Match Limit:</label>
                        <input type="number" id="matchLimit" class="form-control" value="5" min="1" max="20">
                    </div>
                    <button class="btn btn-success" onclick="findMatches()">Find Matches</button>
                </div>
                
                <div class="interview-section">
                    <div class="section-title">Schedule Interview</div>
                    <div class="form-group">
                        <label>Select Candidate:</label>
                        <select id="interviewCandidate" class="form-control">
                            <option value="">Select a candidate...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Select Job:</label>
                        <select id="interviewJob" class="form-control">
                            <option value="">Select a job...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Interview Time:</label>
                        <input type="datetime-local" id="interviewTime" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Interviewers (comma-separated):</label>
                        <input type="text" id="interviewers" class="form-control" placeholder="John Doe, Jane Smith">
                    </div>
                    <button class="btn btn-success" onclick="scheduleInterview()">Schedule Interview</button>
                </div>
                
                <div class="insights-section">
                    <div class="section-title">Recruitment Analytics</div>
                    <button class="btn" onclick="loadInsights()">Refresh Insights</button>
                    <div id="insightsContent" style="margin-top: 15px;">
                        <p style="color: #6c757d;">Click "Refresh Insights" to view recruitment analytics</p>
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
            async function addCandidate() {
                const name = document.getElementById('candidateName').value.trim();
                const email = document.getElementById('candidateEmail').value.trim();
                const location = document.getElementById('candidateLocation').value.trim();
                const experience = parseInt(document.getElementById('candidateExperience').value) || 0;
                const skills = document.getElementById('candidateSkills').value.split(',').map(s => s.trim()).filter(s => s);
                const softSkills = document.getElementById('candidateSoftSkills').value.split(',').map(s => s.trim()).filter(s => s);
                
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
                    const response = await fetch('/api/candidates', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            name: name,
                            email: email,
                            location: location,
                            experience_years: experience,
                            technical_skills: skills,
                            soft_skills: softSkills,
                            skills: [...skills, ...softSkills],
                            previous_roles: [],
                            education: [],
                            certifications: [],
                            leadership_skills: []
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="candidate-card">
                                <div class="candidate-name">${data.basic_info.name}</div>
                                <div class="candidate-info">Email: ${data.basic_info.email}</div>
                                <div class="candidate-info">Location: ${data.basic_info.location}</div>
                                <div class="candidate-info">Experience: ${data.professional_info.experience_years} years</div>
                                <div class="candidate-meta">
                                    <span class="score-badge">Overall Score: ${(data.overall_score * 100).toFixed(1)}%</span>
                                    <span class="score-badge">Cultural Fit: ${(data.cultural_fit_score * 100).toFixed(1)}%</span>
                                    <span>Experience Level: ${data.experience_level.level}</span>
                                </div>
                                <div class="skills">
                                    ${data.skills.technical.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                                    ${data.skills.soft.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                                </div>
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('candidateName').value = '';
                        document.getElementById('candidateEmail').value = '';
                        document.getElementById('candidateLocation').value = '';
                        document.getElementById('candidateExperience').value = '';
                        document.getElementById('candidateSkills').value = '';
                        document.getElementById('candidateSoftSkills').value = '';
                        
                        // Update dropdowns
                        loadCandidates();
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error adding candidate. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error adding candidate. Please try again.</p>';
                    console.error('Add candidate error:', error);
                }
            }
            
            async function createJob() {
                const title = document.getElementById('jobTitle').value.trim();
                const department = document.getElementById('jobDepartment').value;
                const location = document.getElementById('jobLocation').value.trim();
                const minExp = parseInt(document.getElementById('jobMinExp').value) || 0;
                const skills = document.getElementById('jobSkills').value.split(',').map(s => s.trim()).filter(s => s);
                
                if (!title) {
                    alert('Please provide job title');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/jobs', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            title: title,
                            department: department,
                            location: location,
                            min_experience_years: minExp,
                            technical_requirements: skills,
                            soft_requirements: [],
                            responsibilities: [],
                            benefits: [],
                            salary_range: {}
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="job-card">
                                <div class="job-title">${data.basic_info.title}</div>
                                <div class="job-info">Department: ${data.basic_info.department}</div>
                                <div class="job-info">Location: ${data.basic_info.location}</div>
                                <div class="job-info">Experience Required: ${data.requirements.experience_level.min_years}+ years</div>
                                <div class="job-meta">
                                    <span class="score-badge">Difficulty: ${(data.analysis.difficulty_score * 100).toFixed(1)}%</span>
                                    <span>Est. Time to Hire: ${data.analysis.time_to_hire_estimate} days</span>
                                    <span>Est. Candidate Pool: ${data.analysis.candidate_pool_size}</span>
                                </div>
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('jobTitle').value = '';
                        document.getElementById('jobLocation').value = '';
                        document.getElementById('jobMinExp').value = '';
                        document.getElementById('jobSkills').value = '';
                        
                        // Update dropdowns
                        loadJobs();
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error creating job. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error creating job. Please try again.</p>';
                    console.error('Create job error:', error);
                }
            }
            
            async function findMatches() {
                const jobId = document.getElementById('matchJob').value;
                const limit = parseInt(document.getElementById('matchLimit').value) || 5;
                
                if (!jobId) {
                    alert('Please select a job');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch(`/api/match/${jobId}?limit=${limit}`);
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        if (data.length === 0) {
                            resultsContent.innerHTML = '<p style="color: #6c757d; text-align: center;">No matching candidates found.</p>';
                            return;
                        }
                        
                        resultsContent.innerHTML = data.map(match => `
                            <div class="match-card">
                                <div class="candidate-name">${match.candidate.basic_info.name}</div>
                                <div class="candidate-info">${match.candidate.basic_info.email}</div>
                                <div class="candidate-info">Experience: ${match.candidate.professional_info.experience_years} years</div>
                                <div class="candidate-meta">
                                    <span class="match-score">Match Score: ${(match.match_score * 100).toFixed(1)}%</span>
                                    <span class="score-badge">Overall: ${(match.candidate.overall_score * 100).toFixed(1)}%</span>
                                    <span class="score-badge">Cultural Fit: ${(match.candidate.cultural_fit_score * 100).toFixed(1)}%</span>
                                </div>
                                <div style="margin-top: 10px;">
                                    <strong>Strengths:</strong> ${match.match_details.strengths.join(', ') || 'N/A'}
                                </div>
                                <div style="margin-top: 5px;">
                                    <strong>Recommendations:</strong> ${match.recommendations.join(', ')}
                                </div>
                                <div class="skills">
                                    ${Object.entries(match.candidate.skills).map(([category, skills]) => 
                                        skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')
                                    ).join('')}
                                </div>
                            </div>
                        `).join('');
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error finding matches. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error finding matches. Please try again.</p>';
                    console.error('Find matches error:', error);
                }
            }
            
            async function scheduleInterview() {
                const candidateId = document.getElementById('interviewCandidate').value;
                const jobId = document.getElementById('interviewJob').value;
                const interviewTime = document.getElementById('interviewTime').value;
                const interviewers = document.getElementById('interviewers').value.split(',').map(i => i.trim()).filter(i => i);
                
                if (!candidateId || !jobId || !interviewTime) {
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
                    const response = await fetch('/api/interviews', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            candidate_id: candidateId,
                            job_id: jobId,
                            interviewers: interviewers,
                            scheduled_time: interviewTime,
                            duration: 60,
                            interview_type: 'video',
                            stage: 'initial'
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="candidate-card">
                                <div class="candidate-name">Interview Scheduled</div>
                                <div class="candidate-info">Interview ID: ${data.id}</div>
                                <div class="candidate-info">Scheduled Time: ${data.scheduled_time}</div>
                                <div class="candidate-info">Duration: ${data.duration} minutes</div>
                                <div class="candidate-meta">
                                    <span class="score-badge">Type: ${data.type}</span>
                                    <span>Stage: ${data.stage}</span>
                                    <span>Interviewers: ${data.interviewers.length}</span>
                                </div>
                                <div style="margin-top: 15px;">
                                    <strong>Generated Questions:</strong>
                                    <ul style="margin-top: 5px; margin-left: 20px;">
                                        ${data.questions.slice(0, 3).map(q => `<li>${q.question}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('interviewCandidate').value = '';
                        document.getElementById('interviewJob').value = '';
                        document.getElementById('interviewTime').value = '';
                        document.getElementById('interviewers').value = '';
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error scheduling interview. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error scheduling interview. Please try again.</p>';
                    console.error('Schedule interview error:', error);
                }
            }
            
            async function loadInsights() {
                const insightsContent = document.getElementById('insightsContent');
                
                try {
                    const response = await fetch('/api/insights');
                    const data = await response.json();
                    
                    insightsContent.innerHTML = `
                        <div class="insights-grid">
                            <div class="insight-card">
                                <div class="insight-number">${data.candidate_metrics.total_candidates}</div>
                                <div class="insight-label">Total Candidates</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${data.job_metrics.total_jobs}</div>
                                <div class="insight-label">Job Postings</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${data.interview_metrics.total_interviews}</div>
                                <div class="insight-label">Interviews Scheduled</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${(data.candidate_metrics.average_score * 100).toFixed(1)}%</div>
                                <div class="insight-label">Avg Candidate Score</div>
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Score Distribution</h4>
                        <div style="margin-top: 10px;">
                            ${Object.entries(data.candidate_metrics.score_distribution).map(([category, count]) => `
                                <span class="skill-tag" style="margin-right: 5px; margin-bottom: 5px;">${category}: ${count}</span>
                            `).join('')}
                        </div>
                        
                        ${data.bias_analysis.average_bias_risk > 0 ? `
                            <h4 style="margin-top: 20px; color: #2c3e50;">Bias Analysis</h4>
                            <div style="margin-top: 10px;">
                                <span class="score-badge" style="margin-right: 5px; margin-bottom: 5px;">
                                    Avg Bias Risk: ${(data.bias_analysis.average_bias_risk * 100).toFixed(1)}%
                                </span>
                                <span class="score-badge" style="margin-right: 5px; margin-bottom: 5px;">
                                    High Risk Candidates: ${data.bias_analysis.high_risk_candidates}
                                </span>
                            </div>
                        ` : ''}
                        
                        ${data.recommendations.length > 0 ? `
                            <h4 style="margin-top: 20px; color: #2c3e50;">Recommendations</h4>
                            <div style="margin-top: 10px;">
                                ${data.recommendations.map(rec => `
                                    <div style="background: #fff3cd; padding: 10px; border-radius: 4px; margin-bottom: 5px;">
                                        ${rec}
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    `;
                    
                } catch (error) {
                    insightsContent.innerHTML = '<p style="color: #dc3545;">Error loading insights. Please try again.</p>';
                    console.error('Insights error:', error);
                }
            }
            
            async function loadCandidates() {
                try {
                    const response = await fetch('/api/candidates');
                    const candidates = await response.json();
                    
                    const candidateSelect = document.getElementById('interviewCandidate');
                    candidateSelect.innerHTML = '<option value="">Select a candidate...</option>';
                    
                    candidates.forEach(candidate => {
                        const option = document.createElement('option');
                        option.value = candidate.id;
                        option.textContent = `${candidate.basic_info.name} (${candidate.professional_info.experience_years} years)`;
                        candidateSelect.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error loading candidates:', error);
                }
            }
            
            async function loadJobs() {
                try {
                    const response = await fetch('/api/jobs');
                    const jobs = await response.json();
                    
                    const matchJobSelect = document.getElementById('matchJob');
                    const interviewJobSelect = document.getElementById('interviewJob');
                    
                    matchJobSelect.innerHTML = '<option value="">Select a job...</option>';
                    interviewJobSelect.innerHTML = '<option value="">Select a job...</option>';
                    
                    jobs.forEach(job => {
                        const option1 = document.createElement('option');
                        option1.value = job.id;
                        option1.textContent = job.basic_info.title;
                        matchJobSelect.appendChild(option1);
                        
                        const option2 = document.createElement('option');
                        option2.value = job.id;
                        option2.textContent = job.basic_info.title;
                        interviewJobSelect.appendChild(option2);
                    });
                } catch (error) {
                    console.error('Error loading jobs:', error);
                }
            }
            
            // Load initial data
            window.onload = function() {
                loadCandidates();
                loadJobs();
            };
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/candidates")
async def add_candidate(candidate: CandidateProfile):
    """Add new candidate to the system"""
    try:
        candidate_dict = candidate.dict()
        result = await brain_ai.process_candidate(candidate_dict)
        return result
    except Exception as e:
        logger.error(f"Error adding candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candidates")
async def get_candidates():
    """Get all candidates"""
    try:
        candidates = list(brain_ai.candidate_profiles.values())
        return candidates
    except Exception as e:
        logger.error(f"Error getting candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs")
async def create_job(job: JobPosting):
    """Create new job posting"""
    try:
        job_dict = job.dict()
        result = await brain_ai.create_job_posting(job_dict)
        return result
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def get_jobs():
    """Get all job postings"""
    try:
        jobs = list(brain_ai.job_postings.values())
        return jobs
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/match/{job_id}")
async def match_candidates_to_job(job_id: str, limit: int = 10):
    """Match candidates to a specific job"""
    try:
        matches = await brain_ai.match_candidates_to_job(job_id, limit)
        return matches
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error matching candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interviews")
async def schedule_interview(interview: InterviewSchedule):
    """Schedule interview for candidate"""
    try:
        interview_dict = interview.dict()
        result = await brain_ai.schedule_interview(
            interview_dict["candidate_id"],
            interview_dict["job_id"],
            interview_dict
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error scheduling interview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_recruitment_insights():
    """Get recruitment insights and analytics"""
    try:
        insights = await brain_ai.get_recruitment_insights()
        return insights
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interviews")
async def get_interviews():
    """Get all scheduled interviews"""
    try:
        interviews = list(brain_ai.interview_schedules.values())
        return interviews
    except Exception as e:
        logger.error(f"Error getting interviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")