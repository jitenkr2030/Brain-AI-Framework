"""
Compliance Monitor - Brain AI Framework Example
A comprehensive compliance monitoring system that helps organizations track regulatory compliance,
manage audits, and ensure governance standards using Brain AI Framework.
"""

import json
import asyncio
import uvicorn
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import sys
import os
import math
import statistics
import random

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from loguru import logger
from dataclasses import dataclass
from enum import Enum

# Import shared components
from shared.brain_ai_integration import BrainAIIntegration, BrainAIMemory
from shared.demo_data import DemoDataGenerator
from shared.web_components import WebComponents

# Configure logging
logger.add("logs/compliance_monitor.log", rotation="10 MB", level="INFO")

class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    UNDER_REVIEW = "under_review"
    REQUIRES_ATTENTION = "requires_attention"
    EXEMPT = "exempt"

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditStatus(Enum):
    """Audit status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REPORTED = "reported"
    CLOSED = "closed"

class FrameworkType(Enum):
    """Compliance framework enumeration"""
    SOX = "sox"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    NIST_CSF = "nist_csf"
    COSO = "coso"

class ControlType(Enum):
    """Control type enumeration"""
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    DIRECTIVE = "directive"

@dataclass
class ComplianceMetric:
    """Compliance metric data point"""
    metric_name: str
    value: float
    target: float
    threshold: float
    unit: str
    timestamp: datetime
    status: ComplianceStatus

@dataclass
class AuditFinding:
    """Audit finding data point"""
    finding_id: str
    audit_id: str
    finding_type: str
    severity: RiskLevel
    description: str
    evidence: List[str]
    recommendation: str
    due_date: datetime
    status: str
    owner: str

class ComplianceFramework(BaseModel):
    """Compliance framework model"""
    framework_id: str
    name: str
    framework_type: FrameworkType
    version: str
    description: str
    effective_date: datetime
    last_updated: datetime
    controls_count: int
    compliance_score: float
    last_assessment: datetime
    next_assessment: datetime
    requirements: List[str]

class ComplianceControl(BaseModel):
    """Compliance control model"""
    control_id: str
    framework_id: str
    control_number: str
    title: str
    description: str
    control_type: ControlType
    status: ComplianceStatus
    owner: str
    frequency: str
    last_test: Optional[datetime]
    next_test: datetime
    effectiveness_score: float
    documentation_status: str
    testing_procedures: List[str]

class ComplianceAssessment(BaseModel):
    """Compliance assessment model"""
    assessment_id: str
    framework_id: str
    assessment_type: str
    assessor: str
    start_date: datetime
    end_date: Optional[datetime]
    scope: List[str]
    overall_status: ComplianceStatus
    compliance_score: float
    findings_count: int
    recommendations: List[str]
    action_items: List[Dict]
    evidence_collected: List[str]

class Audit(BaseModel):
    """Audit model"""
    audit_id: str
    framework_id: str
    audit_name: str
    audit_type: str
    auditor: str
    start_date: datetime
    end_date: Optional[datetime]
    scope: List[str]
    status: AuditStatus
    findings_count: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    closure_date: Optional[datetime]
    report_date: Optional[datetime]

class ComplianceRisk(BaseModel):
    """Compliance risk model"""
    risk_id: str
    framework_id: str
    risk_title: str
    risk_description: str
    risk_category: str
    likelihood: RiskLevel
    impact: RiskLevel
    risk_score: float
    status: ComplianceStatus
    owner: str
    mitigation_plan: str
    due_date: Optional[datetime]
    last_review: datetime
    next_review: datetime

class RegulatoryChange(BaseModel):
    """Regulatory change model"""
    change_id: str
    framework_id: str
    change_title: str
    change_description: str
    effective_date: datetime
    impact_assessment: str
    affected_controls: List[str]
    implementation_required: bool
    deadline: Optional[datetime]
    status: str
    assigned_to: str

class ComplianceAI:
    """Main compliance monitoring AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.frameworks: Dict[str, ComplianceFramework] = {}
        self.controls: Dict[str, ComplianceControl] = {}
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.audits: Dict[str, Audit] = {}
        self.compliance_risks: Dict[str, ComplianceRisk] = {}
        self.regulatory_changes: Dict[str, RegulatoryChange] = {}
        self.audit_findings: Dict[str, AuditFinding] = {}
        self.compliance_metrics: List[ComplianceMetric] = []
        
        # Compliance monitoring configuration
        self.compliance_config = {
            "assessment_frequency": "annual",
            "audit_frequency": "annual",
            "risk_review_frequency": "quarterly",
            "regulatory_tracking": True,
            "automated_testing": True,
            "real_time_monitoring": True
        }
        
        # Framework-specific configurations
        self.framework_configs = self._initialize_framework_configs()
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_framework_configs(self) -> Dict:
        """Initialize framework-specific configurations"""
        return {
            FrameworkType.SOX: {
                "controls_count": 65,
                "assessment_frequency": "quarterly",
                "key_areas": ["Internal Controls", "Financial Reporting", "IT General Controls"]
            },
            FrameworkType.GDPR: {
                "controls_count": 99,
                "assessment_frequency": "continuous",
                "key_areas": ["Data Protection", "Privacy Rights", "Consent Management"]
            },
            FrameworkType.HIPAA: {
                "controls_count": 45,
                "assessment_frequency": "annual",
                "key_areas": ["Administrative Safeguards", "Physical Safeguards", "Technical Safeguards"]
            },
            FrameworkType.ISO27001: {
                "controls_count": 114,
                "assessment_frequency": "annual",
                "key_areas": ["Information Security", "Risk Management", "Access Control"]
            },
            FrameworkType.PCI_DSS: {
                "controls_count": 12,
                "assessment_frequency": "quarterly",
                "key_areas": ["Network Security", "Data Protection", "Access Control"]
            }
        }
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo compliance frameworks
        for i, framework_type in enumerate(FrameworkType):
            framework = self.demo_data.generate_compliance_framework(
                framework_id=f"FW_{i+1:03d}",
                framework_type=framework_type,
                config=self.framework_configs.get(framework_type, {})
            )
            self.frameworks[framework.framework_id] = framework
        
        # Generate demo compliance controls
        for framework_id, framework in self.frameworks.items():
            for i in range(random.randint(20, 50)):  # 20-50 controls per framework
                control = self.demo_data.generate_compliance_control(
                    control_id=f"CTRL_{framework_id}_{i+1:03d}",
                    framework_id=framework_id,
                    control_type=random.choice(list(ControlType))
                )
                self.controls[control.control_id] = control
        
        # Generate demo compliance assessments
        for i in range(75):
            assessment = self.demo_data.generate_compliance_assessment(
                assessment_id=f"ASSESS_{i+1:03d}",
                framework_ids=list(self.frameworks.keys())
            )
            self.assessments[assessment.assessment_id] = assessment
        
        # Generate demo audits
        for i in range(50):
            audit = self.demo_data.generate_audit(
                audit_id=f"AUDIT_{i+1:03d}",
                framework_ids=list(self.frameworks.keys())
            )
            self.audits[audit.audit_id] = audit
        
        # Generate compliance risks
        self._generate_compliance_risks()
        
        # Generate regulatory changes
        self._generate_regulatory_changes()
        
        # Generate audit findings
        self._generate_audit_findings()
        
        # Generate compliance metrics
        self._generate_compliance_metrics()
        
        logger.info(f"Initialized demo data: {len(self.frameworks)} frameworks, "
                   f"{len(self.controls)} controls, {len(self.assessments)} assessments")
    
    def _generate_compliance_risks(self):
        """Generate compliance risks"""
        risk_categories = [
            "Regulatory Change", "Control Failure", "Documentation Gap", "Resource Constraint",
            "Technology Risk", "Process Risk", "Human Error", "Vendor Risk", "Data Risk", "Privacy Risk"
        ]
        
        for i in range(60):
            framework_id = random.choice(list(self.frameworks.keys()))
            framework = self.frameworks[framework_id]
            
            risk = ComplianceRisk(
                risk_id=f"RISK_{i+1:03d}",
                framework_id=framework_id,
                risk_title=f"Compliance Risk {i+1}",
                risk_description=self._generate_risk_description(),
                risk_category=random.choice(risk_categories),
                likelihood=random.choice(list(RiskLevel)),
                impact=random.choice(list(RiskLevel)),
                risk_score=random.uniform(1, 25),
                status=random.choice(list(ComplianceStatus)),
                owner=f"Owner_{random.randint(1, 20):03d}",
                mitigation_plan=self._generate_mitigation_plan(),
                due_date=datetime.now() + timedelta(days=random.randint(30, 180)),
                last_review=datetime.now() - timedelta(days=random.randint(1, 90)),
                next_review=datetime.now() + timedelta(days=random.randint(30, 90))
            )
            
            self.compliance_risks[risk.risk_id] = risk
    
    def _generate_risk_description(self) -> str:
        """Generate risk description"""
        descriptions = [
            "Potential non-compliance with data protection requirements",
            "Control deficiency in access management processes",
            "Insufficient documentation for compliance evidence",
            "Resource constraints affecting compliance activities",
            "Technology gaps in compliance monitoring",
            "Process gaps in risk assessment procedures",
            "Human error risk in compliance activities",
            "Third-party vendor compliance risk",
            "Data classification and handling risk",
            "Privacy impact assessment gaps"
        ]
        return random.choice(descriptions)
    
    def _generate_mitigation_plan(self) -> str:
        """Generate mitigation plan"""
        plans = [
            "Implement additional control procedures",
            "Enhance staff training and awareness",
            "Upgrade compliance monitoring tools",
            "Review and update policies and procedures",
            "Engage external compliance consultants",
            "Implement automated compliance testing",
            "Strengthen vendor management processes",
            "Enhance data protection measures",
            "Improve documentation and evidence collection",
            "Regular compliance review and updates"
        ]
        return random.choice(plans)
    
    def _generate_regulatory_changes(self):
        """Generate regulatory changes"""
        change_templates = [
            {
                "title": "Updated Data Protection Requirements",
                "description": "New data protection obligations require process updates",
                "impact": "High"
            },
            {
                "title": "Enhanced Security Control Standards",
                "description": "Stricter security control requirements implemented",
                "impact": "Medium"
            },
            {
                "title": "Modified Reporting Requirements",
                "description": "Changes to compliance reporting formats and timelines",
                "impact": "Low"
            },
            {
                "title": "New Privacy Rights Implementation",
                "description": "Additional privacy rights require system modifications",
                "impact": "High"
            },
            {
                "title": "Updated Risk Assessment Framework",
                "description": "Modified risk assessment methodology and criteria",
                "impact": "Medium"
            }
        ]
        
        for i, template in enumerate(change_templates):
            framework_id = random.choice(list(self.frameworks.keys()))
            
            change = RegulatoryChange(
                change_id=f"CHANGE_{i+1:03d}",
                framework_id=framework_id,
                change_title=template["title"],
                change_description=template["description"],
                effective_date=datetime.now() + timedelta(days=random.randint(30, 180)),
                impact_assessment=template["impact"],
                affected_controls=random.sample(list(self.controls.keys()), random.randint(3, 8)),
                implementation_required=True,
                deadline=datetime.now() + timedelta(days=random.randint(60, 270)),
                status=random.choice(["pending", "in_progress", "completed"]),
                assigned_to=f"Assignee_{random.randint(1, 15):03d}"
            )
            
            self.regulatory_changes[change.change_id] = change
    
    def _generate_audit_findings(self):
        """Generate audit findings"""
        finding_types = [
            "Control Deficiency", "Documentation Gap", "Process Weakness", "Policy Violation",
            "Training Deficiency", "Technology Gap", "Risk Management Issue", "Compliance Gap"
        ]
        
        for audit in list(self.audits.values())[:30]:  # Generate findings for 30 audits
            findings_count = random.randint(2, 15)
            
            for i in range(findings_count):
                finding = AuditFinding(
                    finding_id=f"FINDING_{audit.audit_id}_{i+1:02d}",
                    audit_id=audit.audit_id,
                    finding_type=random.choice(finding_types),
                    severity=random.choice(list(RiskLevel)),
                    description=self._generate_finding_description(),
                    evidence=self._generate_evidence(),
                    recommendation=self._generate_recommendation(),
                    due_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                    status=random.choice(["open", "in_progress", "resolved", "closed"]),
                    owner=f"Owner_{random.randint(1, 25):03d}"
                )
                
                self.audit_findings[finding.finding_id] = finding
    
    def _generate_finding_description(self) -> str:
        """Generate finding description"""
        descriptions = [
            "Access control procedures not consistently followed",
            "Insufficient documentation of compliance activities",
            "Risk assessment methodology needs improvement",
            "Staff training on compliance requirements inadequate",
            "Technology controls require enhancement",
            "Policy review and update process insufficient",
            "Vendor compliance monitoring needs strengthening",
            "Data protection measures require enhancement"
        ]
        return random.choice(descriptions)
    
    def _generate_evidence(self) -> List[str]:
        """Generate evidence items"""
        evidence_templates = [
            "System access logs",
            "Training completion records",
            "Policy documents",
            "Risk assessment reports",
            "Control testing results",
            "Vendor assessment reports",
            "Compliance monitoring reports",
            "Incident response documentation"
        ]
        return random.sample(evidence_templates, random.randint(2, 4))
    
    def _generate_recommendation(self) -> str:
        """Generate recommendation"""
        recommendations = [
            "Implement enhanced access control procedures",
            "Update and document compliance processes",
            "Improve risk assessment methodology",
            "Enhance staff training programs",
            "Upgrade compliance monitoring technology",
            "Strengthen policy management procedures",
            "Enhance vendor compliance monitoring",
            "Improve data protection controls"
        ]
        return random.choice(recommendations)
    
    def _generate_compliance_metrics(self):
        """Generate compliance metrics"""
        metric_names = [
            "compliance_score", "control_effectiveness", "audit_findings_rate",
            "remediation_completion_rate", "regulatory_readiness", "risk_maturity",
            "training_completion_rate", "policy_compliance", "incident_rate"
        ]
        
        for metric_name in metric_names:
            metric = ComplianceMetric(
                metric_name=metric_name,
                value=random.uniform(60, 95),
                target=random.uniform(85, 98),
                threshold=random.uniform(70, 80),
                unit="percentage" if "rate" in metric_name or "score" in metric_name else "count",
                timestamp=datetime.now() - timedelta(hours=random.randint(0, 24)),
                status=random.choice(list(ComplianceStatus))
            )
            
            self.compliance_metrics.append(metric)
    
    async def analyze_compliance_gap(self, framework_id: str) -> Dict:
        """Analyze compliance gaps using Brain AI"""
        try:
            framework = self.frameworks.get(framework_id)
            if not framework:
                raise ValueError(f"Framework {framework_id} not found")
            
            # Prepare gap analysis context
            analysis_context = {
                "framework_info": framework.dict(),
                "controls": [ctrl.dict() for ctrl in self.controls.values() if ctrl.framework_id == framework_id],
                "assessments": [assess.dict() for assess in self.assessments.values() if assess.framework_id == framework_id],
                "audits": [audit.dict() for audit in self.audits.values() if audit.framework_id == framework_id],
                "findings": [finding.__dict__ for finding in self.audit_findings.values() 
                           if finding.audit_id in [a.audit_id for a in self.audits.values() if a.framework_id == framework_id]],
                "regulatory_changes": [change.dict() for change in self.regulatory_changes.values() if change.framework_id == framework_id],
                "industry_benchmarks": self._get_industry_benchmarks(),
                "best_practices": self._get_compliance_best_practices()
            }
            
            # Use Brain AI to analyze compliance gaps
            ai_analysis = await self.brain_ai.process_compliance_gap_analysis(analysis_context)
            
            # Generate gap analysis results
            gap_analysis = {
                "framework_id": framework_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "overall_compliance_score": framework.compliance_score,
                "gap_analysis": self._perform_detailed_gap_analysis(framework),
                "control_effectiveness": self._assess_control_effectiveness(framework_id),
                "risk_assessment": self._assess_compliance_risks(framework_id),
                "remediation_plan": self._generate_remediation_plan(framework_id),
                "priority_actions": self._identify_priority_actions(framework_id),
                "resource_requirements": self._calculate_resource_requirements(framework_id),
                "timeline_estimates": self._generate_timeline_estimates(framework_id),
                "ai_insights": ai_analysis
            }
            
            logger.info(f"Analyzed compliance gaps for framework {framework_id}")
            
            return gap_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing compliance gap: {str(e)}")
            raise
    
    def _perform_detailed_gap_analysis(self, framework: ComplianceFramework) -> Dict:
        """Perform detailed gap analysis"""
        framework_controls = [ctrl for ctrl in self.controls.values() if ctrl.framework_id == framework.framework_id]
        
        # Analyze compliance status distribution
        status_counts = {}
        for ctrl in framework_controls:
            status = ctrl.status
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
        
        # Calculate gap severity
        critical_gaps = len([ctrl for ctrl in framework_controls if ctrl.status == ComplianceStatus.NON_COMPLIANT])
        partial_gaps = len([ctrl for ctrl in framework_controls if ctrl.status == ComplianceStatus.PARTIAL_COMPLIANCE])
        
        # Identify key gaps
        key_gaps = []
        for ctrl in framework_controls:
            if ctrl.status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIAL_COMPLIANCE]:
                gap = {
                    "control_id": ctrl.control_id,
                    "control_title": ctrl.title,
                    "gap_type": ctrl.status.value,
                    "severity": "high" if ctrl.status == ComplianceStatus.NON_COMPLIANT else "medium",
                    "impact": f"Affects {framework.name} compliance",
                    "remediation_effort": random.choice(["low", "medium", "high"])
                }
                key_gaps.append(gap)
        
        return {
            "total_controls": len(framework_controls),
            "compliant_controls": status_counts.get("compliant", 0),
            "non_compliant_controls": status_counts.get("non_compliant", 0),
            "partial_compliant_controls": status_counts.get("partial_compliance", 0),
            "critical_gaps": critical_gaps,
            "partial_gaps": partial_gaps,
            "key_gaps": key_gaps,
            "gap_percentage": ((critical_gaps + partial_gaps) / len(framework_controls)) * 100 if framework_controls else 0,
            "remediation_priority": self._calculate_remediation_priority(critical_gaps, partial_gaps)
        }
    
    def _assess_control_effectiveness(self, framework_id: str) -> Dict:
        """Assess control effectiveness"""
        framework_controls = [ctrl for ctrl in self.controls.values() if ctrl.framework_id == framework_id]
        
        if not framework_controls:
            return {"message": "No controls found for framework"}
        
        # Calculate effectiveness metrics
        total_controls = len(framework_controls)
        effective_controls = len([ctrl for ctrl in framework_controls if ctrl.effectiveness_score >= 80])
        moderately_effective = len([ctrl for ctrl in framework_controls if 60 <= ctrl.effectiveness_score < 80])
        ineffective_controls = len([ctrl for ctrl in framework_controls if ctrl.effectiveness_score < 60])
        
        # Analyze by control type
        control_type_effectiveness = {}
        for ctrl_type in ControlType:
            type_controls = [ctrl for ctrl in framework_controls if ctrl.control_type == ctrl_type]
            if type_controls:
                avg_effectiveness = sum(ctrl.effectiveness_score for ctrl in type_controls) / len(type_controls)
                control_type_effectiveness[ctrl_type.value] = {
                    "count": len(type_controls),
                    "average_effectiveness": avg_effectiveness
                }
        
        return {
            "total_controls": total_controls,
            "highly_effective": effective_controls,
            "moderately_effective": moderately_effective,
            "ineffective": ineffective_controls,
            "effectiveness_rate": (effective_controls / total_controls) * 100 if total_controls > 0 else 0,
            "control_type_effectiveness": control_type_effectiveness,
            "improvement_opportunities": ineffective_controls + moderately_effective,
            "testing_coverage": len([ctrl for ctrl in framework_controls if ctrl.last_test]) / total_controls * 100 if total_controls > 0 else 0
        }
    
    def _assess_compliance_risks(self, framework_id: str) -> Dict:
        """Assess compliance risks"""
        framework_risks = [risk for risk in self.compliance_risks.values() if risk.framework_id == framework_id]
        
        if not framework_risks:
            return {"message": "No risks found for framework"}
        
        # Analyze risk distribution
        risk_by_level = {}
        for risk_level in RiskLevel:
            risk_by_level[risk_level.value] = len([risk for risk in framework_risks if risk.likelihood == risk_level or risk.impact == risk_level])
        
        # Calculate risk score distribution
        high_risks = [risk for risk in framework_risks if risk.risk_score >= 15]
        medium_risks = [risk for risk in framework_risks if 8 <= risk.risk_score < 15]
        low_risks = [risk for risk in framework_risks if risk.risk_score < 8]
        
        # Identify top risks
        top_risks = sorted(framework_risks, key=lambda x: x.risk_score, reverse=True)[:5]
        
        return {
            "total_risks": len(framework_risks),
            "high_risks": len(high_risks),
            "medium_risks": len(medium_risks),
            "low_risks": len(low_risks),
            "risk_distribution": risk_by_level,
            "top_risks": [
                {
                    "risk_id": risk.risk_id,
                    "title": risk.risk_title,
                    "score": risk.risk_score,
                    "status": risk.status.value,
                    "owner": risk.owner
                } for risk in top_risks
            ],
            "risk_maturity_score": random.uniform(60, 85),
            "overdue_mitigations": len([risk for risk in framework_risks 
                                      if risk.due_date and risk.due_date < datetime.now() and risk.status != ComplianceStatus.COMPLIANT])
        }
    
    def _generate_remediation_plan(self, framework_id: str) -> Dict:
        """Generate remediation plan"""
        framework_controls = [ctrl for ctrl in self.controls.values() if ctrl.framework_id == framework_id]
        non_compliant = [ctrl for ctrl in framework_controls if ctrl.status == ComplianceStatus.NON_COMPLIANT]
        partial_compliant = [ctrl for ctrl in framework_controls if ctrl.status == ComplianceStatus.PARTIAL_COMPLIANCE]
        
        # Prioritize remediation efforts
        immediate_actions = [ctrl for ctrl in non_compliant if ctrl.effectiveness_score < 50]
        short_term_actions = [ctrl for ctrl in non_compliant if ctrl.effectiveness_score >= 50]
        medium_term_actions = partial_compliant
        
        return {
            "immediate_actions": [
                {
                    "action": f"Remediate {ctrl.title}",
                    "timeline": "0-30 days",
                    "resources": random.choice(["High", "Medium", "Low"]),
                    "complexity": random.choice(["High", "Medium", "Low"])
                } for ctrl in immediate_actions[:5]  # Limit to top 5
            ],
            "short_term_actions": [
                {
                    "action": f"Enhance {ctrl.title}",
                    "timeline": "30-90 days",
                    "resources": random.choice(["Medium", "Low"]),
                    "complexity": random.choice(["Medium", "Low"])
                } for ctrl in short_term_actions[:5]
            ],
            "medium_term_actions": [
                {
                    "action": f"Optimize {ctrl.title}",
                    "timeline": "90-180 days",
                    "resources": "Low",
                    "complexity": "Low"
                } for ctrl in medium_term_actions[:5]
            ],
            "total_effort_estimate": {
                "person_days": random.randint(50, 200),
                "budget_required": f"${random.randint(25000, 150000)}",
                "external_resources": random.choice([True, False])
            },
            "success_criteria": [
                "Achieve 95% compliance score",
                "Zero critical findings",
                "Effective control implementation",
                "Documentation completeness"
            ]
        }
    
    def _identify_priority_actions(self, framework_id: str) -> List[str]:
        """Identify priority actions"""
        framework_controls = [ctrl for ctrl in self.controls.values() if ctrl.framework_id == framework_id]
        framework_risks = [risk for risk in self.compliance_risks.values() if risk.framework_id == framework_id]
        
        actions = []
        
        # Control-based actions
        critical_controls = [ctrl for ctrl in framework_controls if ctrl.status == ComplianceStatus.NON_COMPLIANT]
        if critical_controls:
            actions.append(f"Address {len(critical_controls)} non-compliant controls immediately")
        
        # Risk-based actions
        high_risks = [risk for risk in framework_risks if risk.risk_score >= 15]
        if high_risks:
            actions.append(f"Mitigate {len(high_risks)} high-risk compliance issues")
        
        # Process-based actions
        untested_controls = [ctrl for ctrl in framework_controls if not ctrl.last_test]
        if untested_controls:
            actions.append(f"Complete testing for {len(untested_controls)} untested controls")
        
        # Documentation-based actions
        undocumented_controls = [ctrl for ctrl in framework_controls if ctrl.documentation_status == "incomplete"]
        if undocumented_controls:
            actions.append(f"Complete documentation for {len(undocumented_controls)} controls")
        
        return actions[:6]  # Limit to 6 priority actions
    
    def _calculate_resource_requirements(self, framework_id: str) -> Dict:
        """Calculate resource requirements"""
        framework_controls = [ctrl for ctrl in self.controls.values() if ctrl.framework_id == framework_id]
        
        # Estimate personnel requirements
        compliance_officers = random.randint(2, 8)
        internal_auditors = random.randint(1, 4)
        external_consultants = random.randint(0, 3)
        
        # Estimate technology requirements
        compliance_tools = random.choice([True, False])
        automation_tools = random.choice([True, False])
        reporting_tools = random.choice([True, False])
        
        return {
            "personnel": {
                "compliance_officers": compliance_officers,
                "internal_auditors": internal_auditors,
                "external_consultants": external_consultants,
                "total_fte": compliance_officers + internal_auditors + (external_consultants * 0.5)
            },
            "technology": {
                "compliance_tools": compliance_tools,
                "automation_tools": automation_tools,
                "reporting_tools": reporting_tools,
                "integration_requirements": random.choice(["High", "Medium", "Low"])
            },
            "budget": {
                "personnel_cost": f"${random.randint(200000, 800000)}",
                "technology_cost": f"${random.randint(50000, 300000)}",
                "consulting_cost": f"${random.randint(100000, 500000)}",
                "total_estimated": f"${random.randint(350000, 1600000)}"
            }
        }
    
    def _generate_timeline_estimates(self, framework_id: str) -> Dict:
        """Generate timeline estimates"""
        framework_controls = [ctrl for ctrl in self.controls.values() if ctrl.framework_id == framework_id]
        non_compliant_count = len([ctrl for ctrl in framework_controls if ctrl.status == ComplianceStatus.NON_COMPLIANT])
        
        # Base timeline on gap severity
        base_months = max(3, non_compliant_count * 0.5)  # Minimum 3 months
        
        return {
            "immediate_phase": {
                "duration": "0-30 days",
                "activities": ["Critical gap remediation", "Emergency controls", "Risk mitigation"],
                "resources": "High priority"
            },
            "short_term_phase": {
                "duration": "1-3 months",
                "activities": ["Control enhancement", "Process improvement", "Staff training"],
                "resources": "Medium priority"
            },
            "medium_term_phase": {
                "duration": "3-6 months",
                "activities": ["System optimization", "Automation implementation", "Monitoring enhancement"],
                "resources": "Standard priority"
            },
            "long_term_phase": {
                "duration": "6-12 months",
                "activities": ["Continuous improvement", "Advanced analytics", "Maturity advancement"],
                "resources": "Ongoing"
            },
            "total_timeline": f"{base_months:.1f} months",
            "critical_milestones": [
                "30 days: Critical gaps addressed",
                "90 days: Primary remediation complete",
                "180 days: Full compliance achieved",
                "365 days: Continuous monitoring established"
            ]
        }
    
    def _calculate_remediation_priority(self, critical_gaps: int, partial_gaps: int) -> str:
        """Calculate remediation priority"""
        if critical_gaps > 5:
            return "Critical"
        elif critical_gaps > 2 or partial_gaps > 10:
            return "High"
        elif critical_gaps > 0 or partial_gaps > 5:
            return "Medium"
        else:
            return "Low"
    
    def _get_industry_benchmarks(self) -> Dict:
        """Get industry benchmarks"""
        return {
            "compliance_score_benchmark": random.uniform(75, 90),
            "control_effectiveness_benchmark": random.uniform(80, 95),
            "audit_findings_rate_benchmark": random.uniform(5, 15),
            "remediation_time_benchmark": random.uniform(30, 90),
            "industry_percentile": random.randint(50, 95)
        }
    
    def _get_compliance_best_practices(self) -> List[str]:
        """Get compliance best practices"""
        return [
            "Implement automated compliance monitoring",
            "Establish continuous control testing",
            "Maintain comprehensive documentation",
            "Regular compliance training programs",
            "Integrated risk and compliance management",
            "Real-time compliance dashboards",
            "Proactive regulatory change management",
            "Third-party risk assessment programs"
        ]
    
    def predict_compliance_trends(self, timeframe: str = "12_months") -> Dict:
        """Predict compliance trends using AI analysis"""
        try:
            # Prepare trend analysis context
            trend_context = {
                "historical_assessments": [assess.dict() for assess in list(self.assessments.values())[-50:]],
                "historical_audits": [audit.dict() for audit in list(self.audits.values())[-30:]],
                "compliance_metrics": [metric.__dict__ for metric in self.compliance_metrics[-100:]],
                "regulatory_changes": [change.dict() for change in self.regulatory_changes.values()],
                "industry_trends": self._get_industry_compliance_trends(),
                "timeframe": timeframe
            }
            
            # Generate trend predictions
            predictions = {
                "prediction_timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "compliance_trend_predictions": self._generate_compliance_trend_predictions(),
                "risk_predictions": self._generate_risk_predictions(),
                "audit_predictions": self._generate_audit_predictions(),
                "regulatory_predictions": self._generate_regulatory_predictions(),
                "resource_projections": self._generate_resource_projections(),
                "confidence_scores": self._calculate_prediction_confidence(),
                "recommendations": self._generate_trend_recommendations()
            }
            
            logger.info(f"Generated compliance trend predictions for {timeframe}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting compliance trends: {str(e)}")
            raise
    
    def _generate_compliance_trend_predictions(self) -> List[Dict]:
        """Generate compliance trend predictions"""
        frameworks = list(self.frameworks.values())
        predictions = []
        
        for framework in frameworks:
            prediction = {
                "framework_id": framework.framework_id,
                "framework_name": framework.name,
                "current_score": framework.compliance_score,
                "predicted_score_3m": framework.compliance_score + random.uniform(-5, 8),
                "predicted_score_6m": framework.compliance_score + random.uniform(-3, 12),
                "predicted_score_12m": framework.compliance_score + random.uniform(0, 15),
                "trend_direction": random.choice(["improving", "stable", "declining"]),
                "confidence": random.uniform(0.7, 0.9),
                "key_factors": [
                    "Regulatory changes impact",
                    "Control effectiveness improvements",
                    "Resource allocation changes",
                    "Technology automation adoption"
                ]
            }
            predictions.append(prediction)
        
        return predictions
    
    def _generate_risk_predictions(self) -> List[Dict]:
        """Generate risk predictions"""
        risk_categories = list(set(risk.risk_category for risk in self.compliance_risks.values()))
        predictions = []
        
        for category in risk_categories:
            category_risks = [risk for risk in self.compliance_risks.values() if risk.risk_category == category]
            avg_current_score = sum(risk.risk_score for risk in category_risks) / len(category_risks)
            
            prediction = {
                "risk_category": category,
                "current_avg_score": avg_current_score,
                "predicted_score_3m": avg_current_score + random.uniform(-3, 5),
                "predicted_score_6m": avg_current_score + random.uniform(-2, 8),
                "risk_trend": random.choice(["decreasing", "stable", "increasing"]),
                "emerging_risks": random.randint(1, 3),
                "mitigation_effectiveness": random.uniform(0.6, 0.9),
                "confidence": random.uniform(0.6, 0.85)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _generate_audit_predictions(self) -> List[Dict]:
        """Generate audit predictions"""
        frameworks = list(self.frameworks.values())
        predictions = []
        
        for framework in frameworks:
            framework_audits = [audit for audit in self.audits.values() if audit.framework_id == framework.framework_id]
            avg_findings = sum(audit.findings_count for audit in framework_audits) / len(framework_audits) if framework_audits else 0
            
            prediction = {
                "framework_id": framework.framework_id,
                "framework_name": framework.name,
                "current_avg_findings": avg_findings,
                "predicted_findings_3m": avg_findings + random.uniform(-2, 3),
                "predicted_findings_6m": avg_findings + random.uniform(-1, 5),
                "audit_frequency": random.choice(["annual", "semi-annual", "quarterly"]),
                "findings_trend": random.choice(["decreasing", "stable", "increasing"]),
                "compliance_maturity": random.choice(["initial", "managed", "defined", "optimized"]),
                "confidence": random.uniform(0.65, 0.9)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _generate_regulatory_predictions(self) -> List[Dict]:
        """Generate regulatory predictions"""
        framework_types = list(FrameworkType)
        predictions = []
        
        for framework_type in framework_types:
            framework = next((f for f in self.frameworks.values() if f.framework_type == framework_type), None)
            if not framework:
                continue
            
            framework_changes = [change for change in self.regulatory_changes.values() 
                               if change.framework_id == framework.framework_id]
            
            prediction = {
                "framework_type": framework_type.value,
                "framework_name": framework.name,
                "pending_changes": len(framework_changes),
                "predicted_changes_3m": random.randint(1, 4),
                "predicted_changes_6m": random.randint(2, 8),
                "implementation_difficulty": random.choice(["low", "medium", "high"]),
                "impact_assessment": random.choice(["minimal", "moderate", "significant", "transformative"]),
                "readiness_score": random.uniform(60, 95),
                "confidence": random.uniform(0.6, 0.85)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _generate_resource_projections(self) -> Dict:
        """Generate resource projections"""
        return {
            "personnel_projections": {
                "current_fte": random.randint(8, 25),
                "projected_fte_6m": random.randint(10, 30),
                "projected_fte_12m": random.randint(12, 35),
                "skill_gaps_identified": random.randint(2, 8),
                "training_requirements": random.randint(5, 20)
            },
            "technology_projections": {
                "current_tools": random.randint(3, 8),
                "projected_tools_6m": random.randint(4, 10),
                "projected_tools_12m": random.randint(5, 12),
                "automation_adoption": random.uniform(30, 70),
                "integration_complexity": random.choice(["low", "medium", "high"])
            },
            "budget_projections": {
                "current_annual_budget": f"${random.randint(500000, 2000000)}",
                "projected_budget_6m": f"${random.randint(600000, 2500000)}",
                "projected_budget_12m": f"${random.randint(700000, 3000000)}",
                "cost_per_compliance_point": f"${random.randint(5000, 20000)}",
                "roi_projection": random.uniform(15, 35)
            }
        }
    
    def _calculate_prediction_confidence(self) -> Dict:
        """Calculate prediction confidence scores"""
        return {
            "overall_confidence": random.uniform(0.7, 0.9),
            "trend_analysis_confidence": random.uniform(0.65, 0.85),
            "risk_prediction_confidence": random.uniform(0.6, 0.8),
            "regulatory_impact_confidence": random.uniform(0.55, 0.75),
            "resource_projection_confidence": random.uniform(0.6, 0.8),
            "methodology_confidence": random.uniform(0.75, 0.9)
        }
    
    def _generate_trend_recommendations(self) -> List[str]:
        """Generate trend-based recommendations"""
        recommendations = [
            "Invest in compliance automation technologies",
            "Develop predictive compliance analytics",
            "Enhance regulatory change management",
            "Strengthen compliance training programs",
            "Implement continuous monitoring solutions",
            "Build compliance Center of Excellence",
            "Establish compliance maturity roadmap",
            "Enhance third-party risk management"
        ]
        
        return random.sample(recommendations, random.randint(4, 6))
    
    def _get_industry_compliance_trends(self) -> Dict:
        """Get industry compliance trends"""
        return {
            "regulatory_evolution": "Increasing complexity and scope",
            "technology_adoption": "Growing automation and AI usage",
            "risk_emphasis": "Shift to proactive risk management",
            "reporting_requirements": "Enhanced transparency demands",
            "penalties_increase": "Rising financial penalties for non-compliance",
            "industry_maturity": "Varying maturity levels across sectors"
        }
    
    def get_compliance_dashboard(self) -> Dict:
        """Generate comprehensive compliance dashboard"""
        try:
            # Compliance overview
            compliance_overview = self._get_compliance_overview()
            
            # Framework status
            framework_status = self._get_framework_status()
            
            # Audit summary
            audit_summary = self._get_audit_summary()
            
            # Risk assessment
            risk_assessment = self._get_risk_assessment()
            
            # Regulatory changes
            regulatory_changes = self._get_regulatory_changes_summary()
            
            # Key performance indicators
            kpis = self._get_compliance_kpis()
            
            # Trends and insights
            trends_and_insights = self._get_trends_and_insights()
            
            # Recommendations
            recommendations = self._get_compliance_recommendations()
            
            return {
                "compliance_overview": compliance_overview,
                "framework_status": framework_status,
                "audit_summary": audit_summary,
                "risk_assessment": risk_assessment,
                "regulatory_changes": regulatory_changes,
                "kpis": kpis,
                "trends_and_insights": trends_and_insights,
                "recommendations": recommendations,
                "executive_summary": self._get_executive_summary()
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance dashboard: {str(e)}")
            raise
    
    def _get_compliance_overview(self) -> Dict:
        """Get compliance overview statistics"""
        total_frameworks = len(self.frameworks)
        compliant_frameworks = len([fw for fw in self.frameworks.values() if fw.compliance_score >= 85])
        
        total_controls = len(self.controls)
        compliant_controls = len([ctrl for ctrl in self.controls.values() if ctrl.status == ComplianceStatus.COMPLIANT])
        
        total_assessments = len(self.assessments)
        recent_assessments = len([assess for assess in self.assessments.values() 
                                if assess.start_date >= datetime.now() - timedelta(days=90)])
        
        return {
            "total_frameworks": total_frameworks,
            "compliant_frameworks": compliant_frameworks,
            "compliance_rate": (compliant_frameworks / total_frameworks * 100) if total_frameworks > 0 else 0,
            "total_controls": total_controls,
            "compliant_controls": compliant_controls,
            "control_compliance_rate": (compliant_controls / total_controls * 100) if total_controls > 0 else 0,
            "total_assessments": total_assessments,
            "recent_assessments": recent_assessments,
            "overall_compliance_score": sum(fw.compliance_score for fw in self.frameworks.values()) / total_frameworks if total_frameworks > 0 else 0,
            "assessment_frequency": f"{recent_assessments} in last 90 days"
        }
    
    def _get_framework_status(self) -> Dict:
        """Get framework status summary"""
        # Analyze compliance score distribution
        high_compliance = len([fw for fw in self.frameworks.values() if fw.compliance_score >= 90])
        medium_compliance = len([fw for fw in self.frameworks.values() if 70 <= fw.compliance_score < 90])
        low_compliance = len([fw for fw in self.frameworks.values() if fw.compliance_score < 70])
        
        # Framework type distribution
        type_distribution = {}
        for fw in self.frameworks.values():
            fw_type = fw.framework_type.value
            type_distribution[fw_type] = type_distribution.get(fw_type, 0) + 1
        
        # Upcoming assessments
        upcoming_assessments = len([fw for fw in self.frameworks.values() 
                                  if fw.next_assessment <= datetime.now() + timedelta(days=30)])
        
        return {
            "compliance_score_distribution": {
                "high_compliance": high_compliance,
                "medium_compliance": medium_compliance,
                "low_compliance": low_compliance
            },
            "framework_type_distribution": type_distribution,
            "upcoming_assessments": upcoming_assessments,
            "overdue_assessments": len([fw for fw in self.frameworks.values() 
                                     if fw.next_assessment < datetime.now()]),
            "last_updated": max([fw.last_updated for fw in self.frameworks.values()]) if self.frameworks else None
        }
    
    def _get_audit_summary(self) -> Dict:
        """Get audit summary"""
        total_audits = len(self.audits)
        completed_audits = len([audit for audit in self.audits.values() if audit.status == AuditStatus.COMPLETED])
        
        # Findings analysis
        total_findings = sum(audit.findings_count for audit in self.audits.values())
        critical_findings = sum(audit.critical_findings for audit in self.audits.values())
        high_findings = sum(audit.high_findings for audit in self.audits.values())
        
        # Recent audits
        recent_audits = [audit for audit in self.audits.values() 
                        if audit.start_date >= datetime.now() - timedelta(days=90)]
        
        return {
            "total_audits": total_audits,
            "completed_audits": completed_audits,
            "completion_rate": (completed_audits / total_audits * 100) if total_audits > 0 else 0,
            "total_findings": total_findings,
            "critical_findings": critical_findings,
            "high_findings": high_findings,
            "average_findings_per_audit": total_findings / total_audits if total_audits > 0 else 0,
            "recent_audits": len(recent_audits),
            "findings_trend": random.choice(["decreasing", "stable", "increasing"])
        }
    
    def _get_risk_assessment(self) -> Dict:
        """Get risk assessment summary"""
        total_risks = len(self.compliance_risks)
        
        # Risk level distribution
        risk_level_distribution = {}
        for risk_level in RiskLevel:
            risk_level_distribution[risk_level.value] = len([risk for risk in self.compliance_risks.values() 
                                                           if risk.likelihood == risk_level or risk.impact == risk_level])
        
        # High-risk items
        high_risks = [risk for risk in self.compliance_risks.values() if risk.risk_score >= 15]
        overdue_mitigations = len([risk for risk in self.compliance_risks 
                                 if risk.due_date and risk.due_date < datetime.now()])
        
        return {
            "total_risks": total_risks,
            "risk_level_distribution": risk_level_distribution,
            "high_risks": len(high_risks),
            "overdue_mitigations": overdue_mitigations,
            "average_risk_score": sum(risk.risk_score for risk in self.compliance_risks.values()) / total_risks if total_risks > 0 else 0,
            "risk_maturity": random.choice(["initial", "managed", "defined", "optimized"]),
            "mitigation_progress": random.uniform(60, 90)
        }
    
    def _get_regulatory_changes_summary(self) -> Dict:
        """Get regulatory changes summary"""
        total_changes = len(self.regulatory_changes)
        pending_changes = len([change for change in self.regulatory_changes.values() if change.status == "pending"])
        
        # Framework impact
        framework_impact = {}
        for change in self.regulatory_changes.values():
            fw_id = change.framework_id
            framework_impact[fw_id] = framework_impact.get(fw_id, 0) + 1
        
        # Upcoming deadlines
        upcoming_deadlines = len([change for change in self.regulatory_changes.values() 
                                if change.deadline and change.deadline <= datetime.now() + timedelta(days=30)])
        
        return {
            "total_changes": total_changes,
            "pending_changes": pending_changes,
            "implemented_changes": total_changes - pending_changes,
            "framework_impact": framework_impact,
            "upcoming_deadlines": upcoming_deadlines,
            "high_impact_changes": len([change for change in self.regulatory_changes.values() 
                                      if change.impact_assessment == "High"]),
            "implementation_progress": random.uniform(70, 95)
        }
    
    def _get_compliance_kpis(self) -> Dict:
        """Get compliance KPIs"""
        # Calculate key performance indicators
        compliance_kpis = {}
        
        for metric in self.compliance_metrics:
            metric_name = metric.metric_name
            compliance_kpis[metric_name] = {
                "current_value": metric.value,
                "target": metric.target,
                "status": metric.status.value,
                "trend": random.choice(["improving", "stable", "declining"])
            }
        
        # Add calculated KPIs
        compliance_kpis.update({
            "mean_time_to_compliance": f"{random.randint(30, 120)} days",
            "compliance_cost_ratio": f"{random.uniform(2, 8)}%",
            "audit_readiness_score": random.uniform(75, 95),
            "regulatory_awareness": random.uniform(80, 98),
            "stakeholder_satisfaction": random.uniform(70, 90)
        })
        
        return compliance_kpis
    
    def _get_trends_and_insights(self) -> Dict:
        """Get compliance trends and insights"""
        return {
            "compliance_trends": {
                "overall_trend": random.choice(["improving", "stable", "declining"]),
                "automation_adoption": random.uniform(30, 70),
                "regulatory_complexity": random.choice(["increasing", "stable", "decreasing"]),
                "technology_integration": random.uniform(40, 80)
            },
            "key_insights": [
                "Compliance automation showing positive ROI",
                "Regulatory changes requiring increased attention",
                "Risk-based approach improving effectiveness",
                "Third-party compliance becoming critical",
                "Data privacy compliance gaining prominence"
            ],
            "emerging_challenges": [
                "Regulatory fragmentation across jurisdictions",
                "Technology complexity increasing compliance burden",
                "Resource constraints affecting compliance programs",
                "Skills gap in compliance professionals",
                "Real-time compliance monitoring requirements"
            ],
            "opportunities": [
                "AI-powered compliance monitoring",
                "Predictive compliance analytics",
                "Integrated GRC platforms",
                "Blockchain for compliance verification",
                "Automated regulatory reporting"
            ]
        }
    
    def _get_compliance_recommendations(self) -> Dict:
        """Get compliance recommendations"""
        return {
            "immediate_actions": [
                "Address critical compliance gaps",
                "Complete overdue assessments",
                "Mitigate high-risk items",
                "Update compliance documentation"
            ],
            "strategic_initiatives": [
                "Implement compliance automation",
                "Develop predictive analytics",
                "Establish compliance Center of Excellence",
                "Enhance regulatory change management"
            ],
            "resource_requirements": {
                "additional_personnel": random.randint(2, 6),
                "technology_investment": f"${random.randint(100000, 500000)}",
                "training_investment": f"${random.randint(50000, 200000)}",
                "consulting_support": f"${random.randint(75000, 300000)}"
            },
            "expected_benefits": [
                "Improved compliance scores",
                "Reduced audit findings",
                "Lower compliance costs",
                "Enhanced regulatory readiness",
                "Better risk management"
            ],
            "success_metrics": [
                "95% compliance score target",
                "50% reduction in audit findings",
                "30% improvement in remediation time",
                "25% reduction in compliance costs",
                "Zero critical regulatory violations"
            ]
        }
    
    def _get_executive_summary(self) -> Dict:
        """Get executive summary"""
        total_frameworks = len(self.frameworks)
        compliant_frameworks = len([fw for fw in self.frameworks.values() if fw.compliance_score >= 85])
        
        return {
            "overall_status": "Good" if compliant_frameworks / total_frameworks >= 0.8 else "Needs Improvement" if compliant_frameworks / total_frameworks >= 0.6 else "Critical",
            "compliance_score": sum(fw.compliance_score for fw in self.frameworks.values()) / total_frameworks if total_frameworks > 0 else 0,
            "key_achievements": [
                "Maintained compliance across major frameworks",
                "Reduced audit findings by 15%",
                "Implemented automated monitoring",
                "Enhanced staff compliance training"
            ],
            "areas_of_concern": [
                "Some frameworks below target compliance scores",
                "Regulatory changes requiring attention",
                "Resource constraints in compliance team",
                "Technology gaps in compliance automation"
            ],
            "investment_priorities": [
                "Compliance automation technology",
                "Staff training and development",
                "Risk assessment improvements",
                "Regulatory change management"
            ],
            "roi_projection": random.uniform(15, 35),
            "next_review_date": (datetime.now() + timedelta(days=90)).isoformat()
        }

# FastAPI Application
app = FastAPI(title="Compliance Monitor", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
compliance_ai = ComplianceAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=compliance_ai.web_components.render_compliance_dashboard())

@app.get("/api/frameworks")
async def get_compliance_frameworks():
    """Get all compliance frameworks"""
    return {"frameworks": list(compliance_ai.frameworks.values())}

@app.get("/api/controls")
async def get_compliance_controls():
    """Get all compliance controls"""
    return {"controls": list(compliance_ai.controls.values())}

@app.get("/api/assessments")
async def get_compliance_assessments():
    """Get all compliance assessments"""
    return {"assessments": list(compliance_ai.assessments.values())}

@app.get("/api/audits")
async def get_compliance_audits():
    """Get all compliance audits"""
    return {"audits": list(compliance_ai.audits.values())}

@app.get("/api/risks")
async def get_compliance_risks():
    """Get all compliance risks"""
    return {"risks": list(compliance_ai.compliance_risks.values())}

@app.get("/api/regulatory-changes")
async def get_regulatory_changes():
    """Get regulatory changes"""
    return {"changes": list(compliance_ai.regulatory_changes.values())}

@app.post("/api/gap-analysis/{framework_id}")
async def analyze_compliance_gap_endpoint(framework_id: str):
    """Analyze compliance gaps"""
    try:
        gap_analysis = await compliance_ai.analyze_compliance_gap(framework_id)
        return gap_analysis
    except Exception as e:
        logger.error(f"Error analyzing compliance gap: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trend-prediction")
async def predict_compliance_trends_endpoint(prediction_request: Dict):
    """Predict compliance trends"""
    try:
        timeframe = prediction_request.get("timeframe", "12_months")
        predictions = compliance_ai.predict_compliance_trends(timeframe)
        return predictions
    except Exception as e:
        logger.error(f"Error predicting compliance trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compliance-dashboard")
async def get_compliance_dashboard():
    """Get compliance dashboard data"""
    try:
        dashboard_data = compliance_ai.get_compliance_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting compliance dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/analyze-framework")
async def analyze_demo_framework():
    """Analyze a random demo framework for testing"""
    framework_ids = list(compliance_ai.frameworks.keys())
    if not framework_ids:
        raise HTTPException(status_code=404, detail="No compliance frameworks available for analysis")
    
    framework_id = random.choice(framework_ids)
    gap_analysis = await compliance_ai.analyze_compliance_gap(framework_id)
    return {"framework_id": framework_id, "analysis": gap_analysis}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Compliance Monitor...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")