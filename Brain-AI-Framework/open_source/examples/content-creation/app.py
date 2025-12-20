#!/usr/bin/env python3
"""
Content Creation System - Brain AI Example
AI-powered content generation and optimization platform
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
    """Brain AI Framework - Content Creation Core"""
    
    def __init__(self):
        self.content_templates = {}
        self.brand_voice = {}
        self.content_history = {}
        self.seo_patterns = {}
        self.audience_insights = {}
        self.creative_patterns = {}
        self.content_analytics = {}
        
    async def generate_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using Brain AI creative patterns"""
        content_id = str(uuid.uuid4())
        
        # Extract content requirements
        content_type = request.get("content_type", "article")
        topic = request.get("topic", "")
        target_audience = request.get("target_audience", "general")
        tone = request.get("tone", "professional")
        length = request.get("length", "medium")
        keywords = request.get("keywords", [])
        brand_guidelines = request.get("brand_guidelines", {})
        
        # Analyze creative requirements
        creative_analysis = await self._analyze_creative_requirements(
            content_type, topic, target_audience, tone, length
        )
        
        # Generate content outline
        outline = await self._generate_outline(content_type, topic, length, creative_analysis)
        
        # Generate main content
        main_content = await self._generate_main_content(
            content_type, topic, outline, tone, target_audience, keywords
        )
        
        # Apply brand voice
        branded_content = await self._apply_brand_voice(main_content, brand_guidelines)
        
        # Optimize for SEO
        seo_optimized_content = await self._optimize_seo(branded_content, keywords)
        
        # Create content entry
        content_entry = {
            "id": content_id,
            "content_type": content_type,
            "topic": topic,
            "target_audience": target_audience,
            "tone": tone,
            "length": length,
            "outline": outline,
            "main_content": main_content,
            "final_content": seo_optimized_content,
            "keywords": keywords,
            "brand_guidelines": brand_guidelines,
            "creative_analysis": creative_analysis,
            "seo_score": self._calculate_seo_score(seo_optimized_content, keywords),
            "readability_score": self._calculate_readability(seo_optimized_content),
            "generated_at": datetime.now().isoformat(),
            "word_count": len(seo_optimized_content.split()),
            "confidence": random.uniform(0.8, 0.95)
        }
        
        # Store in content history
        self.content_history[content_id] = content_entry
        
        # Update creative patterns
        await self._update_creative_patterns(content_entry)
        
        # Update analytics
        await self._update_content_analytics(content_entry)
        
        return content_entry
    
    async def _analyze_creative_requirements(self, content_type: str, topic: str, 
                                           target_audience: str, tone: str, length: str) -> Dict[str, Any]:
        """Analyze creative requirements for content generation"""
        analysis = {
            "complexity_level": self._determine_complexity(content_type, target_audience),
            "structure_type": self._determine_structure(content_type, length),
            "engagement_factors": self._identify_engagement_factors(content_type, target_audience),
            "call_to_action_style": self._determine_cta_style(content_type, tone),
            "visual_elements": self._suggest_visual_elements(content_type, topic),
            "narrative_approach": self._select_narrative_approach(content_type, target_audience)
        }
        
        return analysis
    
    def _determine_complexity(self, content_type: str, target_audience: str) -> str:
        """Determine content complexity based on type and audience"""
        complexity_map = {
            ("blog", "general"): "medium",
            ("blog", "expert"): "high",
            ("blog", "beginner"): "low",
            ("social", "general"): "low",
            ("social", "expert"): "medium",
            ("email", "general"): "medium",
            ("whitepaper", "expert"): "high",
            ("whitepaper", "general"): "medium",
            ("guide", "general"): "medium"
        }
        
        return complexity_map.get((content_type, target_audience), "medium")
    
    def _determine_structure(self, content_type: str, length: str) -> str:
        """Determine content structure based on type and length"""
        structure_map = {
            ("blog", "short"): "inverted_pyramid",
            ("blog", "medium"): "classic",
            ("blog", "long"): "pillar",
            ("social", "short"): "hook_body_close",
            ("email", "medium"): "aida",
            ("guide", "long"): "step_by_step",
            ("whitepaper", "long"): "academic"
        }
        
        return structure_map.get((content_type, length), "classic")
    
    def _identify_engagement_factors(self, content_type: str, target_audience: str) -> List[str]:
        """Identify engagement factors for the content"""
        engagement_map = {
            ("blog", "general"): ["storytelling", "examples", "statistics", "questions"],
            ("blog", "expert"): ["data", "case_studies", "research", "technical_details"],
            ("social", "general"): ["visuals", "hashtags", "trending_topics", "community"],
            ("email", "general"): ["personalization", "clear_cta", "value_proposition"],
            ("guide", "general"): ["step_by_step", "examples", "checklists", "actionable_tips"]
        }
        
        return engagement_map.get((content_type, target_audience), ["engagement", "value"])
    
    def _determine_cta_style(self, content_type: str, tone: str) -> str:
        """Determine call-to-action style"""
        cta_styles = {
            ("blog", "professional"): "subtle_informational",
            ("blog", "casual"): "conversational",
            ("social", "professional"): "direct_action",
            ("email", "professional"): "urgent_professional",
            ("guide", "professional"): "educational_cta"
        }
        
        return cta_styles.get((content_type, tone), "direct_action")
    
    def _suggest_visual_elements(self, content_type: str, topic: str) -> List[str]:
        """Suggest visual elements for content"""
        visual_suggestions = {
            "blog": ["header_image", "infographics", "charts", "screenshots"],
            "social": ["images", "memes", "quotes", "polls"],
            "email": ["hero_image", "dividers", "icons", "testimonials"],
            "guide": ["step_illustrations", "process_diagrams", "checklists", "templates"],
            "whitepaper": ["data_visualizations", "diagrams", "tables", "research_charts"]
        }
        
        return visual_suggestions.get(content_type, ["images", "text"])
    
    def _select_narrative_approach(self, content_type: str, target_audience: str) -> str:
        """Select narrative approach"""
        narrative_approaches = {
            ("blog", "general": "storytelling"),
            ("blog", "expert"): "analytical",
            ("guide", "general"): "instructional"),
            ("whitepaper", "expert"): "research_based"),
            ("social", "general"): "conversational")
        }
        
        return narrative_approaches.get((content_type, target_audience), "balanced")
    
    async def _generate_outline(self, content_type: str, topic: str, length: str, 
                               analysis: Dict[str, Any]) -> List[str]:
        """Generate content outline based on structure type"""
        outline_templates = {
            "classic": [
                f"Introduction: Understanding {topic}",
                f"Main Points About {topic}",
                f"Benefits and Applications",
                f"Practical Examples",
                f"Conclusion and Next Steps"
            ],
            "inverted_pyramid": [
                f"Key Takeaway About {topic}",
                f"Essential Information",
                f"Supporting Details"
            ],
            "pillar": [
                f"Introduction to {topic}",
                f"Fundamentals of {topic}",
                f"Advanced Concepts",
                f"Implementation Strategies",
                f"Best Practices",
                f"Case Studies",
                f"Future Trends",
                f"Conclusion"
            ],
            "aida": [
                f"Attention: Hook About {topic}",
                f"Interest: Key Information",
                f"Desire: Benefits and Value",
                f"Action: Next Steps"
            ],
            "step_by_step": [
                f"Getting Started with {topic}",
                f"Step 1: Foundation",
                f"Step 2: Implementation",
                f"Step 3: Optimization",
                f"Step 4: Advanced Techniques",
                f"Step 5: Monitoring and Maintenance"
            ]
        }
        
        structure = analysis["structure_type"]
        base_outline = outline_templates.get(structure, outline_templates["classic"])
        
        # Adjust outline based on length
        if length == "short" and len(base_outline) > 3:
            return base_outline[:3]
        elif length == "long" and len(base_outline) < 8:
            # Extend outline for long content
            return base_outline + [f"Deep Dive: {topic} Strategies", f"Advanced Tips and Tricks"]
        
        return base_outline
    
    async def _generate_main_content(self, content_type: str, topic: str, outline: List[str],
                                   tone: str, target_audience: str, keywords: List[str]) -> str:
        """Generate main content based on outline and requirements"""
        content_segments = []
        
        for i, section in enumerate(outline):
            # Generate content for each section
            segment = await self._generate_section_content(
                section, topic, tone, target_audience, keywords, content_type
            )
            content_segments.append(segment)
        
        # Combine all segments
        main_content = "\n\n".join(content_segments)
        
        # Apply content type specific formatting
        if content_type == "social":
            main_content = await self._format_social_content(main_content, keywords)
        elif content_type == "email":
            main_content = await self._format_email_content(main_content)
        
        return main_content
    
    async def _generate_section_content(self, section: str, topic: str, tone: str,
                                      target_audience: str, keywords: List[str], content_type: str) -> str:
        """Generate content for a specific section"""
        # Simulate content generation based on section type
        content_templates = {
            "introduction": f"{section.replace('Introduction:', '').replace('Introduction', '').strip()}\n\n"
                          f"In today's rapidly evolving landscape, understanding {topic} is more crucial than ever. "
                          f"This comprehensive guide will walk you through everything you need to know.",
            
            "main_points": f"Key aspects of {topic} include:\n\n"
                         f"• Fundamental concepts that form the foundation\n"
                         f"• Practical applications across different industries\n"
                         f"• Common challenges and how to overcome them\n"
                         f"• Best practices for implementation",
            
            "benefits": f"The benefits of mastering {topic} are numerous:\n\n"
                      f"1. Improved efficiency and productivity\n"
                      f"2. Enhanced decision-making capabilities\n"
                      f"3. Better competitive advantage\n"
                      f"4. Increased innovation opportunities",
            
            "examples": f"Practical examples of {topic} in action:\n\n"
                       f"Example 1: [Specific use case]\n"
                       f"Example 2: [Industry application]\n"
                       f"Example 3: [Success story]",
            
            "conclusion": f"In conclusion, {topic} represents a significant opportunity for growth and innovation. "
                         f"By applying the strategies and insights outlined in this guide, you'll be well-equipped "
                         f"to leverage these benefits in your own context."
        }
        
        # Determine section type and use appropriate template
        section_lower = section.lower()
        if "introduction" in section_lower or "getting started" in section_lower:
            template_key = "introduction"
        elif "main points" in section_lower or "fundamentals" in section_lower:
            template_key = "main_points"
        elif "benefits" in section_lower or "advantages" in section_lower:
            template_key = "benefits"
        elif "examples" in section_lower or "case studies" in section_lower:
            template_key = "examples"
        elif "conclusion" in section_lower or "next steps" in section_lower:
            template_key = "conclusion"
        else:
            # Generate generic section content
            template_key = "main_points"
        
        content = content_templates.get(template_key, f"{section}\n\nContent about {topic} goes here.")
        
        # Apply tone adjustments
        if tone == "casual":
            content = content.replace("crucial", "important").replace("comprehensive", "complete")
        elif tone == "professional":
            content = content.replace("In today's", "In the current business environment")
        
        # Add keywords naturally if provided
        if keywords:
            content += f"\n\nKeywords: {', '.join(keywords[:5])}"
        
        return content
    
    async def _apply_brand_voice(self, content: str, brand_guidelines: Dict[str, Any]) -> str:
        """Apply brand voice and guidelines to content"""
        if not brand_guidelines:
            return content
        
        # Apply voice adjustments
        voice = brand_guidelines.get("voice", "professional")
        if voice == "friendly":
            content = content.replace("customers", "friends").replace("clients", "partners")
        elif voice == "authoritative":
            content = content.replace("might", "will").replace("could", "should")
        
        # Apply style guidelines
        style = brand_guidelines.get("style", {})
        if style.get("avoid_jargon", False):
            # Simplify technical terms
            content = content.replace("utilize", "use").replace("leverage", "use")
        
        # Apply brand-specific phrases
        brand_phrases = brand_guidelines.get("phrases", [])
        for phrase in brand_phrases:
            content = content.replace("our company", phrase.get("replacement", "our company"))
        
        return content
    
    async def _optimize_seo(self, content: str, keywords: List[str]) -> str:
        """Optimize content for search engines"""
        if not keywords:
            return content
        
        # Add keyword density optimization
        content_words = content.lower().split()
        total_words = len(content_words)
        
        optimized_content = content
        
        # Ensure primary keyword appears in title area
        if keywords:
            primary_keyword = keywords[0]
            if primary_keyword.lower() not in optimized_content[:100].lower():
                optimized_content = f"{primary_keyword}: {optimized_content}"
        
        # Add meta description simulation
        description = f"Learn about {keywords[0] if keywords else 'this topic'} with our comprehensive guide."
        optimized_content = f"{description}\n\n{optimized_content}"
        
        # Add internal linking suggestions
        if len(keywords) > 1:
            optimized_content += f"\n\nRelated topics: {', '.join(keywords[1:3])}"
        
        return optimized_content
    
    def _calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate SEO optimization score"""
        if not keywords:
            return 0.5
        
        score = 0.0
        
        # Keyword density check
        content_lower = content.lower()
        keyword_density = sum(content_lower.count(kw.lower()) for kw in keywords) / len(content.split())
        if 0.01 <= keyword_density <= 0.03:  # Optimal density
            score += 0.3
        
        # Content length check
        word_count = len(content.split())
        if 300 <= word_count <= 2000:  # Good length range
            score += 0.2
        
        # Title optimization
        if any(kw.lower() in content[:100].lower() for kw in keywords):
            score += 0.2
        
        # Structure optimization
        if "\n\n" in content and content.count("\n") > 3:
            score += 0.15
        
        # Meta elements
        if "Learn about" in content or "comprehensive guide" in content:
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate content readability score"""
        words = content.split()
        sentences = content.split('.')
        
        # Simple readability metrics
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        avg_syllables_per_word = sum(len(word) for word in words) / len(words) if words else 0
        
        # Basic readability score (simplified Flesch-like)
        if avg_words_per_sentence <= 15 and avg_syllables_per_word <= 1.5:
            return 0.9
        elif avg_words_per_sentence <= 20 and avg_syllables_per_word <= 2.0:
            return 0.7
        else:
            return 0.5
    
    async def _format_social_content(self, content: str, keywords: List[str]) -> str:
        """Format content for social media platforms"""
        # Add hashtags
        if keywords:
            hashtags = " ".join([f"#{kw.replace(' ', '')}" for kw in keywords[:3]])
            content += f"\n\n{hashtags}"
        
        # Add engagement elements
        content += "\n\n💬 What do you think? Share your thoughts below!"
        
        return content
    
    async def _format_email_content(self, content: str) -> str:
        """Format content for email marketing"""
        # Add email structure
        header = "Subject: Important Update\n\n"
        greeting = "Hi there,\n\n"
        cta = "\n\nBest regards,\nThe Team\n\nP.S. Don't forget to check out our latest resources!"
        
        return header + greeting + content + cta
    
    async def _update_creative_patterns(self, content_entry: Dict[str, Any]):
        """Update creative patterns based on successful content"""
        content_type = content_entry["content_type"]
        seo_score = content_entry["seo_score"]
        
        if content_type not in self.creative_patterns:
            self.creative_patterns[content_type] = {
                "successful_structures": [],
                "effective_keywords": [],
                "average_performance": 0.0
            }
        
        # Update patterns if content performed well
        if seo_score > 0.7:
            patterns = self.creative_patterns[content_type]
            if content_entry["outline"] not in patterns["successful_structures"]:
                patterns["successful_structures"].append(content_entry["outline"])
            
            for keyword in content_entry["keywords"]:
                if keyword not in patterns["effective_keywords"]:
                    patterns["effective_keywords"].append(keyword)
    
    async def _update_content_analytics(self, content_entry: Dict[str, Any]):
        """Update content analytics"""
        if not self.content_analytics:
            self.content_analytics = {
                "total_content_created": 0,
                "content_by_type": {},
                "average_seo_score": 0.0,
                "average_readability": 0.0,
                "top_performing_topics": [],
                "keyword_performance": {}
            }
        
        analytics = self.content_analytics
        analytics["total_content_created"] += 1
        
        # Update content type distribution
        content_type = content_entry["content_type"]
        analytics["content_by_type"][content_type] = analytics["content_by_type"].get(content_type, 0) + 1
        
        # Update averages
        current_total = analytics["total_content_created"]
        analytics["average_seo_score"] = (
            (analytics["average_seo_score"] * (current_total - 1) + content_entry["seo_score"]) / current_total
        )
        analytics["average_readability"] = (
            (analytics["average_readability"] * (current_total - 1) + content_entry["readability_score"]) / current_total
        )
    
    async def get_content_insights(self) -> Dict[str, Any]:
        """Generate content creation insights and analytics"""
        if not self.content_history:
            return {"message": "No content available for insights"}
        
        insights = {
            "total_content_created": len(self.content_history),
            "content_distribution": {},
            "performance_metrics": {
                "average_seo_score": 0.0,
                "average_readability": 0.0,
                "top_performing_types": []
            },
            "creative_patterns": self.creative_patterns,
            "recent_trends": [],
            "optimization_suggestions": []
        }
        
        # Calculate performance metrics
        if self.content_history:
            seo_scores = [entry["seo_score"] for entry in self.content_history.values()]
            readability_scores = [entry["readability_score"] for entry in self.content_history.values()]
            
            insights["performance_metrics"]["average_seo_score"] = sum(seo_scores) / len(seo_scores)
            insights["performance_metrics"]["average_readability"] = sum(readability_scores) / len(readability_scores)
        
        # Content type distribution
        for entry in self.content_history.values():
            content_type = entry["content_type"]
            insights["content_distribution"][content_type] = insights["content_distribution"].get(content_type, 0) + 1
        
        # Generate suggestions
        if insights["performance_metrics"]["average_seo_score"] < 0.6:
            insights["optimization_suggestions"].append("Focus on keyword optimization and content structure")
        
        if insights["performance_metrics"]["average_readability"] < 0.7:
            insights["optimization_suggestions"].append("Simplify language and improve sentence structure")
        
        return insights

