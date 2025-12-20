"""
Financial Risk Assessment - Brain AI Framework Example
A comprehensive financial risk management system that helps institutions assess credit risk,
market risk, compliance risk, and operational risk using Brain AI Framework.
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

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from loguru import logger
import random
from dataclasses import dataclass
from enum import Enum
import numpy as np

# Import shared components
from shared.brain_ai_integration import BrainAIIntegration, BrainAIMemory
from shared.demo_data import DemoDataGenerator
from shared.web_components import WebComponents

# Configure logging
logger.add("logs/financial_risk.log", rotation="10 MB", level="INFO")

class RiskCategory(Enum):
    """Risk category enumeration"""
    CREDIT = "credit"
    MARKET = "market"
    OPERATIONAL = "operational"
    LIQUIDITY = "liquidity"
    COMPLIANCE = "compliance"
    REPUTATION = "reputation"

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CreditRating(Enum):
    """Credit rating enumeration"""
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"

class AssetClass(Enum):
    """Asset class enumeration"""
    EQUITY = "equity"
    FIXED_INCOME = "fixed_income"
    COMMODITIES = "commodities"
    REAL_ESTATE = "real_estate"
    ALTERNATIVES = "alternatives"
    CASH = "cash"

class Industry(Enum):
    """Industry enumeration"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    ENERGY = "energy"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    REAL_ESTATE = "real_estate"
    UTILITIES = "utilities"

@dataclass
class MarketIndicator:
    """Market indicator data point"""
    date: datetime
    indicator_name: str
    value: float
    change_percent: float
    volatility: float

@dataclass
class RiskMetric:
    """Risk metric"""
    name: str
    value: float
    threshold: float
    status: RiskLevel
    description: str

class CreditProfile(BaseModel):
    """Credit profile model"""
    borrower_id: str
    name: str
    credit_rating: CreditRating
    credit_score: int
    debt_to_income_ratio: float
    annual_income: float
    existing_debt: float
    payment_history: float  # Percentage
    collateral_value: float
    loan_amount: float
    loan_purpose: str
    industry: Industry
    risk_factors: List[str]
    last_updated: datetime

class MarketPosition(BaseModel):
    """Market position model"""
    position_id: str
    asset_class: AssetClass
    instrument_name: str
    quantity: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    var_1day: float  # Value at Risk (1 day)
    var_10day: float  # Value at Risk (10 day)
    beta: float
    volatility: float
    concentration_risk: float

class RiskAssessment(BaseModel):
    """Risk assessment result"""
    assessment_id: str
    entity_id: str
    assessment_type: RiskCategory
    overall_risk_score: float
    risk_level: RiskLevel
    assessment_date: datetime
    key_risks: List[str]
    mitigation_strategies: List[str]
    recommendations: List[str]
    confidence_score: float

class ComplianceCheck(BaseModel):
    """Compliance check result"""
    check_id: str
    regulation: str
    compliance_status: bool
    issues: List[str]
    recommendations: List[str]
    due_date: datetime
    priority: RiskLevel

