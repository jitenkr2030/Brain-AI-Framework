"""
Cybersecurity - Brain AI Framework Example
A comprehensive cybersecurity system that helps organizations monitor threats,
analyze security incidents, and manage cybersecurity operations using Brain AI Framework.
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
import hashlib

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
logger.add("logs/cybersecurity.log", rotation="10 MB", level="INFO")

class ThreatLevel(Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class IncidentStatus(Enum):
    """Incident status enumeration"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

class AttackType(Enum):
    """Attack type enumeration"""
    MALWARE = "malware"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    DDOS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    BRUTE_FORCE = "brute_force"
    SOCIAL_ENGINEERING = "social_engineering"
    INSIDER_THREAT = "insider_threat"
    APT = "apt"

class AssetType(Enum):
    """Asset type enumeration"""
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    DATABASE = "database"
    APPLICATION = "application"
    MOBILE_DEVICE = "mobile_device"
    IOT_DEVICE = "iot_device"
    CLOUD_RESOURCE = "cloud_resource"

class ComplianceFramework(Enum):
    """Compliance framework enumeration"""
    ISO27001 = "iso27001"
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST_CSF = "nist_csf"

@dataclass
class ThreatIntelligence:
    """Threat intelligence data point"""
    threat_id: str
    threat_type: str
    indicators: List[str]
    iocs: List[str]  # Indicators of Compromise
    confidence_score: float
    source: str
    first_seen: datetime
    last_seen: datetime
    attribution: Optional[str]

@dataclass
class SecurityMetric:
    """Security metric data point"""
    metric_name: str
    value: float
    threshold: float
    unit: str
    timestamp: datetime
    status: ThreatLevel

class SecurityIncident(BaseModel):
    """Security incident model"""
    incident_id: str
    title: str
    description: str
    attack_type: AttackType
    threat_level: ThreatLevel
    status: IncidentStatus
    affected_assets: List[str]
    reported_by: str
    assigned_to: Optional[str]
    created_date: datetime
    last_updated: datetime
    severity_score: float
    business_impact: str
    technical_details: Dict[str, Any]
    indicators: List[str]
    mitigation_actions: List[str]

class Vulnerability(BaseModel):
    """Vulnerability model"""
    vuln_id: str
    cve_id: Optional[str]
    title: str
    description: str
    severity: ThreatLevel
    cvss_score: float
    affected_assets: List[str]
    discovery_date: datetime
    patch_available: bool
    patch_deadline: Optional[datetime]
    exploitation_likelihood: float
    business_impact: str
    remediation_priority: int

class SecurityAsset(BaseModel):
    """Security asset model"""
    asset_id: str
    name: str
    asset_type: AssetType
    ip_address: str
    mac_address: Optional[str]
    location: str
    owner: str
    criticality: ThreatLevel
    last_scan: datetime
    security_controls: List[str]
    vulnerabilities: List[str]
    compliance_status: Dict[str, bool]
    patch_level: str

class ComplianceCheck(BaseModel):
    """Compliance check model"""
    check_id: str
    framework: ComplianceFramework
    control_id: str
    control_name: str
    status: bool
    evidence: List[str]
    last_assessment: datetime
    next_assessment: datetime
    findings: List[str]
    remediation_actions: List[str]

class ThreatHunt(BaseModel):
    """Threat hunting session model"""
    hunt_id: str
    name: str
    hypothesis: str
    search_queries: List[str]
    timeframe: str
    results: Dict[str, Any]
    findings: List[str]
    recommendations: List[str]
    created_by: str
    created_date: datetime
    status: str

