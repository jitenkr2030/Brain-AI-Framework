#!/usr/bin/env python3
"""
Knowledge Management System - Brain AI Example
Advanced knowledge management and organizational intelligence
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
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainAI:
    """Brain AI Framework - Knowledge Management Core"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.memory_clusters = {}
        self.associations = {}
        self.learning_patterns = {}
        self.insights_cache = {}
        
    async def process_knowledge(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process and integrate new knowledge"""
        knowledge_id = str(uuid.uuid4())
        
        # Extract concepts and entities
        concepts = await self._extract_concepts(content)
        entities = await self._extract_entities(content)
        
        # Create knowledge entry
        knowledge_entry = {
            "id": knowledge_id,
            "content": content,
            "metadata": metadata,
            "concepts": concepts,
            "entities": entities,
            "timestamp": datetime.now().isoformat(),
            "relevance_score": 0.0,
            "usage_count": 0,
            "last_accessed": datetime.now().isoformat(),
            "confidence": random.uniform(0.7, 0.95)
        }
        
        # Store in knowledge base
        self.knowledge_base[knowledge_id] = knowledge_entry
        
        # Update memory clusters
        await self._update_memory_clusters(knowledge_id, concepts, entities)
        
        # Create associations
        await self._create_associations(knowledge_id, concepts, entities)
        
        # Update relevance scores
        await self._update_relevance_scores()
        
        return knowledge_entry
    
    async def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content"""
        # Simulate concept extraction
        concepts = []
        words = content.lower().split()
        
        # Common concept patterns
        concept_keywords = {
            "technology": ["ai", "machine learning", "algorithm", "data", "system", "software", "hardware"],
            "business": ["strategy", "market", "customer", "revenue", "growth", "profit", "management"],
            "research": ["study", "analysis", "methodology", "findings", "conclusion", "hypothesis"],
            "process": ["workflow", "procedure", "step", "phase", "implementation", "deployment"],
            "people": ["team", "employee", "manager", "customer", "user", "stakeholder"]
        }
        
        for category, keywords in concept_keywords.items():
            for word in words:
                if any(keyword in word for keyword in keywords):
                    concepts.append(category)
                    break
        
        return list(set(concepts))
    
    async def _extract_entities(self, content: str) -> List[str]:
        """Extract named entities from content"""
        # Simulate entity extraction
        entities = []
        words = content.split()
        
        # Simple entity patterns
        for word in words:
            if word.istitle() and len(word) > 2:
                entities.append(word)
            if word.startswith(('Dr.', 'Mr.', 'Ms.', 'Prof.')):
                entities.append(word)
        
        return list(set(entities))
    
    async def _update_memory_clusters(self, knowledge_id: str, concepts: List[str], entities: List[str]):
        """Update memory clusters based on concepts and entities"""
        for concept in concepts:
            if concept not in self.memory_clusters:
                self.memory_clusters[concept] = []
            if knowledge_id not in self.memory_clusters[concept]:
                self.memory_clusters[concept].append(knowledge_id)
        
        for entity in entities:
            if entity not in self.memory_clusters:
                self.memory_clusters[entity] = []
            if knowledge_id not in self.memory_clusters[entity]:
                self.memory_clusters[entity].append(knowledge_id)
    
    async def _create_associations(self, knowledge_id: str, concepts: List[str], entities: List[str]):
        """Create associations between knowledge items"""
        if knowledge_id not in self.associations:
            self.associations[knowledge_id] = {
                "related_knowledge": [],
                "similar_concepts": [],
                "shared_entities": []
            }
        
        # Find related knowledge through shared concepts/entities
        for existing_id, entry in self.knowledge_base.items():
            if existing_id != knowledge_id:
                shared_concepts = set(concepts) & set(entry.get("concepts", []))
                shared_entities = set(entities) & set(entry.get("entities", []))
                
                if shared_concepts or shared_entities:
                    self.associations[knowledge_id]["related_knowledge"].append({
                        "id": existing_id,
                        "shared_concepts": list(shared_concepts),
                        "shared_entities": list(shared_entities),
                        "strength": len(shared_concepts) + len(shared_entities)
                    })
    
    async def _update_relevance_scores(self):
        """Update relevance scores based on usage and associations"""
        for knowledge_id, entry in self.knowledge_base.items():
            # Base score from usage
            base_score = entry["usage_count"] * 0.1
            
            # Association boost
            if knowledge_id in self.associations:
                association_boost = len(self.associations[knowledge_id]["related_knowledge"]) * 0.05
            else:
                association_boost = 0
            
            # Confidence factor
            confidence_factor = entry.get("confidence", 0.8)
            
            entry["relevance_score"] = min(base_score + association_boost + confidence_factor, 1.0)
    
    async def query_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query knowledge base using semantic search"""
        query_concepts = await self._extract_concepts(query)
        query_entities = await self._extract_entities(query)
        
        results = []
        
        for knowledge_id, entry in self.knowledge_base.items():
            # Calculate semantic similarity
            content_similarity = self._calculate_text_similarity(query.lower(), entry["content"].lower())
            concept_similarity = len(set(query_concepts) & set(entry.get("concepts", []))) / max(len(query_concepts), 1)
            entity_similarity = len(set(query_entities) & set(entry.get("entities", []))) / max(len(query_entities), 1)
            
            # Combined relevance score
            total_score = (
                content_similarity * 0.4 +
                concept_similarity * 0.3 +
                entity_similarity * 0.2 +
                entry["relevance_score"] * 0.1
            )
            
            results.append({
                "knowledge": entry,
                "relevance_score": total_score,
                "match_details": {
                    "content_similarity": content_similarity,
                    "concept_similarity": concept_similarity,
                    "entity_similarity": entity_similarity
                }
            })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word overlap"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    async def get_insights(self) -> Dict[str, Any]:
        """Generate knowledge insights and analytics"""
        if not self.knowledge_base:
            return {"message": "No knowledge base available"}
        
        # Calculate analytics
        total_knowledge = len(self.knowledge_base)
        concept_distribution = {}
        entity_frequency = {}
        
        for entry in self.knowledge_base.values():
            for concept in entry.get("concepts", []):
                concept_distribution[concept] = concept_distribution.get(concept, 0) + 1
            
            for entity in entry.get("entities", []):
                entity_frequency[entity] = entity_frequency.get(entity, 0) + 1
        
        # Find trending concepts
        sorted_concepts = sorted(concept_distribution.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate knowledge growth
        recent_knowledge = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for entry in self.knowledge_base.values():
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date > cutoff_date:
                recent_knowledge.append(entry)
        
        insights = {
            "total_knowledge_items": total_knowledge,
            "recent_additions": len(recent_knowledge),
            "top_concepts": sorted_concepts[:10],
            "most_mentioned_entities": sorted(entity_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            "knowledge_distribution": concept_distribution,
            "memory_clusters": len(self.memory_clusters),
            "associations_created": sum(len(assoc.get("related_knowledge", [])) for assoc in self.associations.values()),
            "average_confidence": sum(entry.get("confidence", 0) for entry in self.knowledge_base.values()) / total_knowledge,
            "insights_generated_at": datetime.now().isoformat()
        }
        
        return insights
    
    async def learn_from_feedback(self, knowledge_id: str, feedback_type: str, rating: float):
        """Learn from user feedback to improve knowledge relevance"""
        if knowledge_id in self.knowledge_base:
            entry = self.knowledge_base[knowledge_id]
            
            # Update learning patterns
            pattern_key = f"{feedback_type}_{rating}"
            if pattern_key not in self.learning_patterns:
                self.learning_patterns[pattern_key] = 0
            self.learning_patterns[pattern_key] += 1
            
            # Adjust relevance based on feedback
            feedback_weight = (rating - 0.5) * 0.2  # Scale feedback to reasonable weight
            entry["relevance_score"] = max(0.0, min(1.0, entry["relevance_score"] + feedback_weight))
            
            # Update confidence based on positive feedback
            if rating > 0.7:
                entry["confidence"] = min(1.0, entry["confidence"] + 0.05)
            elif rating < 0.3:
                entry["confidence"] = max(0.0, entry["confidence"] - 0.05)

# Initialize Brain AI
brain_ai = BrainAI()

# Pydantic models
class KnowledgeEntry(BaseModel):
    content: str
    title: Optional[str] = ""
    category: Optional[str] = ""
    tags: List[str] = []
    source: Optional[str] = ""
    priority: Optional[str] = "medium"

class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class FeedbackRequest(BaseModel):
    knowledge_id: str
    feedback_type: str
    rating: float

# Initialize FastAPI app
app = FastAPI(title="Brain AI Knowledge Management System", version="1.0.0")

# Demo data generator
async def generate_demo_data():
    """Generate demo knowledge entries"""
    demo_entries = [
        {
            "content": "Machine Learning algorithms have revolutionized data analysis in recent years. Deep learning models, particularly neural networks, have shown remarkable success in image recognition, natural language processing, and predictive analytics. The key to their effectiveness lies in their ability to learn complex patterns from large datasets.",
            "title": "Introduction to Machine Learning",
            "category": "Technology",
            "tags": ["ML", "algorithms", "neural networks", "data analysis"],
            "source": "AI Research Paper",
            "priority": "high"
        },
        {
            "content": "Customer relationship management (CRM) systems are essential for modern business operations. They help companies manage interactions with current and potential customers, streamline sales processes, and improve customer service. Key features include contact management, sales tracking, and automated marketing campaigns.",
            "title": "CRM System Implementation",
            "category": "Business",
            "tags": ["CRM", "customer management", "sales", "automation"],
            "source": "Business Strategy Guide",
            "priority": "high"
        },
        {
            "content": "Project management methodologies like Agile and Scrum have transformed how teams collaborate and deliver projects. These frameworks emphasize iterative development, continuous feedback, and adaptive planning. Key ceremonies include daily standups, sprint planning, and retrospectives.",
            "title": "Agile Project Management",
            "category": "Process",
            "tags": ["Agile", "Scrum", "project management", "team collaboration"],
            "source": "Management Handbook",
            "priority": "medium"
        },
        {
            "content": "Data security and privacy regulations such as GDPR and CCPA require organizations to implement robust data protection measures. This includes data encryption, access controls, regular security audits, and user consent management. Non-compliance can result in significant fines and reputational damage.",
            "title": "Data Privacy Compliance",
            "category": "Compliance",
            "tags": ["GDPR", "data security", "privacy", "compliance"],
            "source": "Legal Documentation",
            "priority": "high"
        },
        {
            "content": "Cloud computing offers scalable infrastructure and services that can reduce operational costs and improve business agility. Key services include Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). Popular providers include AWS, Azure, and Google Cloud.",
            "title": "Cloud Computing Strategy",
            "category": "Technology",
            "tags": ["cloud computing", "AWS", "Azure", "scalability", "IaaS", "PaaS", "SaaS"],
            "source": "Technology Guide",
            "priority": "medium"
        },
        {
            "content": "Effective communication is crucial for team success. This includes active listening, clear articulation of ideas, appropriate use of digital communication tools, and regular feedback sessions. Non-verbal communication and emotional intelligence also play important roles in professional interactions.",
            "title": "Team Communication Best Practices",
            "category": "People",
            "tags": ["communication", "teamwork", "leadership", "collaboration"],
            "source": "HR Manual",
            "priority": "medium"
        },
        {
            "content": "Financial planning involves budgeting, forecasting, and investment analysis. Key components include cash flow management, risk assessment, and portfolio diversification. Tools like Excel, financial modeling software, and investment tracking applications can streamline these processes.",
            "title": "Financial Planning Fundamentals",
            "category": "Finance",
            "tags": ["budgeting", "forecasting", "investment", "cash flow", "risk management"],
            "source": "Finance Textbook",
            "priority": "high"
        },
        {
            "content": "Quality assurance processes ensure that products and services meet specified requirements and standards. This includes testing methodologies, defect tracking, continuous improvement cycles, and compliance verification. Automation tools can significantly enhance QA efficiency and accuracy.",
            "title": "Quality Assurance Framework",
            "category": "Process",
            "tags": ["QA", "testing", "quality control", "automation", "compliance"],
            "source": "QA Handbook",
            "priority": "medium"
        },
        {
            "content": "Change management is critical for successful organizational transformations. It involves preparing, supporting, and helping individuals and teams adopt new processes, technologies, or organizational structures. Key elements include stakeholder engagement, communication plans, and training programs.",
            "title": "Change Management Strategy",
            "category": "Management",
            "tags": ["change management", "transformation", "stakeholder", "training"],
            "source": "Management Guide",
            "priority": "medium"
        },
        {
            "content": "Digital marketing strategies encompass search engine optimization (SEO), content marketing, social media engagement, and email campaigns. Measuring ROI through analytics and A/B testing is essential for optimizing marketing effectiveness and budget allocation.",
            "title": "Digital Marketing Overview",
            "category": "Marketing",
            "tags": ["digital marketing", "SEO", "content marketing", "analytics", "ROI"],
            "source": "Marketing Playbook",
            "priority": "medium"
        }
    ]
    
    for entry_data in demo_entries:
        metadata = {
            "title": entry_data["title"],
            "category": entry_data["category"],
            "tags": entry_data["tags"],
            "source": entry_data["source"],
            "priority": entry_data["priority"]
        }
        await brain_ai.process_knowledge(entry_data["content"], metadata)

# Generate demo data on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Brain AI Knowledge Management System...")
    await generate_demo_data()
    logger.info(f"Demo data loaded. Knowledge base contains {len(brain_ai.knowledge_base)} entries.")

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
        <title>Brain AI Knowledge Management System</title>
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
            
            .search-section, .add-section, .insights-section {
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
            
            .search-box {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
                margin-bottom: 15px;
            }
            
            .search-box:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            
            .btn-secondary {
                background: #6c757d;
                margin-left: 10px;
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
            
            textarea.form-control {
                height: 80px;
                resize: vertical;
            }
            
            .results {
                grid-column: 1 / -1;
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                border: 1px solid #e9ecef;
            }
            
            .knowledge-item {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }
            
            .knowledge-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            
            .knowledge-content {
                color: #495057;
                margin-bottom: 10px;
                line-height: 1.5;
            }
            
            .knowledge-meta {
                display: flex;
                gap: 15px;
                font-size: 12px;
                color: #6c757d;
                flex-wrap: wrap;
            }
            
            .relevance-score {
                background: #28a745;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
            }
            
            .tags {
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
                margin-top: 8px;
            }
            
            .tag {
                background: #e9ecef;
                color: #495057;
                padding: 2px 8px;
                border-radius: 10px;
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
                <h1>Brain AI Knowledge Management</h1>
                <p>Intelligent knowledge organization and retrieval system powered by Brain AI</p>
            </div>
            
            <div class="main-content">
                <div class="search-section">
                    <div class="section-title">Search Knowledge</div>
                    <input type="text" id="searchQuery" class="search-box" placeholder="Search for knowledge, concepts, or topics...">
                    <div>
                        <button class="btn" onclick="searchKnowledge()">Search</button>
                        <button class="btn btn-secondary" onclick="clearResults()">Clear</button>
                    </div>
                </div>
                
                <div class="add-section">
                    <div class="section-title">Add Knowledge</div>
                    <div class="form-group">
                        <label>Title:</label>
                        <input type="text" id="knowledgeTitle" class="form-control" placeholder="Knowledge title">
                    </div>
                    <div class="form-group">
                        <label>Content:</label>
                        <textarea id="knowledgeContent" class="form-control" placeholder="Enter knowledge content..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Category:</label>
                        <input type="text" id="knowledgeCategory" class="form-control" placeholder="Category">
                    </div>
                    <div class="form-group">
                        <label>Tags (comma-separated):</label>
                        <input type="text" id="knowledgeTags" class="form-control" placeholder="tag1, tag2, tag3">
                    </div>
                    <button class="btn" onclick="addKnowledge()">Add Knowledge</button>
                </div>
                
                <div class="insights-section" style="grid-column: 1 / -1;">
                    <div class="section-title">Knowledge Insights</div>
                    <button class="btn" onclick="loadInsights()">Refresh Insights</button>
                    <div id="insightsContent" style="margin-top: 15px;">
                        <p style="color: #6c757d;">Click "Refresh Insights" to view knowledge analytics</p>
                    </div>
                </div>
                
                <div class="results" id="resultsSection" style="display: none;">
                    <div class="section-title">Search Results</div>
                    <div id="resultsContent"></div>
                    <div class="loading" id="loadingIndicator">
                        <p>Searching knowledge base...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function searchKnowledge() {
                const query = document.getElementById('searchQuery').value.trim();
                if (!query) {
                    alert('Please enter a search query');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            limit: 10
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (data.length === 0) {
                        resultsContent.innerHTML = '<p style="color: #6c757d; text-align: center;">No knowledge found matching your query.</p>';
                        return;
                    }
                    
                    resultsContent.innerHTML = data.map(item => `
                        <div class="knowledge-item">
                            <div class="knowledge-title">${item.knowledge.metadata.title || 'Untitled Knowledge'}</div>
                            <div class="knowledge-content">${item.knowledge.content.substring(0, 200)}${item.knowledge.content.length > 200 ? '...' : ''}</div>
                            <div class="knowledge-meta">
                                <span class="relevance-score">Relevance: ${(item.relevance_score * 100).toFixed(1)}%</span>
                                <span>Category: ${item.knowledge.metadata.category || 'Unknown'}</span>
                                <span>Source: ${item.knowledge.metadata.source || 'Unknown'}</span>
                                <span>Confidence: ${(item.knowledge.confidence * 100).toFixed(1)}%</span>
                            </div>
                            <div class="tags">
                                ${(item.knowledge.metadata.tags || []).map(tag => `<span class="tag">${tag}</span>`).join('')}
                            </div>
                        </div>
                    `).join('');
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error searching knowledge base. Please try again.</p>';
                    console.error('Search error:', error);
                }
            }
            
            async function addKnowledge() {
                const title = document.getElementById('knowledgeTitle').value.trim();
                const content = document.getElementById('knowledgeContent').value.trim();
                const category = document.getElementById('knowledgeCategory').value.trim();
                const tags = document.getElementById('knowledgeTags').value.split(',').map(tag => tag.trim()).filter(tag => tag);
                
                if (!content) {
                    alert('Please enter knowledge content');
                    return;
                }
                
                const metadata = {
                    title: title,
                    category: category,
                    tags: tags,
                    source: 'User Input',
                    priority: 'medium'
                };
                
                try {
                    const response = await fetch('/api/knowledge', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            content: content,
                            metadata: metadata
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert('Knowledge added successfully!');
                        document.getElementById('knowledgeTitle').value = '';
                        document.getElementById('knowledgeContent').value = '';
                        document.getElementById('knowledgeCategory').value = '';
                        document.getElementById('knowledgeTags').value = '';
                    } else {
                        alert('Error adding knowledge: ' + data.detail);
                    }
                    
                } catch (error) {
                    alert('Error adding knowledge. Please try again.');
                    console.error('Add knowledge error:', error);
                }
            }
            
            async function loadInsights() {
                const insightsContent = document.getElementById('insightsContent');
                
                try {
                    const response = await fetch('/api/insights');
                    const data = await response.json();
                    
                    if (data.total_knowledge_items === 0) {
                        insightsContent.innerHTML = '<p style="color: #6c757d;">No knowledge available for insights.</p>';
                        return;
                    }
                    
                    insightsContent.innerHTML = `
                        <div class="insights-grid">
                            <div class="insight-card">
                                <div class="insight-number">${data.total_knowledge_items}</div>
                                <div class="insight-label">Total Knowledge</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${data.recent_additions}</div>
                                <div class="insight-label">Recent Additions</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${data.memory_clusters}</div>
                                <div class="insight-label">Memory Clusters</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${data.associations_created}</div>
                                <div class="insight-label">Associations</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number">${(data.average_confidence * 100).toFixed(1)}%</div>
                                <div class="insight-label">Avg Confidence</div>
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Top Concepts</h4>
                        <div style="margin-top: 10px;">
                            ${data.top_concepts.slice(0, 5).map(concept => `
                                <span class="tag" style="margin-right: 5px; margin-bottom: 5px;">${concept[0]} (${concept[1]})</span>
                            `).join('')}
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Most Mentioned Entities</h4>
                        <div style="margin-top: 10px;">
                            ${data.most_mentioned_entities.slice(0, 5).map(entity => `
                                <span class="tag" style="margin-right: 5px; margin-bottom: 5px;">${entity[0]} (${entity[1]})</span>
                            `).join('')}
                        </div>
                    `;
                    
                } catch (error) {
                    insightsContent.innerHTML = '<p style="color: #dc3545;">Error loading insights. Please try again.</p>';
                    console.error('Insights error:', error);
                }
            }
            
            function clearResults() {
                document.getElementById('resultsSection').style.display = 'none';
                document.getElementById('resultsContent').innerHTML = '';
            }
            
            // Search on Enter key
            document.getElementById('searchQuery').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchKnowledge();
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/knowledge")
async def add_knowledge_entry(entry: KnowledgeEntry):
    """Add new knowledge entry to the system"""
    try:
        metadata = {
            "title": entry.title,
            "category": entry.category,
            "tags": entry.tags,
            "source": entry.source,
            "priority": entry.priority
        }
        
        result = await brain_ai.process_knowledge(entry.content, metadata)
        return {"message": "Knowledge added successfully", "knowledge_id": result["id"], "data": result}
    except Exception as e:
        logger.error(f"Error adding knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_knowledge(request: QueryRequest):
    """Query knowledge base"""
    try:
        results = await brain_ai.query_knowledge(request.query, request.limit)
        return results
    except Exception as e:
        logger.error(f"Error querying knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights():
    """Get knowledge insights and analytics"""
    try:
        insights = await brain_ai.get_insights()
        return insights
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback on knowledge item"""
    try:
        await brain_ai.learn_from_feedback(feedback.knowledge_id, feedback.feedback_type, feedback.rating)
        return {"message": "Feedback recorded successfully"}
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/all")
async def get_all_knowledge():
    """Get all knowledge entries"""
    try:
        knowledge_list = []
        for entry in brain_ai.knowledge_base.values():
            knowledge_list.append(entry)
        
        # Sort by timestamp (newest first)
        knowledge_list.sort(key=lambda x: x["timestamp"], reverse=True)
        return knowledge_list
    except Exception as e:
        logger.error(f"Error getting all knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")