class FinancialRiskAI:
    """Main financial risk AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.credit_profiles: Dict[str, CreditProfile] = {}
        self.market_positions: Dict[str, MarketPosition] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.market_indicators: List[MarketIndicator] = []
        
        # Risk thresholds
        self.risk_thresholds = {
            "credit_score_low": 600,
            "debt_to_income_high": 0.4,
            "var_threshold": 0.05,  # 5% of portfolio
            "concentration_limit": 0.20,  # 20% single position limit
            "liquidity_ratio_min": 0.15
        }
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo credit profiles
        for i in range(50):
            profile = self.demo_data.generate_credit_profile(
                borrower_id=f"BORROWER_{i+1:03d}"
            )
            self.credit_profiles[profile.borrower_id] = profile
        
        # Generate demo market positions
        for i in range(100):
            position = self.demo_data.generate_market_position(
                position_id=f"POSITION_{i+1:03d}"
            )
            self.market_positions[position.position_id] = position
        
        # Generate market indicators
        self.market_indicators = self._generate_market_indicators()
        
        # Generate risk assessments
        self._generate_risk_assessments()
        
        # Generate compliance checks
        self._generate_compliance_checks()
        
        logger.info(f"Initialized demo data: {len(self.credit_profiles)} credit profiles, "
                   f"{len(self.market_positions)} market positions")
    
    def _generate_market_indicators(self) -> List[MarketIndicator]:
        """Generate market indicators"""
        indicators = []
        base_date = datetime.now() - timedelta(days=365)
        
        indicator_names = [
            "VIX", "S&P 500", "10Y Treasury", "USD Index", "Oil Price",
            "Gold Price", "Credit Spreads", "Housing Index", "GDP Growth", "Inflation Rate"
        ]
        
        for day in range(365):
            current_date = base_date + timedelta(days=day)
            
            for indicator_name in indicator_names:
                # Generate realistic market data
                if indicator_name == "VIX":
                    value = random.uniform(15, 45)
                elif indicator_name == "S&P 500":
                    value = random.uniform(3000, 4500)
                elif indicator_name == "10Y Treasury":
                    value = random.uniform(2.0, 5.0)
                elif indicator_name == "USD Index":
                    value = random.uniform(90, 110)
                elif indicator_name == "Oil Price":
                    value = random.uniform(50, 120)
                elif indicator_name == "Gold Price":
                    value = random.uniform(1500, 2200)
                else:
                    value = random.uniform(-5, 10)
                
                change_percent = random.uniform(-3, 3)
                volatility = random.uniform(0.1, 2.0)
                
                indicators.append(MarketIndicator(
                    date=current_date,
                    indicator_name=indicator_name,
                    value=value,
                    change_percent=change_percent,
                    volatility=volatility
                ))
        
        return indicators
    
    def _generate_risk_assessments(self):
        """Generate sample risk assessments"""
        assessment_types = [RiskCategory.CREDIT, RiskCategory.MARKET, RiskCategory.OPERATIONAL]
        
        for i in range(25):
            assessment = RiskAssessment(
                assessment_id=f"RISK_{i+1:03d}",
                entity_id=f"ENTITY_{random.randint(1, 10):03d}",
                assessment_type=random.choice(assessment_types),
                overall_risk_score=random.uniform(0.1, 0.9),
                risk_level=self._score_to_risk_level(random.uniform(0.1, 0.9)),
                assessment_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                key_risks=self._generate_key_risks(),
                mitigation_strategies=self._generate_mitigation_strategies(),
                recommendations=self._generate_recommendations(),
                confidence_score=random.uniform(0.7, 0.95)
            )
            
            self.risk_assessments[assessment.assessment_id] = assessment
    
    def _generate_compliance_checks(self):
        """Generate sample compliance checks"""
        regulations = [
            "Basel III", "SOX", "GDPR", "AML/KYC", "MiFID II",
            "Dodd-Frank", "IFRS 9", "CCAR", "Basel IV"
        ]
        
        for i in range(20):
            check = ComplianceCheck(
                check_id=f"COMP_{i+1:03d}",
                regulation=random.choice(regulations),
                compliance_status=random.choice([True, True, True, False]),  # 75% compliance rate
                issues=self._generate_compliance_issues() if random.random() > 0.75 else [],
                recommendations=self._generate_compliance_recommendations(),
                due_date=datetime.now() + timedelta(days=random.randint(7, 90)),
                priority=random.choice([RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH])
            )
            
            self.compliance_checks[check.check_id] = check
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score >= 0.8:
            return RiskLevel.CRITICAL
        elif score >= 0.6:
            return RiskLevel.HIGH
        elif score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_key_risks(self) -> List[str]:
        """Generate key risk factors"""
        risk_factors = [
            "High debt-to-income ratio",
            "Concentrated position exposure",
            "Market volatility increase",
            "Regulatory compliance gaps",
            "Counterparty default risk",
            "Liquidity constraints",
            "Interest rate sensitivity",
            "Currency exposure",
            "Credit rating downgrade",
            "Operational failures"
        ]
        
        return random.sample(risk_factors, random.randint(2, 5))
    
    def _generate_mitigation_strategies(self) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = [
            "Diversify credit portfolio",
            "Implement position limits",
            "Increase collateral requirements",
            "Enhance monitoring procedures",
            "Stress test scenarios",
            "Hedge market exposures",
            "Strengthen compliance controls",
            "Improve liquidity buffers",
            "Diversify funding sources",
            "Upgrade risk management systems"
        ]
        
        return random.sample(strategies, random.randint(2, 4))
    
    def _generate_recommendations(self) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = [
            "Reduce concentration risk exposure",
            "Implement automated monitoring",
            "Enhance due diligence procedures",
            "Strengthen capital buffers",
            "Improve risk reporting",
            "Update risk policies",
            "Enhance staff training",
            "Implement early warning systems",
            "Strengthen governance framework",
            "Regular risk assessments"
        ]
        
        return random.sample(recommendations, random.randint(1, 3))
    
    def _generate_compliance_issues(self) -> List[str]:
        """Generate compliance issues"""
        issues = [
            "Incomplete documentation",
            "Missing approval signatures",
            "Outdated policies",
            "Training gaps",
            "System control weaknesses",
            "Reporting delays",
            "Data quality issues",
            "Process inefficiencies"
        ]
        
        return random.sample(issues, random.randint(1, 3))
    
    def _generate_compliance_recommendations(self) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = [
            "Update compliance manual",
            "Conduct staff training",
            "Implement system controls",
            "Enhance monitoring procedures",
            "Update documentation",
            "Strengthen governance",
            "Regular compliance reviews",
            "Improve reporting systems"
        ]
        
        return random.sample(recommendations, random.randint(1, 2))
    
    async def assess_credit_risk(self, borrower_id: str) -> RiskAssessment:
        """Assess credit risk for a borrower"""
        try:
            borrower = self.credit_profiles.get(borrower_id)
            if not borrower:
                raise ValueError(f"Borrower {borrower_id} not found")
            
            # Prepare credit risk analysis context
            analysis_context = {
                "borrower_profile": borrower.dict(),
                "market_conditions": self._get_current_market_conditions(),
                "historical_data": self._get_borrower_history(borrower_id),
                "peer_analysis": self._get_peer_analysis(borrower.industry)
            }
            
            # Use Brain AI to analyze credit risk
            ai_analysis = await self.brain_ai.process_credit_risk_analysis(analysis_context)
            
            # Calculate credit risk score
            risk_score = self._calculate_credit_risk_score(borrower)
            risk_level = self._score_to_risk_level(risk_score)
            
            # Generate risk assessment
            assessment = RiskAssessment(
                assessment_id=f"CREDIT_{borrower_id}_{datetime.now().strftime('%Y%m%d')}",
                entity_id=borrower_id,
                assessment_type=RiskCategory.CREDIT,
                overall_risk_score=risk_score,
                risk_level=risk_level,
                assessment_date=datetime.now(),
                key_risks=self._identify_credit_risks(borrower),
                mitigation_strategies=self._suggest_credit_mitigation(borrower),
                recommendations=self._generate_credit_recommendations(borrower),
                confidence_score=0.88
            )
            
            # Store in memory for future reference
            await self.brain_ai.store_credit_assessment(borrower_id, assessment.dict())
            
            self.risk_assessments[assessment.assessment_id] = assessment
            logger.info(f"Assessed credit risk for {borrower_id} with score {risk_score:.2f}")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing credit risk: {str(e)}")
            raise
    
    def _calculate_credit_risk_score(self, borrower: CreditProfile) -> float:
        """Calculate credit risk score"""
        score = 0.0
        
        # Credit score factor (40% weight)
        if borrower.credit_score >= 750:
            score += 0.05
        elif borrower.credit_score >= 700:
            score += 0.10
        elif borrower.credit_score >= 650:
            score += 0.20
        elif borrower.credit_score >= 600:
            score += 0.30
        else:
            score += 0.40
        
        # Debt-to-income ratio (30% weight)
        dti = borrower.debt_to_income_ratio
        if dti <= 0.20:
            score += 0.05
        elif dti <= 0.30:
            score += 0.10
        elif dti <= 0.40:
            score += 0.20
        else:
            score += 0.30
        
        # Payment history (20% weight)
        payment_score = (1 - borrower.payment_history) * 0.20
        score += payment_score
        
        # Collateral coverage (10% weight)
        if borrower.collateral_value > 0:
            coverage_ratio = borrower.collateral_value / borrower.loan_amount
            if coverage_ratio >= 1.5:
                score += 0.02
            elif coverage_ratio >= 1.0:
                score += 0.05
            elif coverage_ratio >= 0.8:
                score += 0.08
            else:
                score += 0.10
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _identify_credit_risks(self, borrower: CreditProfile) -> List[str]:
        """Identify specific credit risks"""
        risks = []
        
        if borrower.credit_score < 650:
            risks.append("Low credit score indicates higher default risk")
        
        if borrower.debt_to_income_ratio > 0.40:
            risks.append("High debt-to-income ratio suggests financial stress")
        
        if borrower.payment_history < 0.90:
            risks.append("Poor payment history increases default probability")
        
        if borrower.collateral_value / borrower.loan_amount < 1.0:
            risks.append("Insufficient collateral coverage")
        
        if borrower.industry in [Industry.ENERGY, Industry.RETAIL]:
            risks.append("Industry volatility increases credit risk")
        
        return risks
    
    def _suggest_credit_mitigation(self, borrower: CreditProfile) -> List[str]:
        """Suggest credit risk mitigation strategies"""
        strategies = []
        
        if borrower.credit_score < 650:
            strategies.append("Require additional collateral or guarantees")
            strategies.append("Implement stricter monitoring")
        
        if borrower.debt_to_income_ratio > 0.40:
            strategies.append("Reduce loan amount or extend term")
            strategies.append("Require debt consolidation")
        
        if borrower.payment_history < 0.90:
            strategies.append("Implement payment monitoring")
            strategies.append("Require payment guarantees")
        
        if borrower.collateral_value / borrower.loan_amount < 1.0:
            strategies.append("Increase collateral requirements")
            strategies.append("Reduce loan-to-value ratio")
        
        return strategies
    
    def _generate_credit_recommendations(self, borrower: CreditProfile) -> List[str]:
        """Generate credit recommendations"""
        recommendations = []
        
        risk_score = self._calculate_credit_risk_score(borrower)
        
        if risk_score > 0.6:
            recommendations.append("Consider loan denial or significant rate increase")
        elif risk_score > 0.4:
            recommendations.append("Approve with additional conditions")
        else:
            recommendations.append("Standard approval process")
        
        recommendations.append("Regular credit monitoring")
        recommendations.append("Annual review of financial condition")
        
        return recommendations
    
    def _get_current_market_conditions(self) -> Dict:
        """Get current market conditions"""
        latest_indicators = {}
        for indicator in self.market_indicators[-10:]:
            latest_indicators[indicator.indicator_name] = {
                "value": indicator.value,
                "volatility": indicator.volatility,
                "change": indicator.change_percent
            }
        return latest_indicators
    
    def _get_borrower_history(self, borrower_id: str) -> Dict:
        """Get borrower historical data"""
        # Generate mock historical data
        return {
            "credit_score_trend": random.choice(["improving", "stable", "declining"]),
            "payment_history": random.uniform(0.85, 0.98),
            "previous_loans": random.randint(0, 5),
            "default_history": random.choice([True, False])
        }
    
    def _get_peer_analysis(self, industry: Industry) -> Dict:
        """Get peer analysis for industry"""
        return {
            "industry_default_rate": random.uniform(0.02, 0.08),
            "average_credit_score": random.randint(650, 750),
            "industry_outlook": random.choice(["positive", "neutral", "negative"])
        }
    
    def calculate_portfolio_var(self, confidence_level: float = 0.95) -> Dict:
        """Calculate Value at Risk for the portfolio"""
        try:
            total_portfolio_value = sum(pos.market_value for pos in self.market_positions.values())
            
            # Calculate portfolio VaR using simplified methodology
            portfolio_var_1day = 0
            portfolio_var_10day = 0
            
            for position in self.market_positions.values():
                # Weight by position value
                weight = position.market_value / total_portfolio_value
                
                # Calculate individual VaR contribution
                var_1day_contrib = weight * position.var_1day * position.market_value
                var_10day_contrib = weight * position.var_10day * position.market_value
                
                portfolio_var_1day += var_1day_contrib
                portfolio_var_10day += var_10day_contrib
            
            # Adjust for diversification (simplified)
            diversification_factor = 0.8  # Assume 20% diversification benefit
            portfolio_var_1day *= diversification_factor
            portfolio_var_10day *= diversification_factor
            
            # Convert to percentage
            var_1day_pct = (portfolio_var_1day / total_portfolio_value) * 100
            var_10day_pct = (portfolio_var_10day / total_portfolio_value) * 100
            
            return {
                "portfolio_value": total_portfolio_value,
                "var_1day": portfolio_var_1day,
                "var_10day": portfolio_var_10day,
                "var_1day_percent": var_1day_pct,
                "var_10day_percent": var_10day_pct,
                "confidence_level": confidence_level,
                "risk_level": self._var_to_risk_level(var_1day_pct),
                "breach_count": self._count_var_breaches(),
                "recommendations": self._var_recommendations(var_1day_pct)
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio VaR: {str(e)}")
            raise
    
    def _var_to_risk_level(self, var_percent: float) -> RiskLevel:
        """Convert VaR percentage to risk level"""
        if var_percent > 10:
            return RiskLevel.CRITICAL
        elif var_percent > 5:
            return RiskLevel.HIGH
        elif var_percent > 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _count_var_breaches(self) -> int:
        """Count VaR breaches in recent history"""
        # Mock implementation - in reality would check historical VaR breaches
        return random.randint(0, 5)
    
    def _var_recommendations(self, var_percent: float) -> List[str]:
        """Generate VaR-based recommendations"""
        recommendations = []
        
        if var_percent > 10:
            recommendations.append("Immediate portfolio rebalancing required")
            recommendations.append("Reduce position sizes significantly")
        elif var_percent > 5:
            recommendations.append("Consider reducing high-risk positions")
            recommendations.append("Implement hedging strategies")
        elif var_percent > 2:
            recommendations.append("Monitor positions closely")
            recommendations.append("Consider diversification")
        
        recommendations.append("Daily VaR monitoring")
        recommendations.append("Stress testing")
        
        return recommendations
    
    def assess_liquidity_risk(self) -> Dict:
        """Assess overall liquidity risk"""
        try:
            # Calculate liquidity metrics
            total_assets = sum(pos.market_value for pos in self.market_positions.values())
            liquid_assets = sum(pos.market_value for pos in self.market_positions.values() 
                              if pos.asset_class in [AssetClass.EQUITY, AssetClass.CASH])
            
            liquidity_ratio = liquid_assets / total_assets if total_assets > 0 else 0
            
            # Calculate funding concentration
            funding_sources = self._get_funding_sources()
            concentration_risk = self._calculate_concentration_risk(funding_sources)
            
            # Assess liquidity risk level
            risk_score = self._calculate_liquidity_risk_score(liquidity_ratio, concentration_risk)
            risk_level = self._score_to_risk_level(risk_score)
            
            return {
                "liquidity_ratio": liquidity_ratio,
                "liquid_assets": liquid_assets,
                "total_assets": total_assets,
                "concentration_risk": concentration_risk,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "stress_test_results": self._run_liquidity_stress_test(),
                "recommendations": self._liquidity_recommendations(liquidity_ratio, concentration_risk)
            }
            
        except Exception as e:
            logger.error(f"Error assessing liquidity risk: {str(e)}")
            raise
    
    def _get_funding_sources(self) -> Dict:
        """Get funding sources (mock implementation)"""
        return {
            "deposits": 0.60,
            "wholesale_funding": 0.25,
            "capital": 0.10,
            "other": 0.05
        }
    
    def _calculate_concentration_risk(self, funding_sources: Dict) -> float:
        """Calculate funding concentration risk"""
        return max(funding_sources.values())
    
    def _calculate_liquidity_risk_score(self, liquidity_ratio: float, concentration_risk: float) -> float:
        """Calculate liquidity risk score"""
        score = 0.0
        
        # Liquidity ratio factor
        if liquidity_ratio < 0.10:
            score += 0.4
        elif liquidity_ratio < 0.15:
            score += 0.3
        elif liquidity_ratio < 0.20:
            score += 0.2
        else:
            score += 0.1
        
        # Concentration risk factor
        if concentration_risk > 0.80:
            score += 0.4
        elif concentration_risk > 0.60:
            score += 0.3
        elif concentration_risk > 0.40:
            score += 0.2
        else:
            score += 0.1
        
        return min(score, 1.0)
    
    def _run_liquidity_stress_test(self) -> Dict:
        """Run liquidity stress test scenarios"""
        return {
            "scenario_1_market_shock": {
                "description": "20% market decline",
                "liquidity_impact": "15% reduction",
                "funding_impact": "10% increase in cost"
            },
            "scenario_2_funding_crisis": {
                "description": "Wholesale funding unavailable",
                "liquidity_impact": "Rely on deposits only",
                "funding_impact": "50% funding reduction"
            },
            "scenario_3_combined_stress": {
                "description": "Market shock + funding crisis",
                "liquidity_impact": "25% reduction",
                "funding_impact": "Severe funding constraints"
            }
        }
    
    def _liquidity_recommendations(self, liquidity_ratio: float, concentration_risk: float) -> List[str]:
        """Generate liquidity recommendations"""
        recommendations = []
        
        if liquidity_ratio < 0.15:
            recommendations.append("Increase liquidity buffer")
            recommendations.append("Reduce illiquid asset exposure")
        
        if concentration_risk > 0.60:
            recommendations.append("Diversify funding sources")
            recommendations.append("Reduce dependence on single funding type")
        
        recommendations.append("Regular stress testing")
        recommendations.append("Maintain contingency funding plan")
        recommendations.append("Daily liquidity monitoring")
        
        return recommendations
    
    def get_risk_dashboard(self) -> Dict:
        """Generate comprehensive risk dashboard"""
        try:
            # Calculate key risk metrics
            portfolio_var = self.calculate_portfolio_var()
            liquidity_risk = self.assess_liquidity_risk()
            
            # Credit risk metrics
            high_credit_risk = len([p for p in self.credit_profiles.values() 
                                  if self._calculate_credit_risk_score(p) > 0.6])
            
            # Market risk metrics
            total_market_risk = sum(pos.var_1day for pos in self.market_positions.values())
            
            # Compliance metrics
            compliance_issues = len([c for c in self.compliance_checks.values() 
                                   if not c.compliance_status])
            
            # Operational risk metrics
            operational_risks = len([r for r in self.risk_assessments.values() 
                                   if r.assessment_type == RiskCategory.OPERATIONAL])
            
            return {
                "portfolio_var": portfolio_var,
                "liquidity_risk": liquidity_risk,
                "credit_risk": {
                    "high_risk_borrowers": high_credit_risk,
                    "total_borrowers": len(self.credit_profiles),
                    "avg_credit_score": statistics.mean([p.credit_score for p in self.credit_profiles.values()])
                },
                "market_risk": {
                    "total_var": total_market_risk,
                    "positions_count": len(self.market_positions),
                    "concentration_risk": self._calculate_portfolio_concentration()
                },
                "compliance": {
                    "open_issues": compliance_issues,
                    "total_checks": len(self.compliance_checks),
                    "compliance_rate": (len(self.compliance_checks) - compliance_issues) / len(self.compliance_checks)
                },
                "operational_risk": {
                    "assessments_count": operational_risks,
                    "high_risk_areas": len([r for r in self.risk_assessments.values() 
                                          if r.risk_level == RiskLevel.HIGH])
                },
                "risk_trends": self._analyze_risk_trends(),
                "alerts": self._generate_risk_alerts()
            }
            
        except Exception as e:
            logger.error(f"Error generating risk dashboard: {str(e)}")
            raise
    
    def _calculate_portfolio_concentration(self) -> float:
        """Calculate portfolio concentration risk"""
        total_value = sum(pos.market_value for pos in self.market_positions.values())
        if total_value == 0:
            return 0
        
        position_weights = [pos.market_value / total_value for pos in self.market_positions.values()]
        return max(position_weights)
    
    def _analyze_risk_trends(self) -> Dict:
        """Analyze risk trends over time"""
        return {
            "credit_risk_trend": random.choice(["improving", "stable", "worsening"]),
            "market_risk_trend": random.choice(["improving", "stable", "worsening"]),
            "liquidity_risk_trend": random.choice(["improving", "stable", "worsening"]),
            "overall_risk_trend": random.choice(["improving", "stable", "worsening"])
        }
    
    def _generate_risk_alerts(self) -> List[Dict]:
        """Generate risk alerts"""
        alerts = []
        
        # Check for critical risks
        portfolio_var = self.calculate_portfolio_var()
        if portfolio_var["risk_level"] == RiskLevel.CRITICAL:
            alerts.append({
                "type": "market_risk",
                "level": "critical",
                "message": "Portfolio VaR exceeds critical threshold",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check compliance issues
        compliance_issues = [c for c in self.compliance_checks.values() if not c.compliance_status]
        if compliance_issues:
            alerts.append({
                "type": "compliance",
                "level": "high",
                "message": f"{len(compliance_issues)} compliance issues require attention",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check liquidity risk
        liquidity_risk = self.assess_liquidity_risk()
        if liquidity_risk["risk_level"] == RiskLevel.HIGH:
            alerts.append({
                "type": "liquidity",
                "level": "high",
                "message": "Liquidity risk level is elevated",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts

# FastAPI Application
app = FastAPI(title="Financial Risk Assessment", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
risk_ai = FinancialRiskAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=risk_ai.web_components.render_risk_dashboard())

@app.get("/api/credit-profiles")
async def get_credit_profiles():
    """Get all credit profiles"""
    return {"profiles": list(risk_ai.credit_profiles.values())}

@app.get("/api/market-positions")
async def get_market_positions():
    """Get all market positions"""
    return {"positions": list(risk_ai.market_positions.values())}

@app.post("/api/credit-risk/{borrower_id}")
async def assess_credit_risk_endpoint(borrower_id: str):
    """Assess credit risk for a borrower"""
    try:
        assessment = await risk_ai.assess_credit_risk(borrower_id)
        return assessment.dict()
    except Exception as e:
        logger.error(f"Error assessing credit risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio-var")
async def get_portfolio_var():
    """Get portfolio Value at Risk"""
    try:
        var_data = risk_ai.calculate_portfolio_var()
        return var_data
    except Exception as e:
        logger.error(f"Error calculating portfolio VaR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/liquidity-risk")
async def get_liquidity_risk():
    """Get liquidity risk assessment"""
    try:
        liquidity_data = risk_ai.assess_liquidity_risk()
        return liquidity_data
    except Exception as e:
        logger.error(f"Error assessing liquidity risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-dashboard")
async def get_risk_dashboard():
    """Get comprehensive risk dashboard"""
    try:
        dashboard_data = risk_ai.get_risk_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting risk dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-assessments")
async def get_risk_assessments():
    """Get all risk assessments"""
    return {"assessments": list(risk_ai.risk_assessments.values())}

@app.get("/api/compliance-checks")
async def get_compliance_checks():
    """Get all compliance checks"""
    return {"checks": list(risk_ai.compliance_checks.values())}

@app.get("/api/market-indicators")
async def get_market_indicators():
    """Get market indicators"""
    return {"indicators": [ind.__dict__ for ind in risk_ai.market_indicators[-30:]]}

@app.post("/api/demo/generate-credit-profile")
async def generate_demo_credit_profile():
    """Generate a random demo credit profile for testing"""
    demo_profile = risk_ai.demo_data.generate_credit_profile(
        borrower_id=f"BORROWER_{len(risk_ai.credit_profiles)+1:03d}"
    )
    assessment = await risk_ai.assess_credit_risk(demo_profile.borrower_id)
    return {"profile": demo_profile.dict(), "assessment": assessment.dict()}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Financial Risk Assessment...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")