# Initialize Brain AI
brain_ai = BrainAI()

# Pydantic models
class ContentRequest(BaseModel):
    content_type: str = "article"
    topic: str
    target_audience: str = "general"
    tone: str = "professional"
    length: str = "medium"
    keywords: List[str] = []
    brand_guidelines: Dict[str, Any] = {}

class OptimizationRequest(BaseModel):
    content: str
    target_keywords: List[str]
    optimization_goals: List[str] = ["seo", "readability"]

# Initialize FastAPI app
app = FastAPI(title="Brain AI Content Creation System", version="1.0.0")

# Demo data generator
async def generate_demo_content():
    """Generate demo content to showcase system capabilities"""
    demo_requests = [
        {
            "content_type": "blog",
            "topic": "Digital Marketing Strategies",
            "target_audience": "marketing professionals",
            "tone": "professional",
            "length": "medium",
            "keywords": ["digital marketing", "SEO", "content strategy"],
            "brand_guidelines": {"voice": "authoritative", "style": {"avoid_jargon": True}}
        },
        {
            "content_type": "social",
            "topic": "Product Launch Announcement",
            "target_audience": "general",
            "tone": "casual",
            "length": "short",
            "keywords": ["product launch", "innovation", "technology"],
            "brand_guidelines": {"voice": "friendly"}
        },
        {
            "content_type": "guide",
            "topic": "Remote Work Best Practices",
            "target_audience": "remote workers",
            "tone": "professional",
            "length": "long",
            "keywords": ["remote work", "productivity", "work-life balance"],
            "brand_guidelines": {"voice": "helpful"}
        }
    ]
    
    for request in demo_requests:
        await brain_ai.generate_content(request)

