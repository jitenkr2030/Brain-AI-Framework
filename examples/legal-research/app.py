#!/usr/bin/env python3
"""
Legal Research System - Brain AI Example
Intelligent legal research and case analysis platform
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
    """Brain AI Framework - Legal Research Core"""
    
    def __init__(self):
        self.case_files = {}
        self.legal_documents = {}
        self.research_queries = {}
        self.jurisprudence_db = {}
        self.citation_network = {}
        self.legal_precedents = {}
        self.research_analytics = {}
        self.compliance_tracking = {}
        
    async def process_legal_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze legal document"""
        document_id = str(uuid.uuid4())
        
        # Extract legal entities
        legal_entities = await self._extract_legal_entities(document_data)
        legal_concepts = await self._extract_legal_concepts(document_data)
        case_citations = await self._extract_case_citations(document_data)
        statutory_references = await self._extract_statutory_references(document_data)
        
        # Analyze legal complexity
        complexity_analysis = await self._analyze_legal_complexity(document_data)
        
        # Create document analysis
        document_analysis = {
            "id": document_id,
            "basic_info": {
                "title": document_data.get("title", ""),
                "document_type": document_data.get("document_type", "legal_brief"),
                "court": document_data.get("court", ""),
                "date": document_data.get("date", ""),
                "jurisdiction": document_data.get("jurisdiction", ""),
                "case_number": document_data.get("case_number", "")
            },
            "content_analysis": {
                "legal_entities": legal_entities,
                "legal_concepts": legal_concepts,
                "case_citations": case_citations,
                "statutory_references": statutory_references,
                "complexity_score": complexity_analysis["complexity_score"],
                "complexity_factors": complexity_analysis["factors"]
            },
            "legal_analysis": {
                "primary_issues": await self._identify_primary_issues(document_data),
                "legal_arguments": await self._extract_legal_arguments(document_data),
                "precedent_analysis": await self._analyze_precedents(case_citations),
                "risk_assessment": await self._assess_legal_risks(document_data),
                "compliance_check": await self._check_compliance_requirements(document_data)
            },
            "metadata": {
                "word_count": len(document_data.get("content", "").split()),
                "page_count": document_data.get("page_count", 1),
                "confidence_score": random.uniform(0.8, 0.95),
                "processing_date": datetime.now().isoformat(),
                "model_version": "1.0.0"
            },
            "quality_metrics": await self._calculate_quality_metrics(document_data),
            "recommendations": await self._generate_legal_recommendations(document_data)
        }
        
        # Store document analysis
        self.legal_documents[document_id] = document_analysis
        
        # Update citation network
        await self._update_citation_network(document_analysis)
        
        # Update research analytics
        await self._update_research_analytics(document_analysis)
        
        return document_analysis
    
    async def _extract_legal_entities(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract legal entities from document"""
        content = document_data.get("content", "")
        entities = []
        
        # Extract parties
        parties = await self._identify_parties(content)
        for party in parties:
            entities.append({
                "type": "party",
                "name": party["name"],
                "role": party["role"],
                "confidence": party["confidence"]
            })
        
        # Extract judges
        judges = await self._identify_judges(content)
        for judge in judges:
            entities.append({
                "type": "judge",
                "name": judge["name"],
                "court": judge.get("court", ""),
                "confidence": judge["confidence"]
            })
        
        # Extract attorneys
        attorneys = await self._identify_attorneys(content)
        for attorney in attorneys:
            entities.append({
                "type": "attorney",
                "name": attorney["name"],
                "firm": attorney.get("firm", ""),
                "bar_number": attorney.get("bar_number", ""),
                "confidence": attorney["confidence"]
            })
        
        # Extract legal organizations
        organizations = await self._identify_legal_organizations(content)
        for org in organizations:
            entities.append({
                "type": "organization",
                "name": org["name"],
                "type_org": org.get("type", "unknown"),
                "confidence": org["confidence"]
            })
        
        return entities
    
    async def _identify_parties(self, content: str) -> List[Dict[str, Any]]:
        """Identify parties in legal document"""
        parties = []
        
        # Simulate party identification
        common_patterns = [
            "plaintiff", "defendant", "appellant", "appellee",
            "petitioner", "respondent", "complainant", "respondent"
        ]
        
        # Simple pattern matching for demo
        lines = content.split('\n')
        for line in lines[:20]:  # Check first 20 lines
            for pattern in common_patterns:
                if pattern.lower() in line.lower():
                    # Extract potential party names
                    if ":" in line:
                        name_part = line.split(":", 1)[1].strip()
                        if len(name_part) > 3:
                            parties.append({
                                "name": name_part,
                                "role": pattern,
                                "confidence": random.uniform(0.6, 0.9)
                            })
        
        return parties[:5]  # Limit results
    
    async def _identify_judges(self, content: str) -> List[Dict[str, Any]]:
        """Identify judges in document"""
        judges = []
        
        # Simulate judge identification
        judge_indicators = ["judge", "justice", "magistrate", "justice of the peace"]
        
        lines = content.split('\n')
        for line in lines:
            for indicator in judge_indicators:
                if indicator.lower() in line.lower() and "honorable" in line.lower():
                    # Extract judge name
                    words = line.split()
                    for i, word in enumerate(words):
                        if word.lower() in ["honorable", "hon."]:
                            if i + 2 < len(words):
                                judge_name = f"{words[i+1]} {words[i+2]}"
                                judges.append({
                                    "name": judge_name,
                                    "court": "unknown",
                                    "confidence": random.uniform(0.7, 0.9)
                                })
        
        return judges[:3]  # Limit results
    
    async def _identify_attorneys(self, content: str) -> List[Dict[str, Any]]:
        """Identify attorneys in document"""
        attorneys = []
        
        # Simulate attorney identification
        attorney_indicators = ["attorney", "counsel", "lawyer", "esquire"]
        
        lines = content.split('\n')
        for line in lines:
            for indicator in attorney_indicators:
                if indicator.lower() in line.lower():
                    # Extract attorney information
                    if ":" in line:
                        info_part = line.split(":", 1)[1].strip()
                        if len(info_part) > 3:
                            attorneys.append({
                                "name": info_part.split(",")[0] if "," in info_part else info_part,
                                "firm": "",
                                "bar_number": "",
                                "confidence": random.uniform(0.6, 0.8)
                            })
        
        return attorneys[:5]  # Limit results
    
    async def _identify_legal_organizations(self, content: str) -> List[Dict[str, Any]]:
        """Identify legal organizations"""
        organizations = []
        
        # Common legal organization patterns
        org_patterns = [
            "llc", "inc", "corp", "corporation", "company", "firm",
            "association", "foundation", "institute", "agency"
        ]
        
        # Simple word-based detection
        words = content.split()
        for i, word in enumerate(words):
            word_clean = word.lower().strip('.,;:()[]{}"')
            if word_clean in org_patterns:
                # Look for organization names
                if i > 0 and i < len(words) - 1:
                    org_name = f"{words[i-1]} {words[i]} {words[i+1]}"
                    organizations.append({
                        "name": org_name,
                        "type": "business_entity",
                        "confidence": random.uniform(0.5, 0.7)
                    })
        
        return organizations[:5]  # Limit results
    
    async def _extract_legal_concepts(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract legal concepts and doctrines"""
        content = document_data.get("content", "")
        concepts = []
        
        # Common legal concepts
        legal_concepts = {
            "contract_law": ["contract", "agreement", "breach", "consideration", "offer", "acceptance"],
            "tort_law": ["negligence", "liability", "damages", "duty of care", "proximate cause"],
            "criminal_law": ["crime", "guilt", "innocence", "punishment", "sentence", "verdict"],
            "constitutional_law": ["constitution", "amendment", "rights", "liberty", "equal protection"],
            "property_law": ["property", "ownership", "title", "deed", "lease", "easement"],
            "corporate_law": ["corporation", "shareholder", "director", "fiduciary", "merger"],
            "employment_law": ["employment", "discrimination", "harassment", "wrongful termination"],
            "intellectual_property": ["patent", "trademark", "copyright", "trade secret"]
        }
        
        content_lower = content.lower()
        
        for category, terms in legal_concepts.items():
            found_terms = []
            for term in terms:
                if term in content_lower:
                    found_terms.append(term)
            
            if found_terms:
                concepts.append({
                    "category": category,
                    "terms": found_terms,
                    "relevance_score": len(found_terms) / len(terms),
                    "confidence": random.uniform(0.7, 0.9)
                })
        
        return concepts
    
    async def _extract_case_citations(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract case citations"""
        content = document_data.get("content", "")
        citations = []
        
        # Pattern for case citations (simplified)
        citation_patterns = [
            r'\b\d+\s+[A-Z][a-z]+\.?\s+\d+\b',  # Volume Reporter Page
            r'\b[A-Z][a-z]+\s+v\.?\s+[A-Z][a-z]+\b',  # Party v. Party
            r'\b\d+\s+U\.S\.\s+\d+\b',  # US Supreme Court
            r'\b\d+\s+F\.\d+d?\s+\d+\b'  # Federal Reporter
        ]
        
        import re
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                citations.append({
                    "citation": match,
                    "type": "case_law",
                    "court_level": self._determine_court_level(match),
                    "relevance": random.uniform(0.6, 0.9),
                    "confidence": random.uniform(0.7, 0.85)
                })
        
        return citations[:10]  # Limit results
    
    def _determine_court_level(self, citation: str) -> str:
        """Determine court level from citation"""
        if "U.S." in citation or "Supreme Court" in citation:
            return "supreme"
        elif "F." in citation:
            return "federal_appellate"
        elif "F.Suppl" in citation:
            return "federal_district"
        else:
            return "state"
    
    async def _extract_statutory_references(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract statutory references"""
        content = document_data.get("content", "")
        statutes = []
        
        # Common statutory patterns
        statute_patterns = [
            r'\b\d+\s+U\.S\.C\.\s+§\s*\d+[a-zA-Z]*\b',  # USC
            r'\b\d+\s+C\.F\.R\.\s+§\s*\d+[a-zA-Z]*\b',  # CFR
            r'\b[A-Z]{2,}\s+Code\s+§\s*\d+[a-zA-Z]*\b',  # State codes
            r'\bSection\s+\d+[a-zA-Z]*\b',  # Generic sections
            r'\b§\s*\d+[a-zA-Z]*\b'  # Section symbols
        ]
        
        import re
        
        for pattern in statute_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                statutes.append({
                    "reference": match,
                    "type": "statute",
                    "jurisdiction": self._determine_jurisdiction(match),
                    "relevance": random.uniform(0.6, 0.9),
                    "confidence": random.uniform(0.7, 0.85)
                })
        
        return statutes[:10]  # Limit results
    
    def _determine_jurisdiction(self, statute: str) -> str:
        """Determine jurisdiction from statute reference"""
        if "U.S.C." in statute:
            return "federal"
        elif "C.F.R." in statute:
            return "federal_regulation"
        else:
            return "state"
    
    async def _analyze_legal_complexity(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze legal complexity of document"""
        content = document_data.get("content", "")
        
        complexity_factors = {
            "legal_jargon_density": await self._calculate_jargon_density(content),
            "sentence_complexity": await self._calculate_sentence_complexity(content),
            "citation_density": await self._calculate_citation_density(content),
            "concept_density": await this._calculate_concept_density(content),
            "procedural_complexity": await self._assess_procedural_complexity(document_data)
        }
        
        # Calculate overall complexity score
        complexity_score = sum(complexity_factors.values()) / len(complexity_factors)
        
        return {
            "complexity_score": complexity_score,
            "factors": complexity_factors,
            "complexity_level": self._classify_complexity_level(complexity_score)
        }
    
    async def _calculate_jargon_density(self, content: str) -> float:
        """Calculate density of legal jargon"""
        legal_jargon = [
            "whereas", "heretofore", "aforementioned", "hereinafter", "notwithstanding",
            "inter alia", "per se", "res ipsa loquitur", "habeas corpus", "in camera",
            "pro bono", "ex parte", "prima facie", "stare decisis", "mens rea"
        ]
        
        words = content.split()
        jargon_count = sum(1 for word in words if any(jargon in word.lower() for jargon in legal_jargon))
        
        return min(jargon_count / len(words), 1.0) if words else 0.0
    
    async def _calculate_sentence_complexity(self, content: str) -> float:
        """Calculate average sentence complexity"""
        sentences = content.split('.')
        if not sentences:
            return 0.0
        
        avg_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
        
        # Normalize to 0-1 scale (assuming 20 words average is complex)
        return min(avg_length / 20.0, 1.0)
    
    async def _calculate_citation_density(self, content: str) -> float:
        """Calculate density of legal citations"""
        # Count citation patterns
        import re
        citation_patterns = [
            r'\d+\s+[A-Z][a-z]+\.?\s+\d+\b',
            r'\b\d+\s+U\.S\.\s+\d+\b',
            r'\b\d+\s+F\.\d+d?\s+\d+\b'
        ]
        
        citation_count = 0
        for pattern in citation_patterns:
            citation_count += len(re.findall(pattern, content))
        
        words = len(content.split())
        return min(citation_count / (words / 100), 1.0) if words > 0 else 0.0
    
    async def _calculate_concept_density(self, content: str) -> float:
        """Calculate density of legal concepts"""
        legal_concepts = [
            "jurisdiction", "precedent", "constitutional", "statutory", "regulatory",
            "litigation", "arbitration", "compliance", "liability", "damages"
        ]
        
        content_lower = content.lower()
        concept_count = sum(1 for concept in legal_concepts if concept in content_lower)
        words = len(content.split())
        
        return min(concept_count / (words / 50), 1.0) if words > 0 else 0.0
    
    async def _assess_procedural_complexity(self, document_data: Dict[str, Any]) -> float:
        """Assess procedural complexity"""
        content = document_data.get("content", "")
        doc_type = document_data.get("document_type", "")
        
        complexity_indicators = [
            "motion", "discovery", "deposition", "subpoena", "pleading",
            "brief", "memorandum", "petition", "complaint", "answer"
        ]
        
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in complexity_indicators if indicator in content_lower)
        
        # Adjust for document type
        type_multiplier = {
            "motion": 1.2,
            "brief": 1.1,
            "contract": 0.8,
            "agreement": 0.7,
            "memo": 0.9
        }.get(doc_type.lower(), 1.0)
        
        return min((indicator_count * type_multiplier) / 10.0, 1.0)
    
    def _classify_complexity_level(self, score: float) -> str:
        """Classify complexity level"""
        if score < 0.3:
            return "simple"
        elif score < 0.6:
            return "moderate"
        elif score < 0.8:
            return "complex"
        else:
            return "very_complex"
    
    async def _identify_primary_issues(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify primary legal issues"""
        content = document_data.get("content", "")
        issues = []
        
        # Common legal issues
        issue_keywords = {
            "contract_dispute": ["breach of contract", "contract dispute", "agreement violation"],
            "personal_injury": ["negligence", "personal injury", "bodily harm", "medical malpractice"],
            "employment_law": ["wrongful termination", "discrimination", "harassment", "employment dispute"],
            "intellectual_property": ["patent infringement", "copyright violation", "trademark dispute"],
            "criminal_charges": ["criminal charges", "indictment", "arraignment", "trial"],
            "family_law": ["divorce", "custody", "support", "adoption"],
            "real_estate": ["property dispute", "title issue", "easement", "zoning"],
            "corporate_litigation": ["merger dispute", "shareholder rights", "corporate governance"]
        }
        
        content_lower = content.lower()
        
        for issue_type, keywords in issue_keywords.items():
            relevance = sum(1 for keyword in keywords if keyword in content_lower)
            if relevance > 0:
                issues.append({
                    "type": issue_type,
                    "relevance_score": relevance / len(keywords),
                    "confidence": random.uniform(0.6, 0.9)
                })
        
        return issues[:5]  # Return top 5 issues
    
    async def _extract_legal_arguments(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract legal arguments from document"""
        content = document_data.get("content", "")
        arguments = []
        
        # Argument indicators
        argument_indicators = [
            "argues", "contends", "maintains", "asserts", "claims",
            "therefore", "consequently", "thus", "hence", "accordingly"
        ]
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if any(indicator in sentence_lower for indicator in argument_indicators):
                arguments.append({
                    "text": sentence.strip(),
                    "type": self._classify_argument_type(sentence),
                    "strength": random.uniform(0.5, 0.9),
                    "confidence": random.uniform(0.6, 0.8)
                })
        
        return arguments[:10]  # Limit results
    
    def _classify_argument_type(self, sentence: str) -> str:
        """Classify type of legal argument"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ["precedent", "prior case", "established law"]):
            return "precedential"
        elif any(word in sentence_lower for word in ["statute", "statutory", "legislative"]):
            return "statutory"
        elif any(word in sentence_lower for word in ["constitutional", "amendment", "rights"]):
            return "constitutional"
        elif any(word in sentence_lower for word in ["policy", "public interest", "social"]):
            return "policy"
        else:
            return "general"
    
    async def _analyze_precedents(self, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cited precedents"""
        precedent_analysis = {
            "total_citations": len(citations),
            "citation_types": {},
            "court_hierarchy": {},
            "relevance_analysis": [],
            "binding_vs_persuasive": {}
        }
        
        for citation in citations:
            # Analyze citation types
            cite_type = citation.get("type", "unknown")
            precedent_analysis["citation_types"][cite_type] = precedent_analysis["citation_types"].get(cite_type, 0) + 1
            
            # Analyze court hierarchy
            court_level = citation.get("court_level", "unknown")
            precedent_analysis["court_hierarchy"][court_level] = precedent_analysis["court_hierarchy"].get(court_level, 0) + 1
            
            # Determine binding vs persuasive
            if court_level in ["supreme", "federal_appellate"]:
                binding_type = "binding"
            else:
                binding_type = "persuasive"
            
            precedent_analysis["binding_vs_persuasive"][binding_type] = precedent_analysis["binding_vs_persuasive"].get(binding_type, 0) + 1
            
            # Relevance analysis
            precedent_analysis["relevance_analysis"].append({
                "citation": citation["citation"],
                "relevance": citation.get("relevance", 0),
                "court_level": court_level,
                "binding_effect": binding_type
            })
        
        return precedent_analysis
    
    async def _assess_legal_risks(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess legal risks in document"""
        risk_assessment = {
            "overall_risk_level": "medium",
            "risk_factors": [],
            "mitigation_strategies": [],
            "compliance_issues": []
        }
        
        content = document_data.get("content", "").lower()
        
        # Risk indicators
        risk_indicators = {
            "high_liability": ["million dollars", "substantial damages", "class action"],
            "regulatory_violation": ["violation", "non-compliance", "regulatory breach"],
            "litigation_risk": ["lawsuit", "litigation", "court case", "dispute"],
            "contract_risk": ["breach", "default", "termination", "dispute"],
            "employment_risk": ["discrimination", "harassment", "wrongful termination"]
        }
        
        for risk_type, indicators in risk_indicators.items():
            risk_score = sum(1 for indicator in indicators if indicator in content)
            if risk_score > 0:
                risk_level = "high" if risk_score > 2 else "medium"
                
                risk_assessment["risk_factors"].append({
                    "type": risk_type,
                    "level": risk_level,
                    "evidence_count": risk_score,
                    "confidence": random.uniform(0.7, 0.9)
                })
        
        # Determine overall risk level
        high_risks = len([r for r in risk_assessment["risk_factors"] if r["level"] == "high"])
        if high_risks > 2:
            risk_assessment["overall_risk_level"] = "high"
        elif len(risk_assessment["risk_factors"]) > 3:
            risk_assessment["overall_risk_level"] = "medium"
        else:
            risk_assessment["overall_risk_level"] = "low"
        
        return risk_assessment
    
    async def _check_compliance_requirements(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with legal requirements"""
        compliance_check = {
            "overall_compliance": "compliant",
            "requirements_checked": [],
            "deficiencies": [],
            "recommendations": []
        }
        
        content = document_data.get("content", "").lower()
        doc_type = document_data.get("document_type", "")
        
        # Common compliance requirements
        requirements = {
            "signature_requirement": ["signed", "signature", "executed"],
            "notarization": ["notary", "notarized", "acknowledged"],
            "disclosure_requirements": ["disclosure", "informed consent", "notice"],
            "filing_requirements": ["filed", "court filing", "registry"],
            "witness_requirements": ["witness", "attested", "witnessed"]
        }
        
        for req_type, keywords in requirements.items():
            is_compliant = any(keyword in content for keyword in keywords)
            compliance_check["requirements_checked"].append({
                "requirement": req_type,
                "compliant": is_compliant,
                "confidence": random.uniform(0.8, 0.95)
            })
            
            if not is_compliant:
                compliance_check["deficiencies"].append(req_type)
        
        # Determine overall compliance
        if len(compliance_check["deficiencies"]) > 2:
            compliance_check["overall_compliance"] = "non_compliant"
        elif len(compliance_check["deficiencies"]) > 0:
            compliance_check["overall_compliance"] = "partially_compliant"
        
        return compliance_check
    
    async def _calculate_quality_metrics(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate document quality metrics"""
        content = document_data.get("content", "")
        
        return {
            "completeness_score": random.uniform(0.7, 0.95),
            "accuracy_score": random.uniform(0.8, 0.95),
            "clarity_score": random.uniform(0.6, 0.9),
            "organization_score": random.uniform(0.7, 0.9),
            "legal_citation_quality": random.uniform(0.6, 0.9),
            "overall_quality": random.uniform(0.7, 0.9)
        }
    
    async def _generate_legal_recommendations(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate legal recommendations"""
        recommendations = []
        
        content = document_data.get("content", "").lower()
        doc_type = document_data.get("document_type", "")
        
        # General recommendations
        if "draft" in content or "preliminary" in content:
            recommendations.append({
                "type": "review",
                "priority": "high",
                "description": "Document appears to be in draft form - final review recommended",
                "category": "quality_assurance"
            })
        
        # Type-specific recommendations
        if doc_type.lower() == "contract":
            recommendations.append({
                "type": "legal_review",
                "priority": "high",
                "description": "Contract should be reviewed by qualified legal counsel",
                "category": "legal_review"
            })
        elif doc_type.lower() == "motion":
            recommendations.append({
                "type": "citation_check",
                "priority": "medium",
                "description": "Verify all case citations are current and accurate",
                "category": "citation_verification"
            })
        
        # Compliance recommendations
        if "confidential" in content:
            recommendations.append({
                "type": "confidentiality",
                "priority": "high",
                "description": "Ensure appropriate confidentiality markings and handling",
                "category": "confidentiality"
            })
        
        return recommendations
    
    async def _update_citation_network(self, document_analysis: Dict[str, Any]):
        """Update citation network with new document"""
        if not self.citation_network:
            self.citation_network = {
                "nodes": {},  # Documents
                "edges": {},  # Citations between documents
                "clusters": {},  # Related document clusters
                "authority_scores": {}  # Document authority
            }
        
        doc_id = document_analysis["id"]
        
        # Add document node
        self.citation_network["nodes"][doc_id] = {
            "title": document_analysis["basic_info"]["title"],
            "type": document_analysis["basic_info"]["document_type"],
            "date": document_analysis["basic_info"]["date"],
            "complexity": document_analysis["content_analysis"]["complexity_score"]
        }
        
        # Add citation edges
        citations = document_analysis["content_analysis"]["case_citations"]
        for citation in citations:
            cite_key = citation["citation"]
            if cite_key not in self.citation_network["edges"]:
                self.citation_network["edges"][cite_key] = []
            
            self.citation_network["edges"][cite_key].append({
                "from": doc_id,
                "relevance": citation["relevance"],
                "type": citation["type"]
            })
    
    async def _update_research_analytics(self, document_analysis: Dict[str, Any]):
        """Update research analytics with new document"""
        if not self.research_analytics:
            self.research_analytics = {
                "total_documents": 0,
                "document_types": {},
                "complexity_distribution": {},
                "legal_concepts_frequency": {},
                "research_trends": []
            }
        
        analytics = self.research_analytics
        
        # Update basic counts
        analytics["total_documents"] += 1
        
        # Update document type distribution
        doc_type = document_analysis["basic_info"]["document_type"]
        analytics["document_types"][doc_type] = analytics["document_types"].get(doc_type, 0) + 1
        
        # Update complexity distribution
        complexity_level = document_analysis["content_analysis"]["complexity_analysis"]["complexity_level"]
        analytics["complexity_distribution"][complexity_level] = analytics["complexity_distribution"].get(complexity_level, 0) + 1
        
        # Update legal concepts frequency
        for concept in document_analysis["content_analysis"]["legal_concepts"]:
            category = concept["category"]
            analytics["legal_concepts_frequency"][category] = analytics["legal_concepts_frequency"].get(category, 0) + 1
    
    async def conduct_legal_research(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive legal research"""
        research_id = str(uuid.uuid4())
        
        # Parse research query
        query_analysis = await self._analyze_research_query(query)
        
        # Search legal documents
        search_results = await self._search_legal_documents(query)
        
        # Analyze results
        result_analysis = await self._analyze_search_results(search_results, query)
        
        # Generate research insights
        research_insights = await self._generate_research_insights(result_analysis, query)
        
        # Create research report
        research_report = {
            "id": research_id,
            "query": query,
            "query_analysis": query_analysis,
            "search_results": search_results,
            "result_analysis": result_analysis,
            "research_insights": research_insights,
            "metadata": {
                "conducted_at": datetime.now().isoformat(),
                "total_documents_reviewed": len(search_results),
                "research_duration": random.randint(30, 300),  # seconds
                "confidence_score": random.uniform(0.75, 0.95)
            },
            "recommendations": await self._generate_research_recommendations(result_analysis)
        }
        
        # Store research
        self.research_queries[research_id] = research_report
        
        return research_report
    
    async def _analyze_research_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze research query for optimal searching"""
        search_terms = query.get("search_terms", [])
        legal_areas = query.get("legal_areas", [])
        jurisdictions = query.get("jurisdictions", [])
        date_range = query.get("date_range", {})
        
        return {
            "primary_terms": search_terms[:3],  # Top 3 terms
            "secondary_terms": search_terms[3:],  # Remaining terms
            "focus_areas": legal_areas,
            "jurisdictions": jurisdictions,
            "temporal_scope": date_range,
            "query_complexity": len(search_terms) + len(legal_areas),
            "search_strategy": self._determine_search_strategy(search_terms, legal_areas)
        }
    
    def _determine_search_strategy(self, search_terms: List[str], legal_areas: List[str]) -> str:
        """Determine optimal search strategy"""
        if len(search_terms) > 5:
            return "comprehensive"
        elif len(legal_areas) > 2:
            return "multi_area"
        else:
            return "focused"
    
    async def _search_legal_documents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search legal documents based on query"""
        search_terms = query.get("search_terms", [])
        legal_areas = query.get("legal_areas", [])
        
        results = []
        
        # Search through existing documents
        for doc_id, document in self.legal_documents.items():
            relevance_score = await this._calculate_document_relevance(document, search_terms, legal_areas)
            
            if relevance_score > 0.3:  # Relevance threshold
                results.append({
                    "document": document,
                    "relevance_score": relevance_score,
                    "match_reasons": await self._identify_match_reasons(document, search_terms, legal_areas)
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:20]  # Return top 20 results
    
    async def _calculate_document_relevance(self, document: Dict[str, Any], 
                                          search_terms: List[str], 
                                          legal_areas: List[str]) -> float:
        """Calculate document relevance to search query"""
        content = document.get("basic_info", {}).get("title", "") + " " + \
                 " ".join([entity.get("name", "") for entity in document.get("content_analysis", {}).get("legal_entities", [])])
        
        content_lower = content.lower()
        term_relevance = 0.0
        
        # Calculate term relevance
        for term in search_terms:
            if term.lower() in content_lower:
                term_relevance += 1.0
        
        # Normalize by number of terms
        term_relevance = term_relevance / len(search_terms) if search_terms else 0.0
        
        # Check legal area relevance
        area_relevance = 0.0
        document_concepts = document.get("content_analysis", {}).get("legal_concepts", [])
        for concept in document_concepts:
            if concept.get("category") in legal_areas:
                area_relevance += concept.get("relevance_score", 0.0)
        
        # Combine relevances
        total_relevance = (term_relevance * 0.6) + (area_relevance * 0.4)
        
        return min(total_relevance, 1.0)
    
    async def _identify_match_reasons(self, document: Dict[str, Any], 
                                    search_terms: List[str], 
                                    legal_areas: List[str]) -> List[str]:
        """Identify why document matches search query"""
        reasons = []
        
        content = document.get("basic_info", {}).get("title", "")
        content_lower = content.lower()
        
        # Term matches
        for term in search_terms:
            if term.lower() in content_lower:
                reasons.append(f"Contains term '{term}'")
        
        # Legal area matches
        document_concepts = document.get("content_analysis", {}).get("legal_concepts", [])
        for concept in document_concepts:
            if concept.get("category") in legal_areas:
                reasons.append(f"Addresses {concept.get('category')}")
        
        # Entity matches
        entities = document.get("content_analysis", {}).get("legal_entities", [])
        for entity in entities:
            if any(term.lower() in entity.get("name", "").lower() for term in search_terms):
                reasons.append(f"Involves {entity.get('name', '')}")
        
        return reasons[:5]  # Limit reasons
    
    async def _analyze_search_results(self, results: List[Dict[str, Any]], 
                                    query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze search results for insights"""
        if not results:
            return {"message": "No relevant documents found"}
        
        analysis = {
            "total_results": len(results),
            "average_relevance": sum(r["relevance_score"] for r in results) / len(results),
            "relevance_distribution": self._calculate_relevance_distribution(results),
            "document_type_breakdown": {},
            "legal_concept_coverage": {},
            "jurisdiction_analysis": {},
            "temporal_distribution": {},
            "quality_assessment": await this._assess_result_quality(results)
        }
        
        # Document type breakdown
        for result in results:
            doc_type = result["document"]["basic_info"]["document_type"]
            analysis["document_type_breakdown"][doc_type] = analysis["document_type_breakdown"].get(doc_type, 0) + 1
        
        # Legal concept coverage
        for result in results:
            concepts = result["document"]["content_analysis"]["legal_concepts"]
            for concept in concepts:
                category = concept["category"]
                if category not in analysis["legal_concept_coverage"]:
                    analysis["legal_concept_coverage"][category] = {
                        "frequency": 0,
                        "total_relevance": 0
                    }
                analysis["legal_concept_coverage"][category]["frequency"] += 1
                analysis["legal_concept_coverage"][category]["total_relevance"] += concept.get("relevance_score", 0)
        
        return analysis
    
    def _calculate_relevance_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, str]:
        """Calculate relevance score distribution"""
        high_relevance = len([r for r in results if r["relevance_score"] > 0.7])
        medium_relevance = len([r for r in results if 0.4 < r["relevance_score"] <= 0.7])
        low_relevance = len([r for r in results if r["relevance_score"] <= 0.4])
        
        return {
            "high": f"{high_relevance}/{len(results)}",
            "medium": f"{medium_relevance}/{len(results)}",
            "low": f"{low_relevance}/{len(results)}"
        }
    
    async def _assess_result_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess quality of search results"""
        total_quality = 0
        quality_details = []
        
        for result in results:
            document = result["document"]
            quality_metrics = document.get("quality_metrics", {})
            
            quality_score = (
                quality_metrics.get("completeness_score", 0.5) +
                quality_metrics.get("accuracy_score", 0.5) +
                quality_metrics.get("legal_citation_quality", 0.5)
            ) / 3
            
            total_quality += quality_score
            quality_details.append({
                "document_id": document["id"],
                "quality_score": quality_score,
                "completeness": quality_metrics.get("completeness_score", 0),
                "accuracy": quality_metrics.get("accuracy_score", 0),
                "citation_quality": quality_metrics.get("legal_citation_quality", 0)
            })
        
        return {
            "average_quality": total_quality / len(results) if results else 0,
            "quality_distribution": quality_details,
            "quality_assessment": "high" if total_quality / len(results) > 0.8 else "medium" if total_quality / len(results) > 0.6 else "low"
        }
    
    async def _generate_research_insights(self, analysis: Dict[str, Any], 
                                        query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from research results"""
        insights = []
        
        # Relevance insight
        avg_relevance = analysis.get("average_relevance", 0)
        if avg_relevance > 0.7:
            insights.append({
                "type": "search_effectiveness",
                "insight": "Search query yielded highly relevant results",
                "confidence": 0.8,
                "actionable": True
            })
        elif avg_relevance < 0.4:
            insights.append({
                "type": "search_refinement",
                "insight": "Consider refining search terms for better results",
                "confidence": 0.7,
                "actionable": True
            })
        
        # Coverage insight
        concept_coverage = analysis.get("legal_concept_coverage", {})
        if len(concept_coverage) > 5:
            insights.append({
                "type": "comprehensive_coverage",
                "insight": f"Research covers {len(concept_coverage)} legal concepts comprehensively",
                "confidence": 0.8,
                "actionable": False
            })
        
        # Quality insight
        quality_assessment = analysis.get("quality_assessment", "medium")
        if quality_assessment == "high":
            insights.append({
                "type": "document_quality",
                "insight": "All retrieved documents are of high quality",
                "confidence": 0.9,
                "actionable": False
            })
        
        return insights
    
    async def _generate_research_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on research results"""
        recommendations = []
        
        # Search refinement recommendations
        if analysis.get("average_relevance", 0) < 0.5:
            recommendations.append({
                "type": "search_optimization",
                "priority": "high",
                "description": "Refine search terms to improve result relevance",
                "implementation": "Add more specific legal terminology or include synonyms"
            })
        
        # Coverage recommendations
        concept_coverage = analysis.get("legal_concept_coverage", {})
        if len(concept_coverage) < 3:
            recommendations.append({
                "type": "coverage_expansion",
                "priority": "medium",
                "description": "Expand search to cover additional legal concepts",
                "implementation": "Include related legal areas or specific doctrines"
            })
        
        # Document type recommendations
        doc_types = analysis.get("document_type_breakdown", {})
        if "brief" not in doc_types and "memorandum" not in doc_types:
            recommendations.append({
                "type": "document_diversity",
                "priority": "low",
                "description": "Consider searching for additional document types",
                "implementation": "Include case briefs, legal memos, or statutes"
            })
        
        return recommendations
    
    async def get_legal_research_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive legal research analytics"""
        if not self.legal_documents:
            return {"message": "No legal documents available for analytics"}
        
        analytics = {
            "document_metrics": await self._calculate_document_metrics(),
            "research_trends": await this._analyze_research_trends(),
            "citation_analysis": await self._analyze_citation_patterns(),
            "legal_topic_analysis": await self._analyze_legal_topics(),
            "quality_insights": await self._generate_quality_insights(),
            "recommendations": await self._generate_platform_recommendations()
        }
        
        return analytics
    
    async def _calculate_document_metrics(self) -> Dict[str, Any]:
        """Calculate document-related metrics"""
        documents = list(self.legal_documents.values())
        total_docs = len(documents)
        
        if total_docs == 0:
            return {"total_documents": 0}
        
        # Calculate averages
        avg_complexity = sum(doc["content_analysis"]["complexity_score"] for doc in documents) / total_docs
        avg_quality = sum(doc["quality_metrics"]["overall_quality"] for doc in documents) / total_docs
        
        # Document type distribution
        doc_types = {}
        for doc in documents:
            doc_type = doc["basic_info"]["document_type"]
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        # Complexity distribution
        complexity_levels = {}
        for doc in documents:
            level = doc["content_analysis"]["complexity_analysis"]["complexity_level"]
            complexity_levels[level] = complexity_levels.get(level, 0) + 1
        
        return {
            "total_documents": total_docs,
            "average_complexity": avg_complexity,
            "average_quality": avg_quality,
            "document_type_distribution": doc_types,
            "complexity_distribution": complexity_levels,
            "recent_activity": len([doc for doc in documents if self._is_recent_document(doc)])
        }
    
    def _is_recent_document(self, document: Dict[str, Any]) -> bool:
        """Check if document is recent (within last 30 days)"""
        doc_date = document.get("basic_info", {}).get("date", "")
        if not doc_date:
            return False
        
        try:
            date_obj = datetime.fromisoformat(doc_date.replace("Z", "+00:00"))
            return (datetime.now() - date_obj).days <= 30
        except:
            return False
    
    async def _analyze_research_trends(self) -> Dict[str, Any]:
        """Analyze research trends over time"""
        # Simulate trend analysis
        return {
            "popular_search_terms": [
                {"term": "contract dispute", "frequency": 45},
                {"term": "intellectual property", "frequency": 38},
                {"term": "employment law", "frequency": 32},
                {"term": "personal injury", "frequency": 28},
                {"term": "real estate", "frequency": 25}
            ],
            "emerging_legal_areas": [
                {"area": "cybersecurity law", "growth_rate": 0.25},
                {"area": "data privacy", "growth_rate": 0.22},
                {"area": "environmental law", "growth_rate": 0.18},
                {"area": "cryptocurrency regulation", "growth_rate": 0.15}
            ],
            "research_activity_trend": "increasing",
            "average_research_duration": 120  # minutes
        }
    
    async def _analyze_citation_patterns(self) -> Dict[str, Any]:
        """Analyze citation patterns in documents"""
        total_citations = 0
        citation_types = {}
        court_levels = {}
        
        for document in self.legal_documents.values():
            citations = document["content_analysis"]["case_citations"]
            total_citations += len(citations)
            
            for citation in citations:
                cite_type = citation.get("type", "unknown")
                court_level = citation.get("court_level", "unknown")
                
                citation_types[cite_type] = citation_types.get(cite_type, 0) + 1
                court_levels[court_level] = court_levels.get(court_level, 0) + 1
        
        return {
            "total_citations": total_citations,
            "citation_type_distribution": citation_types,
            "court_level_distribution": court_levels,
            "average_citations_per_document": total_citations / len(self.legal_documents) if self.legal_documents else 0,
            "most_cited_courts": sorted(court_levels.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    async def _analyze_legal_topics(self) -> Dict[str, Any]:
        """Analyze legal topic distribution and trends"""
        topic_frequency = {}
        primary_issues = {}
        
        for document in self.legal_documents.values():
            # Count legal concepts
            concepts = document["content_analysis"]["legal_concepts"]
            for concept in concepts:
                category = concept["category"]
                topic_frequency[category] = topic_frequency.get(category, 0) + 1
            
            # Count primary issues
            issues = document["legal_analysis"]["primary_issues"]
            for issue in issues:
                issue_type = issue["type"]
                primary_issues[issue_type] = primary_issues.get(issue_type, 0) + 1
        
        return {
            "most_researched_areas": sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:10],
            "common_legal_issues": sorted(primary_issues.items(), key=lambda x: x[1], reverse=True)[:10],
            "specialization_distribution": topic_frequency,
            "interdisciplinary_areas": self._identify_interdisciplinary_areas(topic_frequency)
        }
    
    def _identify_interdisciplinary_areas(self, topic_frequency: Dict[str, int]) -> List[str]:
        """Identify areas that span multiple legal disciplines"""
        interdisciplinary_areas = []
        
        # Simple heuristic: areas that appear with other areas frequently
        for topic in topic_frequency:
            if "corporate" in topic and "employment" in topic:
                interdisciplinary_areas.append("Corporate Employment Law")
            if "intellectual" in topic and "contract" in topic:
                interdisciplinary_areas.append("IP Contract Law")
            if "property" in topic and "environmental" in topic:
                interdisciplinary_areas.append("Environmental Property Law")
        
        return list(set(interdisciplinary_areas))
    
    async def _generate_quality_insights(self) -> Dict[str, Any]:
        """Generate quality insights from document analysis"""
        if not self.legal_documents:
            return {"message": "No documents available for quality analysis"}
        
        documents = list(self.legal_documents.values())
        
        # Calculate quality metrics
        quality_scores = [doc["quality_metrics"]["overall_quality"] for doc in documents]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Identify quality patterns
        high_quality_docs = [doc for doc in documents if doc["quality_metrics"]["overall_quality"] > 0.8]
        low_quality_docs = [doc for doc in documents if doc["quality_metrics"]["overall_quality"] < 0.6]
        
        return {
            "average_quality_score": avg_quality,
            "quality_distribution": {
                "high_quality": len(high_quality_docs),
                "medium_quality": len(documents) - len(high_quality_docs) - len(low_quality_docs),
                "low_quality": len(low_quality_docs)
            },
            "quality_factors": {
                "completeness_avg": sum(doc["quality_metrics"]["completeness_score"] for doc in documents) / len(documents),
                "accuracy_avg": sum(doc["quality_metrics"]["accuracy_score"] for doc in documents) / len(documents),
                "citation_quality_avg": sum(doc["quality_metrics"]["legal_citation_quality"] for doc in documents) / len(documents)
            },
            "improvement_opportunities": [
                "Focus on improving document completeness",
                "Enhance legal citation accuracy",
                "Strengthen document organization"
            ] if avg_quality < 0.7 else ["Maintain high quality standards"]
        }
    
    async def _generate_platform_recommendations(self) -> List[Dict[str, Any]]:
        """Generate platform-level recommendations"""
        recommendations = []
        
        if not self.legal_documents:
            return recommendations
        
        # Document volume recommendations
        if len(self.legal_documents) < 100:
            recommendations.append({
                "area": "content_expansion",
                "recommendation": "Expand legal document collection to improve research coverage",
                "priority": "medium",
                "impact": "high"
            })
        
        # Quality recommendations
        avg_quality = sum(doc["quality_metrics"]["overall_quality"] for doc in self.legal_documents.values()) / len(self.legal_documents)
        if avg_quality < 0.7:
            recommendations.append({
                "area": "quality_improvement",
                "recommendation": "Implement quality assurance processes for document processing",
                "priority": "high",
                "impact": "high"
            })
        
        # Feature recommendations
        recommendations.extend([
            {
                "area": "advanced_search",
                "recommendation": "Implement semantic search capabilities for better document discovery",
                "priority": "medium",
                "impact": "high"
            },
            {
                "area": "collaboration",
                "recommendation": "Add collaborative research features for legal teams",
                "priority": "low",
                "impact": "medium"
            }
        ])
        
        return recommendations

# Initialize Brain AI
brain_ai = BrainAI()

# Pydantic models
class LegalDocument(BaseModel):
    title: str
    document_type: str
    content: str
    court: Optional[str] = ""
    date: Optional[str] = ""
    jurisdiction: Optional[str] = ""
    case_number: Optional[str] = ""
    page_count: Optional[int] = 1

class LegalResearchQuery(BaseModel):
    search_terms: List[str]
    legal_areas: List[str] = []
    jurisdictions: List[str] = []
    date_range: Dict[str, Any] = {}
    document_types: List[str] = []
    complexity_filter: Optional[str] = ""

# Initialize FastAPI app
app = FastAPI(title="Brain AI Legal Research System", version="1.0.0")

# Demo data generator
async def generate_demo_data():
    """Generate demo legal documents and research data"""
    # Demo legal documents
    demo_documents = [
        {
            "title": "Smith v. Jones Contract Dispute Brief",
            "document_type": "legal_brief",
            "content": "This case involves a breach of contract dispute between plaintiff Smith and defendant Jones. The contract in question was executed on January 15, 2024, for the sale of commercial real estate. The plaintiff alleges that the defendant failed to complete the purchase according to the terms agreed upon. The court must determine whether there was a material breach of contract and what remedies are available. This matter involves issues of contract interpretation, consideration, and specific performance. The relevant case law includes Smith v. Brown, 123 F.3d 456, and Johnson v. Wilson, 789 U.S. 321.",
            "court": "Superior Court of California",
            "date": "2024-03-15",
            "jurisdiction": "California",
            "case_number": "CV-2024-001234",
            "page_count": 25
        },
        {
            "title": "Intellectual Property Licensing Agreement",
            "document_type": "contract",
            "content": "This Intellectual Property Licensing Agreement is entered into between TechCorp Inc. and StartupCo LLC. The agreement grants StartupCo a non-exclusive license to use certain patented technology owned by TechCorp. The license includes provisions for royalty payments, quality control, and termination rights. The agreement must comply with federal patent law and state contract law. Key legal concepts include patent licensing, royalty agreements, and intellectual property rights.",
            "court": "",
            "date": "2024-02-20",
            "jurisdiction": "Delaware",
            "case_number": "",
            "page_count": 12
        },
        {
            "title": "Employment Discrimination Complaint",
            "document_type": "complaint",
            "content": "Plaintiff Jane Doe files this complaint against her former employer, ABC Corporation, alleging discrimination based on gender and age in violation of Title VII of the Civil Rights Act and the Age Discrimination in Employment Act. The plaintiff seeks damages, reinstatement, and injunctive relief. The complaint alleges that the plaintiff was passed over for promotion in favor of less qualified male candidates and was subsequently terminated. Relevant precedents include Johnson v. Transportation Agency and Gross v. FBL Financial Services.",
            "court": "U.S. District Court",
            "date": "2024-04-10",
            "jurisdiction": "New York",
            "case_number": "1:24-cv-01234",
            "page_count": 18
        }
    ]
    
    for doc_data in demo_documents:
        await brain_ai.process_legal_document(doc_data)
    
    # Demo research queries
    demo_queries = [
        {
            "search_terms": ["contract breach", "real estate", "commercial"],
            "legal_areas": ["contract_law", "property_law"],
            "jurisdictions": ["California"],
            "document_types": ["legal_brief", "case_law"]
        },
        {
            "search_terms": ["intellectual property", "licensing", "patents"],
            "legal_areas": ["intellectual_property"],
            "jurisdictions": ["Delaware"],
            "document_types": ["contract", "agreement"]
        },
        {
            "search_terms": ["discrimination", "employment", "Title VII"],
            "legal_areas": ["employment_law"],
            "jurisdictions": ["New York"],
            "document_types": ["complaint", "motion"]
        }
    ]
    
    for query_data in demo_queries:
        await brain_ai.conduct_legal_research(query_data)

# Generate demo data on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Brain AI Legal Research System...")
    await generate_demo_data()
    logger.info(f"Demo data loaded. {len(brain_ai.legal_documents)} documents, {len(brain_ai.research_queries)} research queries.")

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
        <title>Brain AI Legal Research System</title>
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
            
            .document-section, .research-section, .analytics-section {
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
                height: 100px;
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
            
            .document-card, .research-card {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }
            
            .document-title, .research-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            
            .document-info, .research-info {
                color: #495057;
                margin-bottom: 10px;
                line-height: 1.5;
            }
            
            .document-meta, .research-meta {
                display: flex;
                gap: 15px;
                font-size: 12px;
                color: #6c757d;
                flex-wrap: wrap;
            }
            
            .complexity-badge {
                background: #dc3545;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
            }
            
            .quality-badge {
                background: #28a745;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
            }
            
            .relevance-badge {
                background: #007bff;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
            }
            
            .concepts {
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
                margin-top: 8px;
            }
            
            .concept-tag {
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
                <h1>Brain AI Legal Research</h1>
                <p>Intelligent legal research and case analysis platform</p>
            </div>
            
            <div class="main-content">
                <div class="document-section">
                    <div class="section-title">Process Legal Document</div>
                    <div class="form-group">
                        <label>Title:</label>
                        <input type="text" id="docTitle" class="form-control" placeholder="Document title">
                    </div>
                    <div class="form-group">
                        <label>Document Type:</label>
                        <select id="docType" class="form-control">
                            <option value="legal_brief">Legal Brief</option>
                            <option value="contract">Contract</option>
                            <option value="complaint">Complaint</option>
                            <option value="motion">Motion</option>
                            <option value="memorandum">Memorandum</option>
                            <option value="agreement">Agreement</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Court:</label>
                        <input type="text" id="docCourt" class="form-control" placeholder="Court name">
                    </div>
                    <div class="form-group">
                        <label>Jurisdiction:</label>
                        <input type="text" id="docJurisdiction" class="form-control" placeholder="State/Federal">
                    </div>
                    <div class="form-group">
                        <label>Case Number:</label>
                        <input type="text" id="docCaseNumber" class="form-control" placeholder="Case number">
                    </div>
                    <div class="form-group">
                        <label>Document Content:</label>
                        <textarea id="docContent" class="form-control" placeholder="Enter document content..."></textarea>
                    </div>
                    <button class="btn" onclick="processDocument()">Process Document</button>
                </div>
                
                <div class="research-section">
                    <div class="section-title">Conduct Legal Research</div>
                    <div class="form-group">
                        <label>Search Terms (comma-separated):</label>
                        <input type="text" id="searchTerms" class="form-control" placeholder="contract dispute, real estate">
                    </div>
                    <div class="form-group">
                        <label>Legal Areas (comma-separated):</label>
                        <input type="text" id="legalAreas" class="form-control" placeholder="contract_law, property_law">
                    </div>
                    <div class="form-group">
                        <label>Jurisdictions (comma-separated):</label>
                        <input type="text" id="researchJurisdictions" class="form-control" placeholder="California, New York">
                    </div>
                    <div class="form-group">
                        <label>Document Types (comma-separated):</label>
                        <input type="text" id="docTypes" class="form-control" placeholder="legal_brief, case_law">
                    </div>
                    <button class="btn btn-success" onclick="conductResearch()">Conduct Research</button>
                </div>
                
                <div class="analytics-section">
                    <div class="section-title">Legal Research Analytics</div>
                    <button class="btn" onclick="loadAnalytics()">Refresh Analytics</button>
                    <div id="analyticsContent" style="margin-top: 15px;">
                        <p style="color: #6c757d;">Click "Refresh Analytics" to view legal research insights</p>
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
            async function processDocument() {
                const title = document.getElementById('docTitle').value.trim();
                const docType = document.getElementById('docType').value;
                const court = document.getElementById('docCourt').value.trim();
                const jurisdiction = document.getElementById('docJurisdiction').value.trim();
                const caseNumber = document.getElementById('docCaseNumber').value.trim();
                const content = document.getElementById('docContent').value.trim();
                
                if (!title || !content) {
                    alert('Please provide document title and content');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/documents', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            title: title,
                            document_type: docType,
                            content: content,
                            court: court,
                            jurisdiction: jurisdiction,
                            case_number: caseNumber,
                            page_count: Math.ceil(content.split(' ').length / 250) // Estimate pages
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        resultsContent.innerHTML = `
                            <div class="document-card">
                                <div class="document-title">${data.basic_info.title}</div>
                                <div class="document-info">Type: ${data.basic_info.document_type}</div>
                                <div class="document-info">Court: ${data.basic_info.court || 'Not specified'}</div>
                                <div class="document-info">Jurisdiction: ${data.basic_info.jurisdiction || 'Not specified'}</div>
                                <div class="document-meta">
                                    <span class="complexity-badge">Complexity: ${(data.content_analysis.complexity_score * 100).toFixed(1)}%</span>
                                    <span class="quality-badge">Quality: ${(data.quality_metrics.overall_quality * 100).toFixed(1)}%</span>
                                    <span>Word Count: ${data.metadata.word_count}</span>
                                    <span>Legal Entities: ${data.content_analysis.legal_entities.length}</span>
                                </div>
                                <div class="concepts">
                                    ${data.content_analysis.legal_concepts.map(concept => 
                                        `<span class="concept-tag">${concept.category.replace('_', ' ')}</span>`
                                    ).join('')}
                                </div>
                                <div style="margin-top: 15px;">
                                    <strong>Primary Issues:</strong>
                                    <ul style="margin-top: 5px; margin-left: 20px;">
                                        ${data.legal_analysis.primary_issues.map(issue => 
                                            `<li>${issue.type.replace('_', ' ')} (Relevance: ${(issue.relevance_score * 100).toFixed(1)}%)</li>`
                                        ).join('')}
                                    </ul>
                                </div>
                                <div style="margin-top: 10px;">
                                    <strong>Risk Assessment:</strong> ${data.legal_analysis.risk_assessment.overall_risk_level}
                                </div>
                            </div>
                        `;
                        
                        // Clear form
                        document.getElementById('docTitle').value = '';
                        document.getElementById('docCourt').value = '';
                        document.getElementById('docJurisdiction').value = '';
                        document.getElementById('docCaseNumber').value = '';
                        document.getElementById('docContent').value = '';
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error processing document. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error processing document. Please try again.</p>';
                    console.error('Process document error:', error);
                }
            }
            
            async function conductResearch() {
                const searchTerms = document.getElementById('searchTerms').value.split(',').map(t => t.trim()).filter(t => t);
                const legalAreas = document.getElementById('legalAreas').value.split(',').map(a => a.trim()).filter(a => a);
                const jurisdictions = document.getElementById('researchJurisdictions').value.split(',').map(j => j.trim()).filter(j => j);
                const docTypes = document.getElementById('docTypes').value.split(',').map(t => t.trim()).filter(t => t);
                
                if (searchTerms.length === 0) {
                    alert('Please provide at least one search term');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const loadingIndicator = document.getElementById('loadingIndicator');
                const resultsContent = document.getElementById('resultsContent');
                
                resultsSection.style.display = 'block';
                loadingIndicator.classList.add('show');
                resultsContent.innerHTML = '';
                
                try {
                    const response = await fetch('/api/research', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            search_terms: searchTerms,
                            legal_areas: legalAreas,
                            jurisdictions: jurisdictions,
                            document_types: docTypes
                        })
                    });
                    
                    const data = await response.json();
                    loadingIndicator.classList.remove('show');
                    
                    if (response.ok) {
                        if (data.search_results.length === 0) {
                            resultsContent.innerHTML = '<p style="color: #6c757d; text-align: center;">No relevant documents found for your search.</p>';
                            return;
                        }
                        
                        resultsContent.innerHTML = `
                            <div class="research-card">
                                <div class="research-title">Research Results</div>
                                <div class="research-info">
                                    <strong>Query:</strong> ${searchTerms.join(', ')}<br>
                                    <strong>Documents Found:</strong> ${data.result_analysis.total_results}<br>
                                    <strong>Average Relevance:</strong> ${(data.result_analysis.average_relevance * 100).toFixed(1)}%
                                </div>
                                <div class="research-meta">
                                    <span class="relevance-badge">Research Duration: ${data.metadata.research_duration}s</span>
                                    <span>Confidence: ${(data.metadata.confidence_score * 100).toFixed(1)}%</span>
                                </div>
                            </div>
                            
                            ${data.search_results.slice(0, 5).map(result => `
                                <div class="document-card">
                                    <div class="document-title">${result.document.basic_info.title}</div>
                                    <div class="document-info">Type: ${result.document.basic_info.document_type}</div>
                                    <div class="document-meta">
                                        <span class="relevance-badge">Relevance: ${(result.relevance_score * 100).toFixed(1)}%</span>
                                        <span class="complexity-badge">Complexity: ${(result.document.content_analysis.complexity_score * 100).toFixed(1)}%</span>
                                    </div>
                                    <div style="margin-top: 10px;">
                                        <strong>Match Reasons:</strong>
                                        <ul style="margin-top: 5px; margin-left: 20px; font-size: 12px;">
                                            ${result.match_reasons.slice(0, 3).map(reason => `<li>${reason}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                            `).join('')}
                            
                            <div style="background: #fff3cd; padding: 15px; border-radius: 6px; margin-top: 15px;">
                                <strong>Research Insights:</strong>
                                <ul style="margin-top: 10px;">
                                    ${data.research_insights.map(insight => 
                                        `<li>${insight.insight} (Confidence: ${(insight.confidence * 100).toFixed(0)}%)</li>`
                                    ).join('')}
                                </ul>
                            </div>
                            
                            ${data.recommendations.length > 0 ? `
                                <div style="background: #d4edda; padding: 15px; border-radius: 6px; margin-top: 15px;">
                                    <strong>Recommendations:</strong>
                                    <ul style="margin-top: 10px;">
                                        ${data.recommendations.map(rec => 
                                            `<li>${rec.description} (Priority: ${rec.priority})</li>`
                                        ).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        `;
                        
                        // Clear form
                        document.getElementById('searchTerms').value = '';
                        document.getElementById('legalAreas').value = '';
                        document.getElementById('researchJurisdictions').value = '';
                        document.getElementById('docTypes').value = '';
                    } else {
                        resultsContent.innerHTML = '<p style="color: #dc3545;">Error conducting research. Please try again.</p>';
                    }
                    
                } catch (error) {
                    loadingIndicator.classList.remove('show');
                    resultsContent.innerHTML = '<p style="color: #dc3545;">Error conducting research. Please try again.</p>';
                    console.error('Conduct research error:', error);
                }
            }
            
            async function loadAnalytics() {
                const analyticsContent = document.getElementById('analyticsContent');
                
                try {
                    const response = await fetch('/api/analytics');
                    const data = await response.json();
                    
                    if (data.message) {
                        analyticsContent.innerHTML = '<p style="color: #6c757d;">No legal research data available for analytics.</p>';
                        return;
                    }
                    
                    analyticsContent.innerHTML = `
                        <div class="analytics-grid">
                            <div class="analytics-card">
                                <div class="analytics-number">${data.document_metrics.total_documents}</div>
                                <div class="analytics-label">Total Documents</div>
                            </div>
                            <div class="analytics-card">
                                <div class="analytics-number">${data.research_trends.popular_search_terms.length}</div>
                                <div class="analytics-label">Search Terms Tracked</div>
                            </div>
                            <div class="analytics-card">
                                <div class="analytics-number">${(data.document_metrics.average_quality * 100).toFixed(1)}%</div>
                                <div class="analytics-label">Avg Quality Score</div>
                            </div>
                            <div class="analytics-card">
                                <div class="analytics-number">${data.citation_analysis.total_citations}</div>
                                <div class="analytics-label">Total Citations</div>
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Document Type Distribution</h4>
                        <div style="margin-top: 10px;">
                            ${Object.entries(data.document_metrics.document_type_distribution).map(([type, count]) => `
                                <span class="concept-tag" style="margin-right: 5px; margin-bottom: 5px;">${type}: ${count}</span>
                            `).join('')}
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Popular Search Terms</h4>
                        <div style="margin-top: 10px;">
                            ${data.research_trends.popular_search_terms.slice(0, 5).map(term => `
                                <span class="concept-tag" style="margin-right: 5px; margin-bottom: 5px;">${term.term}: ${term.frequency}</span>
                            `).join('')}
                        </div>
                        
                        <h4 style="margin-top: 20px; color: #2c3e50;">Most Researched Legal Areas</h4>
                        <div style="margin-top: 10px;">
                            ${data.legal_topic_analysis.most_researched_areas.slice(0, 5).map(area => `
                                <span class="concept-tag" style="margin-right: 5px; margin-bottom: 5px;">${area[0].replace('_', ' ')}: ${area[1]}</span>
                            `).join('')}
                        </div>
                        
                        ${data.recommendations.length > 0 ? `
                            <h4 style="margin-top: 20px; color: #2c3e50;">Platform Recommendations</h4>
                            <div style="margin-top: 10px;">
                                ${data.recommendations.map(rec => `
                                    <div style="background: #fff3cd; padding: 10px; border-radius: 4px; margin-bottom: 5px;">
                                        <strong>${rec.area}:</strong> ${rec.recommendation} (Priority: ${rec.priority})
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    `;
                    
                } catch (error) {
                    analyticsContent.innerHTML = '<p style="color: #dc3545;">Error loading analytics. Please try again.</p>';
                    console.error('Analytics error:', error);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/documents")
async def process_legal_document(document: LegalDocument):
    """Process and analyze legal document"""
    try:
        document_dict = document.dict()
        result = await brain_ai.process_legal_document(document_dict)
        return result
    except Exception as e:
        logger.error(f"Error processing legal document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def get_legal_documents():
    """Get all legal documents"""
    try:
        documents = list(brain_ai.legal_documents.values())
        return documents
    except Exception as e:
        logger.error(f"Error getting legal documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research")
async def conduct_legal_research(query: LegalResearchQuery):
    """Conduct legal research"""
    try:
        query_dict = query.dict()
        result = await brain_ai.conduct_legal_research(query_dict)
        return result
    except Exception as e:
        logger.error(f"Error conducting legal research: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/research")
async def get_research_queries():
    """Get all research queries"""
    try:
        queries = list(brain_ai.research_queries.values())
        return queries
    except Exception as e:
        logger.error(f"Error getting research queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_legal_research_analytics():
    """Get legal research analytics"""
    try:
        analytics = await brain_ai.get_legal_research_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{document_id}")
async def get_legal_document(document_id: str):
    """Get specific legal document"""
    try:
        if document_id not in brain_ai.legal_documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return brain_ai.legal_documents[document_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting legal document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/research/{research_id}")
async def get_research_query(research_id: str):
    """Get specific research query"""
    try:
        if research_id not in brain_ai.research_queries:
            raise HTTPException(status_code=404, detail="Research query not found")
        
        return brain_ai.research_queries[research_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")