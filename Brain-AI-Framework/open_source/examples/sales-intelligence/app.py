"""
Sales Intelligence Assistant - Brain AI Framework Example
A comprehensive sales intelligence system that helps sales professionals with lead analysis,
deal prediction, customer insights, and sales performance optimization.
"""

import json
import asyncio
import uvicorn
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
import sys
import os

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

# Import shared components
from shared.brain_ai_integration import BrainAIIntegration, BrainAIMemory
from shared.demo_data import DemoDataGenerator
from shared.web_components import WebComponents

# Configure logging
logger.add("logs/sales_intelligence.log", rotation="10 MB", level="INFO")

class DealStatus(Enum):
    """Deal status enumeration"""
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class LeadSource(Enum):
    """Lead source enumeration"""
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    TRADE_SHOW = "trade_show"
    SOCIAL_MEDIA = "social_media"
    EMAIL_CAMPAIGN = "email_campaign"

class Industry(Enum):
    """Industry enumeration"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    EDUCATION = "education"
    OTHER = "other"

@dataclass
class SalesMetric:
    """Sales performance metric"""
    period: str
    revenue: float
    deals_closed: int
    conversion_rate: float
    avg_deal_size: float
    sales_cycle_days: int

class CustomerProfile(BaseModel):
    """Customer profile model"""
    id: str
    name: str
    company: str
    industry: Industry
    revenue: float
    employee_count: int
    tech_stack: List[str]
    pain_points: List[str]
    budget_range: str
    decision_maker: bool
    engagement_level: float
    last_interaction: datetime
    satisfaction_score: float

class Deal(BaseModel):
    """Sales deal model"""
    id: str
    customer_id: str
    title: str
    value: float
    probability: float
    status: DealStatus
    stage: str
    expected_close_date: datetime
    assigned_sales_rep: str
    notes: List[str]
    activities: List[Dict]
    created_date: datetime

class LeadAnalysis(BaseModel):
    """Lead analysis result"""
    lead_id: str
    score: float
    qualification: str
    key_insights: List[str]
    recommended_actions: List[str]
    risk_factors: List[str]
    next_steps: List[str]

class SalesIntelligenceAI:
    """Main sales intelligence AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.customers: Dict[str, CustomerProfile] = {}
        self.deals: Dict[str, Deal] = {}
        self.lead_analyses: Dict[str, LeadAnalysis] = {}
        self.sales_metrics: List[SalesMetric] = []
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo customers
        for i in range(20):
            customer = self.demo_data.generate_customer_profile(
                customer_id=f"CUST_{i+1:03d}",
                industry=random.choice(list(Industry))
            )
            self.customers[customer.id] = customer
        
        # Generate demo deals
        for i in range(50):
            deal = self.demo_data.generate_sales_deal(
                deal_id=f"DEAL_{i+1:03d}",
                customer_ids=list(self.customers.keys())
            )
            self.deals[deal.id] = deal
        
        # Generate sales metrics
        self.sales_metrics = self._generate_sales_metrics()
        
        logger.info(f"Initialized demo data: {len(self.customers)} customers, {len(self.deals)} deals")
    
    def _generate_sales_metrics(self) -> List[SalesMetric]:
        """Generate historical sales metrics"""
        metrics = []
        base_date = datetime.now() - timedelta(days=365)
        
        for month in range(12):
            period_date = base_date + timedelta(days=30 * month)
            metrics.append(SalesMetric(
                period=period_date.strftime("%Y-%m"),
                revenue=random.uniform(50000, 200000),
                deals_closed=random.randint(5, 25),
                conversion_rate=random.uniform(0.15, 0.35),
                avg_deal_size=random.uniform(5000, 25000),
                sales_cycle_days=random.randint(30, 90)
            ))
        
        return metrics
    
    async def analyze_lead(self, lead_data: Dict) -> LeadAnalysis:
        """Analyze a sales lead using Brain AI"""
        try:
            # Prepare lead analysis context
            analysis_context = {
                "lead_data": lead_data,
                "customer_database": len(self.customers),
                "historical_deals": len(self.deals),
                "success_patterns": self._get_success_patterns()
            }
            
            # Use Brain AI to analyze the lead
            ai_analysis = await self.brain_ai.process_lead_analysis(analysis_context)
            
            # Generate detailed lead analysis
            lead_id = lead_data.get("id", f"LEAD_{len(self.lead_analyses)+1:03d}")
            
            # Calculate lead score based on multiple factors
            score = self._calculate_lead_score(lead_data)
            qualification = self._determine_qualification(score)
            insights = self._generate_lead_insights(lead_data)
            actions = self._recommend_actions(lead_data)
            risks = self._identify_risk_factors(lead_data)
            next_steps = self._suggest_next_steps(lead_data)
            
            analysis = LeadAnalysis(
                lead_id=lead_id,
                score=score,
                qualification=qualification,
                key_insights=insights,
                recommended_actions=actions,
                risk_factors=risks,
                next_steps=next_steps
            )
            
            # Store in memory for future reference
            await self.brain_ai.store_lead_analysis(lead_id, analysis.dict())
            
            self.lead_analyses[lead_id] = analysis
            logger.info(f"Analyzed lead {lead_id} with score {score:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing lead: {str(e)}")
            raise
    
    def _calculate_lead_score(self, lead_data: Dict) -> float:
        """Calculate lead score based on various factors"""
        score = 0.0
        
        # Company size factor
        employee_count = lead_data.get("employee_count", 0)
        if employee_count > 1000:
            score += 25
        elif employee_count > 500:
            score += 20
        elif employee_count > 100:
            score += 15
        elif employee_count > 50:
            score += 10
        else:
            score += 5
        
        # Revenue factor
        revenue = lead_data.get("revenue", 0)
        if revenue > 100000000:
            score += 25
        elif revenue > 50000000:
            score += 20
        elif revenue > 10000000:
            score += 15
        elif revenue > 1000000:
            score += 10
        else:
            score += 5
        
        # Industry factor
        industry = lead_data.get("industry", "other")
        tech_industries = ["technology", "finance", "healthcare"]
        if industry in tech_industries:
            score += 15
        else:
            score += 10
        
        # Engagement factor
        engagement = lead_data.get("engagement_score", 0)
        score += engagement * 10
        
        # Budget factor
        budget = lead_data.get("budget_range", "unknown")
        if "enterprise" in budget.lower():
            score += 20
        elif "mid" in budget.lower():
            score += 15
        elif "small" in budget.lower():
            score += 10
        
        # Decision maker factor
        if lead_data.get("is_decision_maker", False):
            score += 15
        
        # Source factor
        source = lead_data.get("source", "unknown")
        if source == "referral":
            score += 20
        elif source == "website":
            score += 15
        elif source == "cold_call":
            score += 5
        
        return min(score, 100.0)  # Cap at 100
    
    def _determine_qualification(self, score: float) -> str:
        """Determine lead qualification based on score"""
        if score >= 80:
            return "Hot Lead"
        elif score >= 60:
            return "Warm Lead"
        elif score >= 40:
            return "Qualified Lead"
        else:
            return "Cold Lead"
    
    def _generate_lead_insights(self, lead_data: Dict) -> List[str]:
        """Generate key insights about the lead"""
        insights = []
        
        # Company insights
        if lead_data.get("employee_count", 0) > 500:
            insights.append("Large enterprise - high-value potential")
        
        if lead_data.get("industry") == "technology":
            insights.append("Tech-savvy company - likely to adopt new solutions")
        
        # Engagement insights
        engagement = lead_data.get("engagement_score", 0)
        if engagement > 0.8:
            insights.append("Highly engaged prospect - strong buying intent")
        elif engagement > 0.5:
            insights.append("Moderate engagement - nurturing opportunity")
        
        # Budget insights
        budget = lead_data.get("budget_range", "")
        if "enterprise" in budget.lower():
            insights.append("Enterprise budget allocation detected")
        
        # Pain points insights
        pain_points = lead_data.get("pain_points", [])
        if len(pain_points) > 3:
            insights.append("Multiple pain points - solution-oriented prospect")
        
        return insights
    
    def _recommend_actions(self, lead_data: Dict) -> List[str]:
        """Recommend specific actions for the lead"""
        actions = []
        
        score = self._calculate_lead_score(lead_data)
        
        if score >= 80:
            actions.append("Schedule immediate demo with senior sales engineer")
            actions.append("Prepare customized proposal within 24 hours")
            actions.append("Assign to top-performing sales rep")
        elif score >= 60:
            actions.append("Schedule discovery call within 48 hours")
            actions.append("Send relevant case studies and testimonials")
            actions.append("Add to high-priority nurture sequence")
        elif score >= 40:
            actions.append("Add to weekly follow-up cadence")
            actions.append("Share educational content and resources")
            actions.append("Monitor engagement and behavior")
        else:
            actions.append("Add to automated nurture campaign")
            actions.append("Schedule check-in call in 30 days")
        
        # Industry-specific actions
        industry = lead_data.get("industry", "")
        if industry == "healthcare":
            actions.append("Ensure HIPAA compliance discussion")
        elif industry == "finance":
            actions.append("Address security and compliance requirements")
        
        return actions
    
    def _identify_risk_factors(self, lead_data: Dict) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Engagement risks
        if lead_data.get("engagement_score", 1) < 0.3:
            risks.append("Low engagement - may lose interest")
        
        # Budget risks
        budget = lead_data.get("budget_range", "")
        if "unknown" in budget.lower():
            risks.append("Budget not confirmed - qualification risk")
        
        # Decision maker risks
        if not lead_data.get("is_decision_maker", False):
            risks.append("Not a decision maker - additional stakeholder needed")
        
        # Timeline risks
        timeline = lead_data.get("timeline", "")
        if "urgent" in timeline.lower():
            risks.append("Rushed timeline - may indicate budget or scope issues")
        
        # Competition risks
        if lead_data.get("evaluating_competitors", False):
            risks.append("Actively evaluating competitors - competitive risk")
        
        return risks
    
    def _suggest_next_steps(self, lead_data: Dict) -> List[str]:
        """Suggest specific next steps"""
        next_steps = []
        
        score = self._calculate_lead_score(lead_data)
        
        if score >= 80:
            next_steps = [
                "Send calendar invite for demo",
                "Research company specific needs",
                "Prepare custom demo environment",
                "Coordinate with product team for technical deep-dive"
            ]
        elif score >= 60:
            next_steps = [
                "Send discovery call invitation",
                "Prepare qualification questions",
                "Research company background",
                "Identify additional stakeholders"
            ]
        else:
            next_steps = [
                "Add to email nurture sequence",
                "Send relevant content",
                "Set reminder for follow-up",
                "Monitor website and email engagement"
            ]
        
        return next_steps
    
    def _get_success_patterns(self) -> Dict:
        """Get patterns from successful deals"""
        won_deals = [deal for deal in self.deals.values() if deal.status == DealStatus.CLOSED_WON]
        
        patterns = {
            "avg_deal_size": sum(deal.value for deal in won_deals) / len(won_deals) if won_deals else 0,
            "avg_sales_cycle": 60,  # days
            "success_industries": ["technology", "healthcare", "finance"],
            "success_sources": ["referral", "website", "trade_show"]
        }
        
        return patterns
    
    def predict_deal_closure(self, deal_id: str) -> Dict:
        """Predict deal closure probability and timeline"""
        deal = self.deals.get(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")
        
        # Calculate closure probability based on multiple factors
        probability = deal.probability
        
        # Adjust based on deal age
        deal_age = (datetime.now() - deal.created_date).days
        if deal_age > 180:
            probability *= 0.7  # Reduce probability for very old deals
        elif deal_age > 90:
            probability *= 0.85
        
        # Adjust based on deal value
        if deal.value > 100000:
            probability *= 1.1  # Increase probability for high-value deals
        
        # Adjust based on customer engagement
        customer = self.customers.get(deal.customer_id)
        if customer:
            probability *= (0.8 + customer.engagement_level * 0.4)
        
        # Predict closure date
        base_days = 60  # Base sales cycle
        if deal.status == DealStatus.LEAD:
            base_days += 30
        elif deal.status == DealStatus.PROPOSAL:
            base_days += 15
        elif deal.status == DealStatus.NEGOTIATION:
            base_days += 7
        
        predicted_close = datetime.now() + timedelta(days=base_days)
        
        return {
            "deal_id": deal_id,
            "closure_probability": min(probability, 1.0),
            "predicted_close_date": predicted_close.isoformat(),
            "confidence_score": 0.85,
            "risk_factors": self._get_deal_risk_factors(deal),
            "recommendations": self._get_deal_recommendations(deal)
        }
    
    def _get_deal_risk_factors(self, deal: Deal) -> List[str]:
        """Get risk factors for a specific deal"""
        risks = []
        
        if deal.probability < 0.3:
            risks.append("Low probability - deal may not close")
        
        if deal.value > 500000:
            risks.append("High-value deal - extended decision process likely")
        
        deal_age = (datetime.now() - deal.created_date).days
        if deal_age > 120:
            risks.append("Extended sales cycle - risk of deal stalling")
        
        return risks
    
    def _get_deal_recommendations(self, deal: Deal) -> List[str]:
        """Get recommendations for deal progression"""
        recommendations = []
        
        if deal.status == DealStatus.LEAD:
            recommendations.append("Schedule discovery call to qualify")
            recommendations.append("Send relevant case studies")
        elif deal.status == DealStatus.QUALIFIED:
            recommendations.append("Prepare and deliver demo")
            recommendations.append("Identify additional stakeholders")
        elif deal.status == DealStatus.PROPOSAL:
            recommendations.append("Follow up on proposal within 48 hours")
            recommendations.append("Address any objections or concerns")
        elif deal.status == DealStatus.NEGOTIATION:
            recommendations.append("Negotiate terms and pricing")
            recommendations.append("Prepare contract for signature")
        
        return recommendations
    
    def get_sales_performance_dashboard(self) -> Dict:
        """Generate sales performance dashboard data"""
        # Calculate current month metrics
        current_month = datetime.now().strftime("%Y-%m")
        current_metrics = [m for m in self.sales_metrics if m.period == current_month]
        
        if current_metrics:
            current = current_metrics[0]
        else:
            # Generate current month estimate
            current = SalesMetric(
                period=current_month,
                revenue=random.uniform(80000, 120000),
                deals_closed=random.randint(8, 15),
                conversion_rate=random.uniform(0.20, 0.30),
                avg_deal_size=random.uniform(8000, 15000),
                sales_cycle_days=random.randint(45, 75)
            )
        
        # Calculate pipeline metrics
        active_deals = [deal for deal in self.deals.values() if deal.status != DealStatus.CLOSED_WON and deal.status != DealStatus.CLOSED_LOST]
        pipeline_value = sum(deal.value * deal.probability for deal in active_deals)
        
        # Calculate conversion rates by stage
        stage_conversions = {}
        for status in DealStatus:
            deals_in_stage = [d for d in self.deals.values() if d.status == status]
            if deals_in_stage:
                stage_conversions[status.value] = len(deals_in_stage)
        
        return {
            "current_performance": current,
            "pipeline_value": pipeline_value,
            "active_deals_count": len(active_deals),
            "stage_distribution": stage_conversions,
            "monthly_trend": self.sales_metrics[-6:],  # Last 6 months
            "top_performers": self._get_top_performers(),
            "conversion_funnel": self._get_conversion_funnel(),
            "forecast": self._generate_forecast()
        }
    
    def _get_top_performers(self) -> List[Dict]:
        """Get top performing sales reps"""
        rep_performance = {}
        
        for deal in self.deals.values():
            if deal.status == DealStatus.CLOSED_WON:
                rep = deal.assigned_sales_rep
                if rep not in rep_performance:
                    rep_performance[rep] = {"deals": 0, "revenue": 0}
                rep_performance[rep]["deals"] += 1
                rep_performance[rep]["revenue"] += deal.value
        
        # Sort by revenue
        top_performers = sorted(
            [{"name": rep, **data} for rep, data in rep_performance.items()],
            key=lambda x: x["revenue"],
            reverse=True
        )[:5]
        
        return top_performers
    
    def _get_conversion_funnel(self) -> Dict:
        """Get conversion funnel data"""
        total_leads = len([d for d in self.deals.values() if d.status == DealStatus.LEAD])
        qualified = len([d for d in self.deals.values() if d.status == DealStatus.QUALIFIED])
        proposal = len([d for d in self.deals.values() if d.status == DealStatus.PROPOSAL])
        negotiation = len([d for d in self.deals.values() if d.status == DealStatus.NEGOTIATION])
        won = len([d for d in self.deals.values() if d.status == DealStatus.CLOSED_WON])
        
        return {
            "leads": total_leads,
            "qualified": qualified,
            "proposal": proposal,
            "negotiation": negotiation,
            "won": won,
            "conversion_rates": {
                "lead_to_qualified": qualified / total_leads if total_leads > 0 else 0,
                "qualified_to_proposal": proposal / qualified if qualified > 0 else 0,
                "proposal_to_negotiation": negotiation / proposal if proposal > 0 else 0,
                "negotiation_to_won": won / negotiation if negotiation > 0 else 0
            }
        }
    
    def _generate_forecast(self) -> Dict:
        """Generate sales forecast"""
        current_pipeline = sum(deal.value * deal.probability for deal in self.deals.values())
        
        # Simple forecast based on historical performance
        avg_monthly = sum(m.revenue for m in self.sales_metrics[-6:]) / 6
        
        return {
            "current_pipeline": current_pipeline,
            "next_month_forecast": avg_monthly * 1.1,
            "quarter_forecast": avg_monthly * 3 * 1.15,
            "confidence_interval": (avg_monthly * 0.9, avg_monthly * 1.2)
        }

# FastAPI Application
app = FastAPI(title="Sales Intelligence Assistant", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
sales_ai = SalesIntelligenceAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=sales_ai.web_components.render_sales_dashboard())

@app.get("/api/customers")
async def get_customers():
    """Get all customers"""
    return {"customers": list(sales_ai.customers.values())}

@app.get("/api/deals")
async def get_deals():
    """Get all deals"""
    return {"deals": list(sales_ai.deals.values())}

@app.post("/api/leads/analyze")
async def analyze_lead_endpoint(lead_data: Dict):
    """Analyze a sales lead"""
    try:
        analysis = await sales_ai.analyze_lead(lead_data)
        return analysis.dict()
    except Exception as e:
        logger.error(f"Error analyzing lead: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deals/{deal_id}/prediction")
async def predict_deal_closure(deal_id: str):
    """Predict deal closure"""
    try:
        prediction = sales_ai.predict_deal_closure(deal_id)
        return prediction
    except Exception as e:
        logger.error(f"Error predicting deal closure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get dashboard data"""
    try:
        dashboard_data = sales_ai.get_sales_performance_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads")
async def get_lead_analyses():
    """Get all lead analyses"""
    return {"analyses": list(sales_ai.lead_analyses.values())}

@app.get("/api/metrics")
async def get_sales_metrics():
    """Get sales metrics"""
    return {"metrics": sales_ai.sales_metrics}

@app.post("/api/demo/generate-lead")
async def generate_demo_lead():
    """Generate a random demo lead for testing"""
    demo_lead = sales_ai.demo_data.generate_sales_lead()
    analysis = await sales_ai.analyze_lead(demo_lead)
    return {"lead": demo_lead, "analysis": analysis.dict()}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Sales Intelligence Assistant...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")