# Generate demo content on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Brain AI Content Creation System...")
    await generate_demo_content()
    logger.info(f"Demo content created. System ready for content generation.")

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
        <title>Brain AI Content Creation System</title>
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
            
            .create-section, .optimize-section, .insights-section {
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
            
            .results {
                grid-column: 1 / -1;
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                border: 1px solid #e9ecef;
            }
            
            .content-output {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
                margin-bottom: 15px;
                max-height: 400px;
                overflow-y: auto;
            }
            
            .content-meta {
                display: flex;
                gap: 15px;
                font-size: 12px;
                color: #6c757d;
                flex-wrap: wrap;
                margin-top: 10px;
            }
            
            .score-badge {
                background: #28a745;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
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
            
            .tabs {
                display: flex;
                border-bottom: 1px solid #dee2e6;
                margin-bottom: 20px;
            }
            
            .tab {
                padding: 10px 20px;
                background: none;
                border: none;
                cursor: pointer;
                color: #6c757d;
                border-bottom: 2px solid transparent;
            }
            
            .tab.active {
                color: #667eea;
                border-bottom-color: #667eea;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
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
                <h1>Brain AI Content Creation</h1>
                <p>AI-powered content generation and optimization platform</p>
            </div>
            
            <div class="main-content">
                <div class="create-section">
                    <div class="section-title">Generate Content</div>
                    <div class="form-group">
                        <label>Content Type:</label>
                        <select id="contentType" class="form-control">
                            <option value="article">Article</option>
                            <option value="blog">Blog Post</option>
                            <option value="social">Social Media</option>
                            <option value="email">Email</option>
                            <option value="guide">Guide</option>
                            <option value="whitepaper">Whitepaper</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Topic:</label>
                        <input type="text" id="topic" class="form-control" placeholder="Enter your topic">
                    </div>
                    <div class="form-group">
                        <label>Target Audience:</label>
                        <select id="targetAudience" class="form-control">
                            <option value="general">General Public</option>
                            <option value="professionals">Professionals</option>
                            <option value="experts">Industry Experts</option>
                            <option value="beginners">Beginners</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Tone:</label>
                        <select id="tone" class="form-control">
                            <option value="professional">Professional</option>
                            <option value="casual">Casual</option>
                            <option value="friendly">Friendly</option>
                            <option value="authoritative">Authoritative</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Length:</label>
                        <select id="length" class="form-control">
                            <option value="short">Short</option>
                            <option value="medium" selected>Medium</option>
                            <option value="long">Long</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Keywords (comma-separated):</label>
                        <input type="text" id="keywords" class="form-control" placeholder="keyword1, keyword2, keyword3">
                    </div>
                    <button class="btn" onclick="generateContent()">Generate Content</button>
                </div>
                
                <div class="optimize-section">
                    <div class="section-title">Optimize Content</div>
                    <div class="form-group">
                        <label>Content to Optimize:</label>
                        <textarea id="contentToOptimize" class="form-control" placeholder="Paste your content here..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Target Keywords:</label>
                        <input type="text" id="optimizationKeywords" class="form-control" placeholder="keyword1, keyword2">
                    </div>
                    <div class="form-group">
                        <label>Optimization Goals:</label>
                        <div>
                            <input type="checkbox" id="goalSEO" value="seo" checked> SEO Optimization<br>
                            <input type="checkbox" id="goalReadability" value="readability" checked> Readability<br>
                            <input type="checkbox" id="goalEngagement" value="engagement"> Engagement
                        </div>
                    </div>
                    <button class="btn" onclick="optimizeContent()">Optimize Content</button>
                </div>
                
                <div class="insights-section" style="grid-column: 1 / -1;">
                    <div class="section-title">Content Analytics</div>
                    <button class="btn" onclick="loadInsights()">Refresh Insights</button>
                    <div id="insightsContent" style="margin-top: 15px;">
                        <p style="color: #6c757d;">Click "Refresh Insights" to view content analytics</p>
                    </div>
                </div>
                
                <div class="results" id="resultsSection" style="display: none;">
                    <div class="section-title">Generated Content</div>
                    <div id="resultsContent"></div>
                    <div class="loading" id="loadingIndicator">
                        <p>Generating content...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function generateContent() {
                const contentType = document.getElementById('contentType').value;
                const topic = document.getElementById('topic').value.trim();
                const targetAudience = document.getElementById('targetAudience').value;
                const tone = document.getElementById('tone').value;
                const length = document.getElementById('length').value;
                const keywords = document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(k => k);
                
                if (!topic) {
                    alert('Please enter a topic');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            content_type: contentType,
                            topic: topic,
                            target_audience: targetAudience,
                            tone: tone,
                            length: length,
                            keywords: keywords,
                            brand_guidelines: {}
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="content-output">
                                <h4>${data.content_type.charAt(0).toUpperCase() + data.content_type.slice(1)}: ${data.topic}</h4>
                                <div style="margin-top: 15px; line-height: 1.6;">${data.final_content.replace(/\\n/g, '<br>')}</div>
                                <div class="content-meta">
                                    <span class="score-badge">SEO Score: ${(data.seo_score * 100).toFixed(1)}%</span>
                                    <span class="score-badge">Readability: ${(data.readability_score * 100).toFixed(1)}%</span>
                                    <span>Word Count: ${data.word_count}</span>
                                    <span>Confidence: ${(data.confidence * 100).toFixed(1)}%</span>
                                </div>
                            </div>
                            
                            <div style="background: #e9ecef; padding: 15px; border-radius: 6px; margin-top: 15px;">
                                <h5>Content Outline</h5>
                                <ul style="margin-top: 10px;">
                                    ${data.outline.map(item => `<li>${item}</li>`).join('')}
                                </ul>
                            </div>
                            
                            <div style="background: #fff3cd; padding: 15px; border-radius: 6px; margin-top: 15px;">
                                <h5>Creative Analysis</h5>
                                <p><strong>Complexity:</strong> ${data.creative_analysis.complexity_level}</p>
                                <p><strong>Structure:</strong> ${data.creative_analysis.structure_type}</p>
                                <p><strong>Engagement Factors:</strong> ${data.creative_analysis.engagement_factors.join(', ')}</p>
                            </div>
                        `;
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error generating content. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error generating content. Please try again.</p>';
                    console.error('Content generation error:', error);
                }
            }
            
            async function optimizeContent() {
                const content = document.getElementById('contentToOptimize').value.trim();
                const keywords = document.getElementById('optimizationKeywords').value.split(',').map(k => k.trim()).filter(k => k);
                
                if (!content) {
                    alert('Please enter content to optimize');
                    return;
                }
                
                const goals = [];
                if (document.getElementById('goalSEO').checked) goals.push('seo');
                if (document.getElementById('goalReadability').checked) goals.push('readability');
                if (document.getElementById('goalEngagement').checked) goals.push('engagement');
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/optimize', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            content: content,
                            target_keywords: keywords,
                            optimization_goals: goals
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="content-output">
                                <h4>Optimized Content</h4>
                                <div style="margin-top: 15px; line-height: 1.6;">${data.optimized_content.replace(/\\n/g, '<br>')}</div>
                                <div class="content-meta">
                                    <span class="score-badge">SEO Score: ${(data.seo_score * 100).toFixed(1)}%</span>
                                    <span class="score-badge">Readability: ${(data.readability_score * 100).toFixed(1)}%</span>
                                    <span>Improvements: ${data.improvements.length}</span>
                                </div>
                            </div>
                            
                            <div style="background: #d4edda; padding: 15px; border-radius: 6px; margin-top: 15px;">
                                <h5>Optimization Suggestions</h5>
                                <ul style="margin-top: 10px;">
                                    ${data.improvements.map(improvement => `<li>${improvement}</li>`).join('')}
                                </ul>
                            </div>
                        `;
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error optimizing content. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error optimizing content. Please try again.</p>';
                    console.error('Content optimization error:', error);
                }
            }
            
            async function loadInsights() {
                const insightsContent = document.getElementById('insightsContent');
                
                try {
                    const response = await fetch('/api/insights');
                    const data = await response.json();
                    
                    if (data.total_content_created === 0) {
                        insightsContent.innerHTML = '<p style="color: #6c757d;">No content available for insights.</p>';
                        return;
                    }
                    
                    insightsContent.innerHTML = `
                        <div class="insights-grid">
                            <div class="insight-card">
                                <div class="insight-number">${data.total_content_created}</div>
                                <div class="insight-label">Content Created</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${(data.performance_metrics.average_seo_score * 100).toFixed(1)}%</div>
                                <div class="insight-label">Avg SEO Score</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${(data.performance_metrics.average_readability * 100).toFixed(1)}%</div>
                                <div class="insight-label">Avg Readability</div>
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Content Distribution</h4>
                        <div style="margin-top: 10px;">
                            ${Object.entries(data.content_distribution).map(([type, count]) => `
                                <span class="score-badge" style="margin-right: 5px; margin-bottom: 5px;">${type}: ${count}</span>
                            `).join('')}
                        </div>
                        
                        ${data.optimization_suggestions.length > 0 ? `
                            <h4 style="margin-top: 20px; color: #2c3e50;">Optimization Suggestions</h4>
                            <div style="margin-top: 10px;">
                                ${data.optimization_suggestions.map(suggestion => `
                                    <div style="background: #fff3cd; padding: 10px; border-radius: 4px; margin-bottom: 5px;">
                                        ${suggestion}
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
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/generate")
async def generate_content(request: ContentRequest):
    """Generate content using Brain AI"""
    try:
        request_dict = request.dict()
        result = await brain_ai.generate_content(request_dict)
        return result
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize")
async def optimize_content(request: OptimizationRequest):
    """Optimize existing content"""
    try:
        # Calculate current scores
        current_seo = brain_ai._calculate_seo_score(request.content, request.target_keywords)
        current_readability = brain_ai._calculate_readability(request.content)
        
        # Generate optimization suggestions
        improvements = []
        if "seo" in request.optimization_goals:
            if current_seo < 0.7:
                improvements.append("Add more relevant keywords naturally throughout the content")
                improvements.append("Improve content structure with clear headings and subheadings")
                improvements.append("Add meta description and internal linking")
            
        if "readability" in request.optimization_goals:
            if current_readability < 0.7:
                improvements.append("Break down long sentences into shorter, clearer ones")
                improvements.append("Use simpler vocabulary and avoid jargon")
                improvements.append("Add bullet points and numbered lists for better scanning")
        
        # Generate optimized content
        optimized_content = request.content
        
        # Apply keyword optimization
        if request.target_keywords and "seo" in request.optimization_goals:
            for keyword in request.target_keywords:
                if keyword.lower() not in optimized_content.lower():
                    # Add keyword in first paragraph naturally
                    first_paragraph = optimized_content.split('\n\n')[0]
                    optimized_content = optimized_content.replace(
                        first_paragraph, 
                        f"{keyword}: {first_paragraph}"
                    )
        
        # Calculate new scores
        new_seo = brain_ai._calculate_seo_score(optimized_content, request.target_keywords)
        new_readability = brain_ai._calculate_readability(optimized_content)
        
        return {
            "original_content": request.content,
            "optimized_content": optimized_content,
            "original_seo_score": current_seo,
            "seo_score": new_seo,
            "original_readability": current_readability,
            "readability_score": new_readability,
            "improvements": improvements,
            "optimized_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error optimizing content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_content_insights():
    """Get content creation insights and analytics"""
    try:
        insights = await brain_ai.get_content_insights()
        return insights
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content/history")
async def get_content_history():
    """Get content generation history"""
    try:
        history = list(brain_ai.content_history.values())
        # Sort by generation time (newest first)
        history.sort(key=lambda x: x["generated_at"], reverse=True)
        return history
    except Exception as e:
        logger.error(f"Error getting content history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")