class CybersecurityAI:
    """Main cybersecurity AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.security_incidents: Dict[str, SecurityIncident] = {}
        self.vulnerabilities: Dict[str, Vulnerability] = {}
        self.security_assets: Dict[str, SecurityAsset] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.threat_hunts: Dict[str, ThreatHunt] = {}
        self.threat_intelligence: Dict[str, ThreatIntelligence] = {}
        self.security_metrics: List[SecurityMetric] = []
        
        # Cybersecurity configuration
        self.security_config = {
            "threat_intelligence_feeds": 5,
            "vulnerability_scan_frequency": "weekly",
            "incident_response_timeout": 3600,  # seconds
            "patch_deadline_days": 30,
            "compliance_check_frequency": "monthly"
        }
        
        # Asset criticality mapping
        self.asset_criticality_map = {
            AssetType.DATABASE: ThreatLevel.CRITICAL,
            AssetType.SERVER: ThreatLevel.HIGH,
            AssetType.APPLICATION: ThreatLevel.HIGH,
            AssetType.WORKSTATION: ThreatLevel.MEDIUM,
            AssetType.NETWORK_DEVICE: ThreatLevel.HIGH,
            AssetType.MOBILE_DEVICE: ThreatLevel.MEDIUM,
            AssetType.IOT_DEVICE: ThreatLevel.MEDIUM,
            AssetType.CLOUD_RESOURCE: ThreatLevel.HIGH
        }
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo security assets
        for i in range(200):
            asset = self.demo_data.generate_security_asset(
                asset_id=f"ASSET_{i+1:04d}",
                asset_type=random.choice(list(AssetType))
            )
            self.security_assets[asset.asset_id] = asset
        
        # Generate demo vulnerabilities
        for i in range(150):
            vuln = self.demo_data.generate_vulnerability(
                vuln_id=f"VULN_{i+1:03d}",
                affected_assets=random.sample(list(self.security_assets.keys()), random.randint(1, 3))
            )
            self.vulnerabilities[vuln.vuln_id] = vuln
        
        # Generate demo security incidents
        for i in range(100):
            incident = self.demo_data.generate_security_incident(
                incident_id=f"INC_{i+1:03d}",
                attack_type=random.choice(list(AttackType)),
                affected_assets=random.sample(list(self.security_assets.keys()), random.randint(1, 5))
            )
            self.security_incidents[incident.incident_id] = incident
        
        # Generate demo compliance checks
        self._generate_compliance_checks()
        
        # Generate threat intelligence
        self._generate_threat_intelligence()
        
        # Generate threat hunts
        self._generate_threat_hunts()
        
        # Generate security metrics
        self._generate_security_metrics()
        
        logger.info(f"Initialized demo data: {len(self.security_assets)} assets, "
                   f"{len(self.vulnerabilities)} vulnerabilities, {len(self.security_incidents)} incidents")
    
    def _generate_compliance_checks(self):
        """Generate compliance checks"""
        frameworks = list(ComplianceFramework)
        control_templates = {
            ComplianceFramework.ISO27001: ["A.5.1", "A.6.1", "A.8.1", "A.9.1", "A.10.1"],
            ComplianceFramework.SOC2: ["CC1.1", "CC2.1", "CC3.1", "CC4.1", "CC5.1"],
            ComplianceFramework.GDPR: ["Article 25", "Article 30", "Article 32", "Article 35", "Article 39"],
            ComplianceFramework.HIPAA: ["164.308", "164.310", "164.312", "164.314", "164.316"],
            ComplianceFramework.PCI_DSS: ["1.1", "2.1", "3.1", "4.1", "5.1"],
            ComplianceFramework.NIST_CSF: ["ID.AM", "PR.AC", "DE.CM", "RS.RP", "RC.IM"]
        }
        
        for framework in frameworks:
            controls = control_templates.get(framework, ["Control_1", "Control_2", "Control_3"])
            
            for control in controls:
                check = ComplianceCheck(
                    check_id=f"COMP_{framework.value}_{control}",
                    framework=framework,
                    control_id=control,
                    control_name=f"{framework.value.title()} {control} Control",
                    status=random.choice([True, True, True, False]),  # 75% pass rate
                    evidence=self._generate_compliance_evidence(),
                    last_assessment=datetime.now() - timedelta(days=random.randint(1, 30)),
                    next_assessment=datetime.now() + timedelta(days=random.randint(30, 90)),
                    findings=self._generate_compliance_findings(),
                    remediation_actions=self._generate_remediation_actions()
                )
                
                self.compliance_checks[check.check_id] = check
    
    def _generate_compliance_evidence(self) -> List[str]:
        """Generate compliance evidence"""
        evidence_templates = [
            "Firewall configuration documentation",
            "Access control matrix",
            "Encryption policy document",
            "Incident response procedures",
            "Employee training records",
            "Vulnerability assessment report",
            "Backup and recovery procedures",
            "Data classification policy",
            "Vendor management procedures",
            "Security awareness training"
        ]
        
        return random.sample(evidence_templates, random.randint(2, 5))
    
    def _generate_compliance_findings(self) -> List[str]:
        """Generate compliance findings"""
        findings_templates = [
            "Documentation needs updating",
            "Policy not consistently enforced",
            "Training completion rate below target",
            "Technical controls require enhancement",
            "Process gaps identified",
            "Evidence collection incomplete",
            "Control testing insufficient",
            "Remediation timeline not met"
        ]
        
        return random.sample(findings_templates, random.randint(0, 3))
    
    def _generate_remediation_actions(self) -> List[str]:
        """Generate remediation actions"""
        actions_templates = [
            "Update security policies",
            "Implement additional controls",
            "Conduct staff training",
            "Enhance monitoring procedures",
            "Update documentation",
            "Increase testing frequency",
            "Improve evidence collection",
            "Review and update procedures"
        ]
        
        return random.sample(actions_templates, random.randint(1, 3))
    
    def _generate_threat_intelligence(self):
        """Generate threat intelligence data"""
        threat_types = [
            "APT29", "Lazarus Group", "Cozy Bear", "Fancy Bear", "APT1",
            "Malware", "Ransomware", "Phishing Campaign", "Data Breach",
            "Supply Chain Attack", "Zero-day Exploit"
        ]
        
        sources = [
            "CISA", "NIST", "AlienVault", "VirusTotal", "ThreatConnect",
            "Recorded Future", "FireEye", "CrowdStrike", "Internal Research"
        ]
        
        for i in range(50):
            threat_type = random.choice(threat_types)
            
            # Generate IOCs
            iocs = self._generate_iocs()
            
            threat = ThreatIntelligence(
                threat_id=f"TI_{i+1:03d}",
                threat_type=threat_type,
                indicators=self._generate_threat_indicators(threat_type),
                iocs=iocs,
                confidence_score=random.uniform(0.6, 0.95),
                source=random.choice(sources),
                first_seen=datetime.now() - timedelta(days=random.randint(1, 90)),
                last_seen=datetime.now() - timedelta(days=random.randint(0, 7)),
                attribution=self._generate_threat_attribution(threat_type)
            )
            
            self.threat_intelligence[threat.threat_id] = threat
    
    def _generate_iocs(self) -> List[str]:
        """Generate indicators of compromise"""
        ioc_types = [
            "IP addresses", "Domain names", "File hashes", "URLs",
            "Registry keys", "Mutex names", "Email addresses", "File paths"
        ]
        
        sample_iocs = [
            "192.168.1.100", "malicious-domain.com", "a1b2c3d4e5f6", "http://evil.com/payload",
            "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "Mutex_Malware", "admin@evil.com",
            "C:\\Windows\\System32\\malware.dll"
        ]
        
        return random.sample(sample_iocs, random.randint(2, 5))
    
    def _generate_threat_indicators(self, threat_type: str) -> List[str]:
        """Generate threat indicators"""
        indicators = [
            "Suspicious network traffic",
            "Unusual process behavior",
            "File modifications",
            "Registry changes",
            "Network connections",
            "Privilege escalation",
            "Data exfiltration attempts",
            "Lateral movement indicators"
        ]
        
        return random.sample(indicators, random.randint(3, 6))
    
    def _generate_threat_attribution(self, threat_type: str) -> Optional[str]:
        """Generate threat attribution"""
        if random.random() < 0.4:  # 40% chance of attribution
            attributions = [
                "Nation-state actor",
                "Cybercriminal group",
                "Hacktivist organization",
                "Insider threat",
                "Unknown actor"
            ]
            return random.choice(attributions)
        return None
    
    def _generate_threat_hunts(self):
        """Generate threat hunting sessions"""
        hunt_templates = [
            {
                "name": "Suspicious Network Traffic Hunt",
                "hypothesis": "Unauthorized network connections detected",
                "queries": ["source_ip", "destination_ip", "port", "protocol", "bytes_transferred"],
                "timeframe": "24_hours"
            },
            {
                "name": "Malware Persistence Hunt",
                "hypothesis": "Malware attempting to establish persistence",
                "queries": ["registry_keys", "startup_programs", "services", "scheduled_tasks"],
                "timeframe": "7_days"
            },
            {
                "name": "Data Exfiltration Hunt",
                "hypothesis": "Sensitive data being exfiltrated",
                "queries": ["large_file_transfers", "unusual_destinations", "encrypted_transfers"],
                "timeframe": "30_days"
            },
            {
                "name": "Privilege Escalation Hunt",
                "hypothesis": "Unauthorized privilege escalation attempts",
                "queries": ["user_account_changes", "group_membership", "privilege_assignments"],
                "timeframe": "24_hours"
            },
            {
                "name": "Insider Threat Hunt",
                "hypothesis": "Insider threat activity detected",
                "queries": ["user_behavior", "access_patterns", "data_access", "time_anomalies"],
                "timeframe": "7_days"
            }
        ]
        
        for i, template in enumerate(hunt_templates):
            hunt = ThreatHunt(
                hunt_id=f"HUNT_{i+1:03d}",
                name=template["name"],
                hypothesis=template["hypothesis"],
                search_queries=template["queries"],
                timeframe=template["timeframe"],
                results=self._generate_hunt_results(),
                findings=self._generate_hunt_findings(),
                recommendations=self._generate_hunt_recommendations(),
                created_by="Security Analyst",
                created_date=datetime.now() - timedelta(days=random.randint(1, 14)),
                status=random.choice(["completed", "in_progress", "planned"])
            )
            
            self.threat_hunts[hunt.hunt_id] = hunt
    
    def _generate_hunt_results(self) -> Dict[str, Any]:
        """Generate threat hunt results"""
        return {
            "total_events": random.randint(100, 10000),
            "suspicious_events": random.randint(5, 100),
            "confirmed_threats": random.randint(0, 10),
            "false_positives": random.randint(10, 50),
            "confidence_score": random.uniform(0.6, 0.9),
            "execution_time": f"{random.randint(30, 300)} seconds",
            "data_sources": ["network_logs", "endpoint_logs", "authentication_logs", "dns_logs"]
        }
    
    def _generate_hunt_findings(self) -> List[str]:
        """Generate threat hunt findings"""
        findings = [
            "Suspicious outbound connections identified",
            "Unusual file access patterns detected",
            "Potential malware behavior observed",
            "Unauthorized access attempts found",
            "Data exfiltration indicators present",
            "Privilege escalation attempts detected",
            "Lateral movement indicators identified",
            "Anomalous user behavior patterns"
        ]
        
        return random.sample(findings, random.randint(2, 5))
    
    def _generate_hunt_recommendations(self) -> List[str]:
        """Generate threat hunt recommendations"""
        recommendations = [
            "Implement network segmentation",
            "Enhance monitoring capabilities",
            "Update security policies",
            "Conduct additional hunting",
            "Deploy additional controls",
            "Review access permissions",
            "Update threat intelligence",
            "Improve incident response"
        ]
        
        return random.sample(recommendations, random.randint(2, 4))
    
    def _generate_security_metrics(self):
        """Generate security metrics"""
        metric_names = [
            "threats_detected", "incidents_resolved", "vulnerabilities_fixed",
            "compliance_score", "false_positive_rate", "mean_time_to_detect",
            "mean_time_to_respond", "patch_compliance", "security_awareness_score"
        ]
        
        for metric_name in metric_names:
            metric = SecurityMetric(
                metric_name=metric_name,
                value=random.uniform(0, 100),
                threshold=random.uniform(70, 90),
                unit="percentage" if "rate" in metric_name or "score" in metric_name else "count",
                timestamp=datetime.now() - timedelta(hours=random.randint(0, 24)),
                status=random.choice(list(ThreatLevel))
            )
            
            self.security_metrics.append(metric)
    
    async def analyze_security_incident(self, incident_id: str) -> Dict:
        """Analyze security incident using Brain AI"""
        try:
            incident = self.security_incidents.get(incident_id)
            if not incident:
                raise ValueError(f"Incident {incident_id} not found")
            
            # Prepare incident analysis context
            analysis_context = {
                "incident_info": incident.dict(),
                "affected_assets": [self.security_assets.get(asset_id).dict() for asset_id in incident.affected_assets if asset_id in self.security_assets],
                "threat_intelligence": [ti.__dict__ for ti in self.threat_intelligence.values()],
                "historical_incidents": [inc.dict() for inc in list(self.security_incidents.values())[-50:]],
                "vulnerability_data": [vuln.dict() for vuln in self.vulnerabilities.values()],
                "compliance_status": self._get_compliance_status_for_assets(incident.affected_assets)
            }
            
            # Use Brain AI to analyze the incident
            ai_analysis = await self.brain_ai.process_security_incident_analysis(analysis_context)
            
            # Generate analysis results
            analysis_results = {
                "incident_id": incident_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "threat_assessment": self._assess_threat_level(incident),
                "attack_vector_analysis": self._analyze_attack_vector(incident),
                "impact_assessment": self._assess_business_impact(incident),
                "recommended_actions": self._generate_recommended_actions(incident),
                "related_threats": self._identify_related_threats(incident),
                "remediation_plan": self._generate_remediation_plan(incident),
                "lessons_learned": self._generate_lessons_learned(incident),
                "ai_confidence": random.uniform(0.75, 0.95)
            }
            
            # Update incident with analysis results
            incident.technical_details["ai_analysis"] = analysis_results
            incident.last_updated = datetime.now()
            
            logger.info(f"Analyzed security incident {incident_id}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing security incident: {str(e)}")
            raise
    
    def _assess_threat_level(self, incident: SecurityIncident) -> Dict:
        """Assess threat level for incident"""
        # Analyze factors affecting threat level
        factors = {
            "attack_type_severity": self._get_attack_type_severity(incident.attack_type),
            "affected_asset_criticality": self._get_max_asset_criticality(incident.affected_assets),
            "business_impact": self._get_business_impact_score(incident.business_impact),
            "compromise_scope": len(incident.affected_assets) / 10.0,  # Normalize by max assets
            "data_sensitivity": random.uniform(0.3, 0.9)
        }
        
        # Calculate overall threat score
        threat_score = sum(factors.values()) / len(factors)
        
        # Determine threat level
        if threat_score >= 0.8:
            threat_level = ThreatLevel.EMERGENCY
        elif threat_score >= 0.6:
            threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.4:
            threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.2:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW
        
        return {
            "threat_score": threat_score,
            "threat_level": threat_level.value,
            "assessment_factors": factors,
            "confidence": random.uniform(0.7, 0.95)
        }
    
    def _get_attack_type_severity(self, attack_type: AttackType) -> float:
        """Get severity score for attack type"""
        severity_map = {
            AttackType.RANSOMWARE: 0.9,
            AttackType.APT: 0.85,
            AttackType.MALWARE: 0.7,
            AttackType.PHISHING: 0.6,
            AttackType.DDOS: 0.5,
            AttackType.SQL_INJECTION: 0.6,
            AttackType.XSS: 0.4,
            AttackType.BRUTE_FORCE: 0.5,
            AttackType.SOCIAL_ENGINEERING: 0.6,
            AttackType.INSIDER_THREAT: 0.8
        }
        
        return severity_map.get(attack_type, 0.5)
    
    def _get_max_asset_criticality(self, asset_ids: List[str]) -> float:
        """Get maximum asset criticality score"""
        criticality_scores = {
            ThreatLevel.CRITICAL: 1.0,
            ThreatLevel.HIGH: 0.8,
            ThreatLevel.MEDIUM: 0.6,
            ThreatLevel.LOW: 0.4
        }
        
        max_criticality = ThreatLevel.LOW
        for asset_id in asset_ids:
            if asset_id in self.security_assets:
                asset = self.security_assets[asset_id]
                if asset.criticality.value > max_criticality.value:
                    max_criticality = asset.criticality
        
        return criticality_scores[max_criticality]
    
    def _get_business_impact_score(self, business_impact: str) -> float:
        """Get business impact score"""
        impact_map = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4,
            "minimal": 0.2
        }
        
        return impact_map.get(business_impact.lower(), 0.5)
    
    def _analyze_attack_vector(self, incident: SecurityIncident) -> Dict:
        """Analyze attack vector"""
        return {
            "primary_vector": self._determine_primary_vector(incident),
            "attack_chain": self._map_attack_chain(incident),
            "entry_points": self._identify_entry_points(incident),
            "privilege_escalation": self._assess_privilege_escalation(incident),
            "persistence_mechanisms": self._identify_persistence_mechanisms(incident),
            "lateral_movement": self._assess_lateral_movement(incident),
            "confidence": random.uniform(0.6, 0.9)
        }
    
    def _determine_primary_vector(self, incident: SecurityIncident) -> str:
        """Determine primary attack vector"""
        vector_mapping = {
            AttackType.PHISHING: "Email",
            AttackType.MALWARE: "File Download",
            AttackType.RANSOMWARE: "Exploit/Download",
            AttackType.SQL_INJECTION: "Web Application",
            AttackType.BRUTE_FORCE: "Authentication",
            AttackType.SOCIAL_ENGINEERING: "Human Interaction"
        }
        
        return vector_mapping.get(incident.attack_type, "Unknown")
    
    def _map_attack_chain(self, incident: SecurityIncident) -> List[str]:
        """Map attack chain steps"""
        chain_steps = [
            "Initial Access",
            "Execution",
            "Persistence",
            "Privilege Escalation",
            "Defense Evasion",
            "Credential Access",
            "Discovery",
            "Lateral Movement",
            "Collection",
            "Command and Control",
            "Exfiltration",
            "Impact"
        ]
        
        # Return relevant steps based on attack type
        if incident.attack_type == AttackType.RANSOMWARE:
            return chain_steps[:9] + ["Impact"]
        elif incident.attack_type == AttackType.PHISHING:
            return ["Initial Access", "Execution", "Persistence", "Collection", "Exfiltration"]
        else:
            return chain_steps[:6]
    
    def _identify_entry_points(self, incident: SecurityIncident) -> List[str]:
        """Identify entry points"""
        entry_points = [
            "Email attachment",
            "Malicious website",
            "Remote desktop",
            "VPN connection",
            "USB device",
            "Software vulnerability",
            "Misconfigured service",
            "Social engineering"
        ]
        
        return random.sample(entry_points, random.randint(2, 4))
    
    def _assess_privilege_escalation(self, incident: SecurityIncident) -> Dict:
        """Assess privilege escalation"""
        return {
            "attempted": random.choice([True, True, False]),
            "successful": random.choice([True, False]),
            "method": random.choice(["Exploit", "Token theft", "Password dump", "Misconfiguration"]),
            "evidence": ["Process injection", "Registry modification", "Service exploitation"],
            "risk_level": random.choice(["High", "Medium", "Low"])
        }
    
    def _identify_persistence_mechanisms(self, incident: SecurityIncident) -> List[str]:
        """Identify persistence mechanisms"""
        mechanisms = [
            "Registry run keys",
            "Scheduled tasks",
            "Startup folders",
            "Services",
            "WMI event subscriptions",
            "DLL search order hijacking",
            "Browser extensions",
            "Kernel drivers"
        ]
        
        return random.sample(mechanisms, random.randint(1, 3))
    
    def _assess_lateral_movement(self, incident: SecurityIncident) -> Dict:
        """Assess lateral movement"""
        return {
            "indicators_present": random.choice([True, False]),
            "scope": random.choice(["Single system", "Department", "Network segment", "Enterprise"]),
            "techniques": ["SMB/WMI", "RDP", "PowerShell", "Remote services"],
            "evidence": ["Network connections", "Authentication logs", "Process creation"],
            "risk": random.choice(["High", "Medium", "Low"])
        }
    
    def _assess_business_impact(self, incident: SecurityIncident) -> Dict:
        """Assess business impact"""
        return {
            "financial_impact": random.choice(["$10K-$50K", "$50K-$100K", "$100K-$500K", "$500K+"]),
            "operational_impact": random.choice(["None", "Minimal", "Moderate", "Severe"]),
            "reputational_impact": random.choice(["None", "Minor", "Significant", "Severe"]),
            "regulatory_impact": random.choice(["None", "Reporting required", "Investigation required"]),
            "customer_impact": random.choice(["None", "Limited", "Significant", "Severe"]),
            "recovery_time": f"{random.randint(1, 72)} hours",
            "mitigation_cost": f"${random.randint(5000, 50000)}"
        }
    
    def _generate_recommended_actions(self, incident: SecurityIncident) -> List[str]:
        """Generate recommended actions"""
        base_actions = [
            "Isolate affected systems immediately",
            "Preserve evidence and forensic data",
            "Notify stakeholders and leadership",
            "Implement additional monitoring",
            "Conduct comprehensive security review"
        ]
        
        # Add specific actions based on attack type
        if incident.attack_type == AttackType.RANSOMWARE:
            base_actions.extend([
                "Do not pay ransom",
                "Restore from clean backups",
                "Strengthen backup procedures",
                "Implement network segmentation"
            ])
        elif incident.attack_type == AttackType.PHISHING:
            base_actions.extend([
                "Reset compromised credentials",
                "Implement email security controls",
                "Conduct security awareness training",
                "Review email gateway configurations"
            ])
        
        return base_actions[:6]  # Limit to 6 actions
    
    def _identify_related_threats(self, incident: SecurityIncident) -> List[Dict]:
        """Identify related threats"""
        related_threats = []
        
        # Find similar incidents
        similar_incidents = [inc for inc in self.security_incidents.values() 
                           if inc.attack_type == incident.attack_type and inc.incident_id != incident.incident_id]
        
        for related in similar_incidents[:3]:  # Limit to 3 related incidents
            related_threats.append({
                "incident_id": related.incident_id,
                "similarity_score": random.uniform(0.6, 0.9),
                "common_indicators": random.sample(incident.indicators, random.randint(1, 3)),
                "relationship": random.choice(["Same attack pattern", "Same actor", "Same timeframe", "Same vector"])
            })
        
        return related_threats
    
    def _generate_remediation_plan(self, incident: SecurityIncident) -> Dict:
        """Generate remediation plan"""
        return {
            "immediate_actions": [
                "Contain the incident",
                "Preserve evidence",
                "Restore services",
                "Monitor for recurrence"
            ],
            "short_term_actions": [
                "Conduct root cause analysis",
                "Implement additional controls",
                "Update security policies",
                "Staff training and awareness"
            ],
            "long_term_actions": [
                "Architecture improvements",
                "Process enhancements",
                "Technology upgrades",
                "Continuous monitoring"
            ],
            "timeline": {
                "immediate": "0-24 hours",
                "short_term": "1-30 days",
                "long_term": "1-6 months"
            },
            "resources_required": {
                "personnel": random.randint(2, 10),
                "budget": f"${random.randint(10000, 100000)}",
                "technology": ["SIEM", "EDR", "Network monitoring"]
            }
        }
    
    def _generate_lessons_learned(self, incident: SecurityIncident) -> List[str]:
        """Generate lessons learned"""
        lessons = [
            "Enhanced monitoring capabilities needed",
            "Incident response procedures require updates",
            "Staff security awareness training necessary",
            "Additional security controls recommended",
            "Backup and recovery processes need improvement"
        ]
        
        # Add specific lessons based on attack type
        if incident.attack_type == AttackType.PHISHING:
            lessons.append("Email security controls need enhancement")
        elif incident.attack_type == AttackType.RANSOMWARE:
            lessons.append("Backup strategy and testing procedures require review")
        
        return random.sample(lessons, random.randint(3, 5))
    
    def _get_compliance_status_for_assets(self, asset_ids: List[str]) -> Dict:
        """Get compliance status for affected assets"""
        compliance_status = {}
        
        for asset_id in asset_ids:
            if asset_id in self.security_assets:
                asset = self.security_assets[asset_id]
                compliance_status[asset_id] = asset.compliance_status
        
        return compliance_status
    
    def predict_security_threats(self, timeframe: str = "30_days") -> Dict:
        """Predict security threats using AI analysis"""
        try:
            # Prepare threat prediction context
            prediction_context = {
                "historical_incidents": [inc.dict() for inc in list(self.security_incidents.values())[-100:]],
                "threat_intelligence": [ti.__dict__ for ti in self.threat_intelligence.values()],
                "vulnerability_data": [vuln.dict() for vuln in self.vulnerabilities.values()],
                "security_metrics": [metric.__dict__ for metric in self.security_metrics[-50:]],
                "asset_information": {aid: asset.dict() for aid, asset in self.security_assets.items()},
                "timeframe": timeframe
            }
            
            # Generate threat predictions
            predictions = {
                "prediction_timestamp": datetime.now().isoformat(),
                "timeframe": timeframe,
                "threat_predictions": self._generate_threat_predictions(),
                "vulnerability_predictions": self._generate_vulnerability_predictions(),
                "attack_predictions": self._generate_attack_predictions(),
                "compliance_predictions": self._generate_compliance_predictions(),
                "confidence_scores": self._calculate_prediction_confidence(),
                "recommendations": self._generate_threat_recommendations()
            }
            
            logger.info(f"Generated threat predictions for {timeframe}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting security threats: {str(e)}")
            raise
    
    def _generate_threat_predictions(self) -> List[Dict]:
        """Generate threat predictions"""
        threat_types = ["Ransomware", "Phishing", "APT", "Malware", "Insider Threat"]
        predictions = []
        
        for threat_type in threat_types:
            prediction = {
                "threat_type": threat_type,
                "probability": random.uniform(0.1, 0.7),
                "expected_timeline": f"{random.randint(1, 30)} days",
                "risk_level": random.choice(["Low", "Medium", "High"]),
                "indicators": self._generate_threat_indicators(threat_type),
                "mitigation_priority": random.randint(1, 5),
                "confidence": random.uniform(0.6, 0.9)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _generate_vulnerability_predictions(self) -> List[Dict]:
        """Generate vulnerability predictions"""
        predictions = []
        
        # Get high-severity vulnerabilities
        high_severity_vulns = [vuln for vuln in self.vulnerabilities.values() 
                              if vuln.severity in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]
        
        for vuln in random.sample(high_severity_vulns, min(5, len(high_severity_vulns))):
            prediction = {
                "vulnerability_id": vuln.vuln_id,
                "exploitation_probability": random.uniform(0.3, 0.8),
                "predicted_attack_timeline": f"{random.randint(1, 14)} days",
                "business_impact": vuln.business_impact,
                "patch_urgency": random.choice(["Immediate", "High", "Medium"]),
                "affected_assets": len(vuln.affected_assets),
                "confidence": random.uniform(0.7, 0.95)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _generate_attack_predictions(self) -> List[Dict]:
        """Generate attack predictions"""
        predictions = []
        
        # Analyze attack patterns
        attack_patterns = self._analyze_attack_patterns()
        
        for pattern in attack_patterns:
            prediction = {
                "attack_pattern": pattern["name"],
                "frequency_prediction": random.uniform(1, 10),
                "success_probability": random.uniform(0.2, 0.6),
                "target_assets": pattern["target_types"],
                "seasonal_factors": random.choice(["Low", "Medium", "High"]),
                "geographic_factors": random.choice(["Local", "Regional", "Global"]),
                "confidence": random.uniform(0.6, 0.85)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _analyze_attack_patterns(self) -> List[Dict]:
        """Analyze attack patterns from historical data"""
        patterns = [
            {"name": "Business Email Compromise", "target_types": ["Email", "Financial"]},
            {"name": "Supply Chain Attack", "target_types": ["Software", "Hardware"]},
            {"name": "Cloud Credential Theft", "target_types": ["Cloud Services", "Applications"]},
            {"name": "IoT Botnet Formation", "target_types": ["IoT Devices", "Network"]},
            {"name": "Data Exfiltration", "target_types": ["Databases", "File Servers"]}
        ]
        
        return patterns
    
    def _generate_compliance_predictions(self) -> List[Dict]:
        """Generate compliance predictions"""
        predictions = []
        
        # Group compliance checks by framework
        framework_checks = {}
        for check in self.compliance_checks.values():
            framework = check.framework.value
            if framework not in framework_checks:
                framework_checks[framework] = []
            framework_checks[framework].append(check)
        
        for framework, checks in framework_checks.items():
            failed_checks = [check for check in checks if not check.status]
            
            prediction = {
                "framework": framework,
                "compliance_score_prediction": random.uniform(0.7, 0.95),
                "high_risk_areas": len(failed_checks),
                "predicted_findings": random.randint(2, 8),
                "audit_readiness": random.choice(["High", "Medium", "Low"]),
                "remediation_urgency": random.choice(["High", "Medium", "Low"]),
                "confidence": random.uniform(0.6, 0.9)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _calculate_prediction_confidence(self) -> Dict:
        """Calculate prediction confidence scores"""
        return {
            "overall_confidence": random.uniform(0.7, 0.9),
            "threat_intelligence_confidence": random.uniform(0.6, 0.85),
            "historical_data_confidence": random.uniform(0.7, 0.95),
            "external_factor_confidence": random.uniform(0.5, 0.8),
            "methodology_confidence": random.uniform(0.8, 0.95)
        }
    
    def _generate_threat_recommendations(self) -> List[str]:
        """Generate threat-based recommendations"""
        recommendations = [
            "Enhance threat intelligence monitoring",
            "Implement proactive threat hunting",
            "Strengthen vulnerability management",
            "Improve incident response capabilities",
            "Deploy additional security controls",
            "Conduct security awareness training",
            "Review and update security policies",
            "Implement zero-trust architecture"
        ]
        
        return random.sample(recommendations, random.randint(4, 6))
    
    def get_cybersecurity_dashboard(self) -> Dict:
        """Generate comprehensive cybersecurity dashboard"""
        try:
            # Security overview
            security_overview = self._get_security_overview()
            
            # Threat landscape
            threat_landscape = self._get_threat_landscape()
            
            # Incident analysis
            incident_analysis = self._get_incident_analysis()
            
            # Vulnerability assessment
            vulnerability_assessment = self._get_vulnerability_assessment()
            
            # Compliance status
            compliance_status = self._get_compliance_status()
            
            # Asset security
            asset_security = self._get_asset_security()
            
            # Security metrics
            security_metrics = self._get_security_metrics()
            
            # Threat intelligence
            threat_intel = self._get_threat_intelligence_summary()
            
            return {
                "security_overview": security_overview,
                "threat_landscape": threat_landscape,
                "incident_analysis": incident_analysis,
                "vulnerability_assessment": vulnerability_assessment,
                "compliance_status": compliance_status,
                "asset_security": asset_security,
                "security_metrics": security_metrics,
                "threat_intelligence": threat_intel,
                "predictive_insights": self._get_predictive_insights(),
                "recommendations": self._get_security_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating cybersecurity dashboard: {str(e)}")
            raise
    
    def _get_security_overview(self) -> Dict:
        """Get security overview statistics"""
        total_incidents = len(self.security_incidents)
        active_incidents = len([inc for inc in self.security_incidents.values() 
                               if inc.status in [IncidentStatus.NEW, IncidentStatus.INVESTIGATING]])
        resolved_incidents = len([inc for inc in self.security_incidents.values() 
                                if inc.status == IncidentStatus.RESOLVED])
        
        # Calculate incident trends
        recent_incidents = [inc for inc in self.security_incidents.values() 
                           if inc.created_date >= datetime.now() - timedelta(days=30)]
        
        return {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "resolved_incidents": resolved_incidents,
            "incident_trend_30_days": len(recent_incidents),
            "average_resolution_time": f"{random.randint(2, 48)} hours",
            "security_posture_score": random.uniform(70, 95),
            "threat_level": random.choice(["Low", "Medium", "High"]),
            "last_security_scan": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        }
    
    def _get_threat_landscape(self) -> Dict:
        """Get threat landscape analysis"""
        # Analyze threat types
        threat_type_counts = {}
        for incident in self.security_incidents.values():
            threat_type = incident.attack_type.value
            threat_type_counts[threat_type] = threat_type_counts.get(threat_type, 0) + 1
        
        # Calculate threat intelligence metrics
        active_threats = len([ti for ti in self.threat_intelligence.values() 
                             if (datetime.now() - ti.last_seen).days <= 7])
        
        return {
            "threat_distribution": threat_type_counts,
            "active_threat_intelligence": active_threats,
            "high_priority_threats": len([ti for ti in self.threat_intelligence.values() 
                                        if ti.confidence_score > 0.8]),
            "emerging_threats": random.randint(2, 8),
            "threat_actor_activity": random.choice(["Low", "Medium", "High"]),
            "geographic_threat_distribution": {
                "domestic": random.randint(30, 50),
                "international": random.randint(40, 60),
                "unknown": random.randint(10, 20)
            }
        }
    
    def _get_incident_analysis(self) -> Dict:
        """Get incident analysis summary"""
        # Analyze incident status distribution
        status_counts = {}
        severity_counts = {}
        
        for incident in self.security_incidents.values():
            status = incident.status.value
            severity = incident.threat_level.value
            status_counts[status] = status_counts.get(status, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate average metrics
        avg_severity = sum(inc.severity_score for inc in self.security_incidents.values()) / len(self.security_incidents)
        
        return {
            "status_distribution": status_counts,
            "severity_distribution": severity_counts,
            "average_severity_score": avg_severity,
            "critical_incidents": len([inc for inc in self.security_incidents.values() 
                                     if inc.threat_level == ThreatLevel.CRITICAL]),
            "resolution_rate": (len([inc for inc in self.security_incidents.values() 
                                   if inc.status == IncidentStatus.RESOLVED]) / len(self.security_incidents)) * 100,
            "recurring_incidents": random.randint(5, 15),
            "false_positive_rate": random.uniform(5, 20)
        }
    
    def _get_vulnerability_assessment(self) -> Dict:
        """Get vulnerability assessment summary"""
        # Analyze vulnerability severity distribution
        severity_counts = {}
        for vuln in self.vulnerabilities.values():
            severity = vuln.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate patch status
        patch_available = len([vuln for vuln in self.vulnerabilities.values() if vuln.patch_available])
        overdue_patches = len([vuln for vuln in self.vulnerabilities.values() 
                              if vuln.patch_deadline and vuln.patch_deadline < datetime.now()])
        
        return {
            "total_vulnerabilities": len(self.vulnerabilities),
            "severity_distribution": severity_counts,
            "patch_available": patch_available,
            "overdue_patches": overdue_patches,
            "patch_compliance_rate": ((len(self.vulnerabilities) - overdue_patches) / len(self.vulnerabilities)) * 100,
            "exploitation_risk": random.choice(["Low", "Medium", "High"]),
            "remediation_progress": random.uniform(60, 90),
            "risk_score": random.uniform(30, 80)
        }
    
    def _get_compliance_status(self) -> Dict:
        """Get compliance status summary"""
        # Analyze compliance by framework
        framework_compliance = {}
        for framework in ComplianceFramework:
            framework_checks = [check for check in self.compliance_checks.values() if check.framework == framework]
            if framework_checks:
                pass_rate = (len([check for check in framework_checks if check.status]) / len(framework_checks)) * 100
                framework_compliance[framework.value] = {
                    "pass_rate": pass_rate,
                    "total_checks": len(framework_checks),
                    "passed_checks": len([check for check in framework_checks if check.status])
                }
        
        return {
            "overall_compliance_score": random.uniform(75, 95),
            "framework_compliance": framework_compliance,
            "high_risk_findings": len([check for check in self.compliance_checks.values() 
                                     if not check.status and len(check.findings) > 0]),
            "remediation_progress": random.uniform(60, 85),
            "audit_readiness": random.choice(["Ready", "Nearly Ready", "Needs Work"]),
            "next_audit_date": (datetime.now() + timedelta(days=random.randint(30, 180))).isoformat()
        }
    
    def _get_asset_security(self) -> Dict:
        """Get asset security summary"""
        # Analyze asset distribution
        asset_type_counts = {}
        criticality_counts = {}
        
        for asset in self.security_assets.values():
            asset_type = asset.asset_type.value
            criticality = asset.criticality.value
            asset_type_counts[asset_type] = asset_type_counts.get(asset_type, 0) + 1
            criticality_counts[criticality] = criticality_counts.get(criticality, 0) + 1
        
        # Calculate security posture
        secure_assets = len([asset for asset in self.security_assets.values() 
                           if len(asset.vulnerabilities) == 0])
        security_coverage = (secure_assets / len(self.security_assets)) * 100
        
        return {
            "total_assets": len(self.security_assets),
            "asset_distribution": asset_type_counts,
            "criticality_distribution": criticality_counts,
            "security_coverage": security_coverage,
            "unmanaged_assets": random.randint(5, 20),
            "end_of_life_assets": random.randint(10, 30),
            "shadow_it_percentage": random.uniform(5, 15),
            "asset_inventory_accuracy": random.uniform(85, 98)
        }
    
    def _get_security_metrics(self) -> Dict:
        """Get security metrics summary"""
        # Calculate key security metrics
        metrics_summary = {}
        
        for metric in self.security_metrics:
            metric_name = metric.metric_name
            if metric_name not in metrics_summary:
                metrics_summary[metric_name] = {
                    "current_value": metric.value,
                    "threshold": metric.threshold,
                    "status": metric.status.value,
                    "trend": random.choice(["improving", "stable", "declining"])
                }
        
        return {
            "metrics_summary": metrics_summary,
            "performance_indicators": {
                "mean_time_to_detect": f"{random.randint(15, 120)} minutes",
                "mean_time_to_respond": f"{random.randint(30, 240)} minutes",
                "mean_time_to_recover": f"{random.randint(2, 48)} hours",
                "false_positive_rate": f"{random.uniform(5, 20)}%",
                "security_awareness_score": f"{random.uniform(70, 95)}%"
            },
            "trending_metrics": random.choice(["improving", "stable", "declining"])
        }
    
    def _get_threat_intelligence_summary(self) -> Dict:
        """Get threat intelligence summary"""
        # Analyze threat intelligence sources
        source_counts = {}
        confidence_distribution = {"high": 0, "medium": 0, "low": 0}
        
        for ti in self.threat_intelligence.values():
            source = ti.source
            source_counts[source] = source_counts.get(source, 0) + 1
            
            if ti.confidence_score >= 0.8:
                confidence_distribution["high"] += 1
            elif ti.confidence_score >= 0.6:
                confidence_distribution["medium"] += 1
            else:
                confidence_distribution["low"] += 1
        
        return {
            "total_intelligence_feeds": len(self.threat_intelligence),
            "source_distribution": source_counts,
            "confidence_distribution": confidence_distribution,
            "recent_activity": len([ti for ti in self.threat_intelligence.values() 
                                  if (datetime.now() - ti.last_seen).days <= 7]),
            "attribution_confidence": random.choice(["Low", "Medium", "High"]),
            "threat_actor_tracking": random.randint(5, 20),
            "ioc_coverage": random.uniform(70, 95)
        }
    
    def _get_predictive_insights(self) -> Dict:
        """Get predictive security insights"""
        return {
            "threat_predictions": {
                "high_probability_threats": random.randint(2, 6),
                "predicted_attack_timeline": f"{random.randint(1, 30)} days",
                "confidence_level": random.uniform(0.6, 0.85)
            },
            "vulnerability_predictions": {
                "critical_vulnerabilities_expected": random.randint(1, 5),
                "patch_urgency": random.choice(["High", "Medium", "Low"]),
                "exploitation_likelihood": random.choice(["High", "Medium", "Low"])
            },
            "compliance_predictions": {
                "audit_readiness": random.choice(["Ready", "Nearly Ready", "Needs Work"]),
                "remediation_urgency": random.choice(["High", "Medium", "Low"])
            },
            "risk_trends": {
                "overall_risk_trend": random.choice(["increasing", "stable", "decreasing"]),
                "emerging_risks": random.randint(2, 8),
                "mitigation_effectiveness": random.uniform(0.7, 0.9)
            }
        }
    
    def _get_security_recommendations(self) -> Dict:
        """Get security recommendations"""
        return {
            "priority_actions": [
                "Address critical vulnerabilities within 24 hours",
                "Enhance monitoring for high-risk assets",
                "Update incident response procedures",
                "Conduct security awareness training"
            ],
            "strategic_initiatives": [
                "Implement zero-trust architecture",
                "Deploy advanced threat protection",
                "Enhance vulnerability management",
                "Strengthen supply chain security"
            ],
            "resource_requirements": {
                "personnel": random.randint(2, 8),
                "budget": f"${random.randint(50000, 500000)}",
                "timeline": f"{random.randint(3, 18)} months"
            },
            "expected_benefits": [
                "Reduced incident response time",
                "Improved threat detection",
                "Enhanced compliance posture",
                "Better risk management"
            ]
        }

# FastAPI Application
app = FastAPI(title="Cybersecurity", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
cybersecurity_ai = CybersecurityAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=cybersecurity_ai.web_components.render_cybersecurity_dashboard())

@app.get("/api/security-incidents")
async def get_security_incidents():
    """Get all security incidents"""
    return {"incidents": list(cybersecurity_ai.security_incidents.values())}

@app.get("/api/vulnerabilities")
async def get_vulnerabilities():
    """Get all vulnerabilities"""
    return {"vulnerabilities": list(cybersecurity_ai.vulnerabilities.values())}

@app.get("/api/security-assets")
async def get_security_assets():
    """Get all security assets"""
    return {"assets": list(cybersecurity_ai.security_assets.values())}

@app.get("/api/compliance-checks")
async def get_compliance_checks():
    """Get all compliance checks"""
    return {"checks": list(cybersecurity_ai.compliance_checks.values())}

@app.get("/api/threat-intelligence")
async def get_threat_intelligence():
    """Get threat intelligence data"""
    return {"threats": list(cybersecurity_ai.threat_intelligence.values())}

@app.get("/api/threat-hunts")
async def get_threat_hunts():
    """Get threat hunting sessions"""
    return {"hunts": list(cybersecurity_ai.threat_hunts.values())}

@app.post("/api/incident-analysis/{incident_id}")
async def analyze_incident_endpoint(incident_id: str):
    """Analyze security incident"""
    try:
        analysis = await cybersecurity_ai.analyze_security_incident(incident_id)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing incident: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/threat-prediction")
async def predict_threats_endpoint(prediction_request: Dict):
    """Predict security threats"""
    try:
        timeframe = prediction_request.get("timeframe", "30_days")
        predictions = cybersecurity_ai.predict_security_threats(timeframe)
        return predictions
    except Exception as e:
        logger.error(f"Error predicting threats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cybersecurity-dashboard")
async def get_cybersecurity_dashboard():
    """Get cybersecurity dashboard data"""
    try:
        dashboard_data = cybersecurity_ai.get_cybersecurity_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting cybersecurity dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/analyze-incident")
async def analyze_demo_incident():
    """Analyze a random demo incident for testing"""
    incident_ids = list(cybersecurity_ai.security_incidents.keys())
    if not incident_ids:
        raise HTTPException(status_code=404, detail="No security incidents available for analysis")
    
    incident_id = random.choice(incident_ids)
    analysis = await cybersecurity_ai.analyze_security_incident(incident_id)
    return {"incident_id": incident_id, "analysis": analysis}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Cybersecurity...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")