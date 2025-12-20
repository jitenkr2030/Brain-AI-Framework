"""
Smart Quality Control - Brain AI Framework Example
A comprehensive quality control system that helps manufacturing and industrial companies
with AI-powered quality inspection, defect detection, and process optimization.
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
import base64
from io import BytesIO

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
logger.add("logs/quality_control.log", rotation="10 MB", level="INFO")

class QualityLevel(Enum):
    """Quality level enumeration"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    DEFECTIVE = "defective"
    REJECT = "reject"

class DefectType(Enum):
    """Defect type enumeration"""
    SCRATCH = "scratch"
    DISCOLORATION = "discoloration"
    DIMENSION = "dimension"
    SURFACE = "surface"
    ASSEMBLY = "assembly"
    FUNCTIONAL = "functional"
    CONTAMINATION = "contamination"
    STRUCTURAL = "structural"

class ProductionStage(Enum):
    """Production stage enumeration"""
    RAW_MATERIAL = "raw_material"
    PROCESSING = "processing"
    ASSEMBLY = "assembly"
    FINISHING = "finishing"
    PACKAGING = "packaging"
    FINAL_INSPECTION = "final_inspection"

class ProductCategory(Enum):
    """Product category enumeration"""
    ELECTRONICS = "electronics"
    AUTOMOTIVE = "automotive"
    AEROSPACE = "aerospace"
    MEDICAL = "medical"
    CONSUMER_GOODS = "consumer_goods"
    INDUSTRIAL = "industrial"

@dataclass
class QualityMetric:
    """Quality metric data point"""
    metric_name: str
    value: float
    target: float
    tolerance: float
    unit: str
    status: QualityLevel

@dataclass
class InspectionPoint:
    """Quality inspection point"""
    point_id: str
    stage: ProductionStage
    description: str
    inspection_type: str
    frequency: str
    critical: bool

class Product(BaseModel):
    """Product model"""
    product_id: str
    name: str
    category: ProductCategory
    serial_number: str
    production_date: datetime
    batch_id: str
    specifications: Dict[str, Any]
    quality_target: QualityLevel

class InspectionResult(BaseModel):
    """Quality inspection result"""
    inspection_id: str
    product_id: str
    inspection_point: str
    inspector: str
    timestamp: datetime
    quality_level: QualityLevel
    defects: List[Dict]
    measurements: List[QualityMetric]
    images: List[str]  # Base64 encoded images
    notes: str
    actions_taken: List[str]
    ai_confidence: float

class ProcessParameter(BaseModel):
    """Process parameter model"""
    parameter_id: str
    process_name: str
    stage: ProductionStage
    current_value: float
    target_value: float
    tolerance: float
    unit: str
    status: QualityLevel
    last_updated: datetime

class QualityAlert(BaseModel):
    """Quality alert model"""
    alert_id: str
    alert_type: str
    severity: QualityLevel
    description: str
    product_id: Optional[str]
    process_parameter: Optional[str]
    timestamp: datetime
    acknowledged: bool
    resolved: bool
    resolution_notes: Optional[str]

class QualityTrend(BaseModel):
    """Quality trend analysis"""
    analysis_id: str
    metric_name: str
    time_period: str
    trend_direction: str
    trend_strength: float
    predicted_value: float
    recommendations: List[str]
    analysis_date: datetime

class SmartQualityControlAI:
    """Main quality control AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.products: Dict[str, Product] = {}
        self.inspection_results: Dict[str, InspectionResult] = {}
        self.process_parameters: Dict[str, ProcessParameter] = {}
        self.quality_alerts: Dict[str, QualityAlert] = {}
        self.quality_trends: Dict[str, QualityTrend] = {}
        
        # Quality standards
        self.quality_standards = {
            ProductCategory.ELECTRONICS: {
                "dimension_tolerance": 0.01,
                "surface_roughness": 1.6,
                "electrical_resistance": 0.05,
                "temperature_range": (-40, 85)
            },
            ProductCategory.AUTOMOTIVE: {
                "dimension_tolerance": 0.05,
                "surface_roughness": 3.2,
                "strength_test": 500,
                "corrosion_resistance": 1000
            },
            ProductCategory.MEDICAL: {
                "dimension_tolerance": 0.001,
                "surface_roughness": 0.8,
                "sterility": 100,
                "biocompatibility": 95
            }
        }
        
        # Inspection points configuration
        self.inspection_points = self._initialize_inspection_points()
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_inspection_points(self) -> List[InspectionPoint]:
        """Initialize inspection points configuration"""
        return [
            InspectionPoint("IP_001", ProductionStage.RAW_MATERIAL, "Material verification", "visual", "each_batch", True),
            InspectionPoint("IP_002", ProductionStage.PROCESSING, "Dimensional check", "measurement", "each_unit", True),
            InspectionPoint("IP_003", ProductionStage.PROCESSING, "Surface quality", "visual", "each_unit", False),
            InspectionPoint("IP_004", ProductionStage.ASSEMBLY, "Assembly verification", "functional", "each_unit", True),
            InspectionPoint("IP_005", ProductionStage.FINISHING, "Surface finish", "visual", "each_unit", False),
            InspectionPoint("IP_006", ProductionStage.FINAL_INSPECTION, "Final quality check", "comprehensive", "each_unit", True),
            InspectionPoint("IP_007", ProductionStage.PACKAGING, "Packaging integrity", "visual", "each_unit", False)
        ]
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo products
        for i in range(100):
            product = self.demo_data.generate_product(
                product_id=f"PROD_{i+1:04d}",
                category=random.choice(list(ProductCategory))
            )
            self.products[product.product_id] = product
        
        # Generate demo inspection results
        for i in range(500):
            inspection = self.demo_data.generate_inspection_result(
                inspection_id=f"INSP_{i+1:04d}",
                product_ids=list(self.products.keys()),
                inspection_points=self.inspection_points
            )
            self.inspection_results[inspection.inspection_id] = inspection
        
        # Generate demo process parameters
        for i in range(25):
            parameter = self.demo_data.generate_process_parameter(
                parameter_id=f"PARAM_{i+1:03d}",
                stages=list(ProductionStage)
            )
            self.process_parameters[parameter.parameter_id] = parameter
        
        # Generate quality alerts
        self._generate_quality_alerts()
        
        # Generate quality trends
        self._generate_quality_trends()
        
        logger.info(f"Initialized demo data: {len(self.products)} products, "
                   f"{len(self.inspection_results)} inspections, {len(self.process_parameters)} parameters")
    
    def _generate_quality_alerts(self):
        """Generate sample quality alerts"""
        alert_types = ["defect_rate", "parameter_drift", "process_variation", "equipment_malfunction"]
        
        for i in range(15):
            alert = QualityAlert(
                alert_id=f"ALERT_{i+1:03d}",
                alert_type=random.choice(alert_types),
                severity=random.choice([QualityLevel.ACCEPTABLE, QualityLevel.DEFECTIVE, QualityLevel.REJECT]),
                description=self._generate_alert_description(),
                product_id=random.choice(list(self.products.keys())) if random.random() > 0.5 else None,
                process_parameter=random.choice(list(self.process_parameters.keys())) if random.random() > 0.7 else None,
                timestamp=datetime.now() - timedelta(hours=random.randint(1, 72)),
                acknowledged=random.choice([True, True, False]),
                resolved=random.choice([True, True, True, False])
            )
            
            self.quality_alerts[alert.alert_id] = alert
    
    def _generate_alert_description(self) -> str:
        """Generate alert description"""
        descriptions = [
            "Defect rate exceeded threshold in assembly line",
            "Temperature parameter drifting from target",
            "Surface finish quality below standard",
            "Dimensional tolerance violation detected",
            "Equipment calibration drift detected",
            "Material quality deviation in batch",
            "Process cycle time variation increased",
            "Visual inspection failure rate elevated"
        ]
        return random.choice(descriptions)
    
    def _generate_quality_trends(self):
        """Generate quality trend analyses"""
        metric_names = ["defect_rate", "first_pass_yield", "cycle_time", "parameter_precision", "customer_satisfaction"]
        time_periods = ["daily", "weekly", "monthly"]
        
        for metric in metric_names:
            for period in time_periods:
                trend = QualityTrend(
                    analysis_id=f"TREND_{metric}_{period}",
                    metric_name=metric,
                    time_period=period,
                    trend_direction=random.choice(["improving", "stable", "declining"]),
                    trend_strength=random.uniform(0.1, 0.9),
                    predicted_value=random.uniform(0.8, 0.98),
                    recommendations=self._generate_trend_recommendations(metric),
                    analysis_date=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                
                self.quality_trends[trend.analysis_id] = trend
    
    def _generate_trend_recommendations(self, metric: str) -> List[str]:
        """Generate trend-based recommendations"""
        recommendations_map = {
            "defect_rate": [
                "Investigate root cause of defects",
                "Review operator training programs",
                "Check equipment calibration status",
                "Implement additional quality checks"
            ],
            "first_pass_yield": [
                "Optimize process parameters",
                "Reduce process variation",
                "Improve operator skill levels",
                "Update standard operating procedures"
            ],
            "cycle_time": [
                "Identify process bottlenecks",
                "Optimize material handling",
                "Upgrade equipment performance",
                "Streamline workflow processes"
            ],
            "parameter_precision": [
                "Recalibrate measurement equipment",
                "Review environmental controls",
                "Update measurement procedures",
                "Implement statistical process control"
            ],
            "customer_satisfaction": [
                "Improve product quality consistency",
                "Enhance customer service response",
                "Address product feature requests",
                "Strengthen quality feedback loop"
            ]
        }
        
        return random.sample(recommendations_map.get(metric, []), random.randint(1, 3))
    
    async def perform_quality_inspection(self, product_id: str, inspection_point: str) -> InspectionResult:
        """Perform AI-powered quality inspection"""
        try:
            product = self.products.get(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")
            
            # Prepare inspection context
            inspection_context = {
                "product_info": product.dict(),
                "inspection_point": inspection_point,
                "historical_data": self._get_product_history(product_id),
                "process_parameters": self._get_current_process_parameters(),
                "quality_standards": self.quality_standards.get(product.category, {})
            }
            
            # Use Brain AI to analyze quality inspection
            ai_analysis = await self.brain_ai.process_quality_inspection(inspection_context)
            
            # Generate inspection measurements
            measurements = self._generate_inspection_measurements(product, inspection_point)
            
            # Detect defects using AI
            defects = self._detect_defects(product, inspection_point, measurements)
            
            # Determine overall quality level
            quality_level = self._determine_quality_level(measurements, defects)
            
            # Generate quality assessment
            inspection = InspectionResult(
                inspection_id=f"INSP_{len(self.inspection_results)+1:04d}",
                product_id=product_id,
                inspection_point=inspection_point,
                inspector="AI_System",
                timestamp=datetime.now(),
                quality_level=quality_level,
                defects=defects,
                measurements=measurements,
                images=self._generate_mock_inspection_images(),
                notes=self._generate_inspection_notes(quality_level, defects),
                actions_taken=self._suggest_actions(quality_level, defects),
                ai_confidence=0.92
            )
            
            # Store in memory for future reference
            await self.brain_ai.store_inspection_result(inspection.inspection_id, inspection.dict())
            
            self.inspection_results[inspection.inspection_id] = inspection
            
            # Generate alert if quality issues detected
            if quality_level in [QualityLevel.DEFECTIVE, QualityLevel.REJECT]:
                await self._generate_quality_alert(product_id, inspection_point, quality_level, defects)
            
            logger.info(f"Performed inspection {inspection.inspection_id} for product {product_id}, quality: {quality_level.value}")
            
            return inspection
            
        except Exception as e:
            logger.error(f"Error performing quality inspection: {str(e)}")
            raise
    
    def _get_product_history(self, product_id: str) -> Dict:
        """Get product inspection history"""
        product_inspections = [r for r in self.inspection_results.values() if r.product_id == product_id]
        
        return {
            "total_inspections": len(product_inspections),
            "defect_count": len([r for r in product_inspections if r.quality_level in [QualityLevel.DEFECTIVE, QualityLevel.REJECT]]),
            "average_quality": self._calculate_average_quality(product_inspections),
            "last_inspection": max([r.timestamp for r in product_inspections]) if product_inspections else None
        }
    
    def _get_current_process_parameters(self) -> List[ProcessParameter]:
        """Get current process parameter values"""
        return list(self.process_parameters.values())
    
    def _generate_inspection_measurements(self, product: Product, inspection_point: str) -> List[QualityMetric]:
        """Generate inspection measurements"""
        measurements = []
        
        # Get quality standards for product category
        standards = self.quality_standards.get(product.category, {})
        
        # Generate relevant measurements based on inspection point
        if inspection_point == "IP_002":  # Dimensional check
            measurements.append(QualityMetric(
                metric_name="length",
                value=random.uniform(95, 105),
                target=100,
                tolerance=standards.get("dimension_tolerance", 0.01),
                unit="mm",
                status=QualityLevel.GOOD
            ))
            measurements.append(QualityMetric(
                metric_name="width",
                value=random.uniform(47.5, 52.5),
                target=50,
                tolerance=standards.get("dimension_tolerance", 0.01),
                unit="mm",
                status=QualityLevel.GOOD
            ))
        
        elif inspection_point == "IP_003":  # Surface quality
            measurements.append(QualityMetric(
                metric_name="surface_roughness",
                value=random.uniform(0.5, 2.5),
                target=1.6,
                tolerance=standards.get("surface_roughness", 1.6),
                unit="μm",
                status=QualityLevel.GOOD
            ))
        
        elif inspection_point == "IP_006":  # Final inspection
            measurements.extend([
                QualityMetric("overall_quality", 0.95, 0.98, 0.02, "score", QualityLevel.GOOD),
                QualityMetric("visual_inspection", 0.92, 0.95, 0.03, "score", QualityLevel.GOOD),
                QualityMetric("functional_test", 0.98, 0.99, 0.01, "score", QualityLevel.EXCELLENT)
            ])
        
        return measurements
    
    def _detect_defects(self, product: Product, inspection_point: str, measurements: List[QualityMetric]) -> List[Dict]:
        """Detect defects using AI analysis"""
        defects = []
        
        # Check measurements for out-of-tolerance conditions
        for measurement in measurements:
            if measurement.status in [QualityLevel.DEFECTIVE, QualityLevel.REJECT]:
                defect = {
                    "defect_type": self._map_measurement_to_defect_type(measurement.metric_name),
                    "severity": measurement.status.value,
                    "description": f"{measurement.metric_name} out of tolerance",
                    "measurement": measurement.value,
                    "target": measurement.target,
                    "tolerance": measurement.tolerance
                }
                defects.append(defect)
        
        # Add random defects based on inspection point
        if random.random() < 0.1:  # 10% chance of additional defects
            additional_defect = {
                "defect_type": random.choice(list(DefectType)).value,
                "severity": random.choice([QualityLevel.ACCEPTABLE, QualityLevel.DEFECTIVE]).value,
                "description": "Visual defect detected",
                "location": f"Area {random.randint(1, 10)}",
                "size": f"{random.uniform(0.1, 2.0):.1f}mm"
            }
            defects.append(additional_defect)
        
        return defects
    
    def _map_measurement_to_defect_type(self, metric_name: str) -> str:
        """Map measurement to defect type"""
        mapping = {
            "length": DefectType.DIMENSION.value,
            "width": DefectType.DIMENSION.value,
            "surface_roughness": DefectType.SURFACE.value,
            "overall_quality": DefectType.FUNCTIONAL.value
        }
        return mapping.get(metric_name, DefectType.SURFACE.value)
    
    def _determine_quality_level(self, measurements: List[QualityMetric], defects: List[Dict]) -> QualityLevel:
        """Determine overall quality level"""
        # Count defects by severity
        severe_defects = len([d for d in defects if d.get("severity") == QualityLevel.REJECT.value])
        moderate_defects = len([d for d in defects if d.get("severity") == QualityLevel.DEFECTIVE.value])
        minor_defects = len([d for d in defects if d.get("severity") == QualityLevel.ACCEPTABLE.value])
        
        # Check measurement failures
        measurement_failures = len([m for m in measurements if m.status in [QualityLevel.DEFECTIVE, QualityLevel.REJECT]])
        
        # Determine quality level
        if severe_defects > 0 or measurement_failures > 2:
            return QualityLevel.REJECT
        elif moderate_defects > 0 or measurement_failures > 0:
            return QualityLevel.DEFECTIVE
        elif minor_defects > 0:
            return QualityLevel.ACCEPTABLE
        elif all(m.status == QualityLevel.EXCELLENT for m in measurements):
            return QualityLevel.EXCELLENT
        else:
            return QualityLevel.GOOD
    
    def _generate_mock_inspection_images(self) -> List[str]:
        """Generate mock inspection images (base64 encoded)"""
        # In a real implementation, this would contain actual inspection images
        # For demo purposes, return empty list or mock base64 data
        return []
    
    def _generate_inspection_notes(self, quality_level: QualityLevel, defects: List[Dict]) -> str:
        """Generate inspection notes"""
        if quality_level == QualityLevel.EXCELLENT:
            return "Product meets all quality specifications. No defects detected."
        elif quality_level == QualityLevel.GOOD:
            return "Product meets quality standards with minor variations within acceptable limits."
        elif quality_level == QualityLevel.ACCEPTABLE:
            return "Product has minor defects but remains within acceptable quality range."
        elif quality_level == QualityLevel.DEFECTIVE:
            return "Product contains defects that require attention. Review recommended."
        else:
            return "Product has significant defects and does not meet quality standards. Rejection recommended."
    
    def _suggest_actions(self, quality_level: QualityLevel, defects: List[Dict]) -> List[str]:
        """Suggest corrective actions"""
        actions = []
        
        if quality_level == QualityLevel.REJECT:
            actions.extend([
                "Reject product immediately",
                "Quarantine batch for investigation",
                "Review process parameters",
                "Update quality procedures"
            ])
        elif quality_level == QualityLevel.DEFECTIVE:
            actions.extend([
                "Perform detailed defect analysis",
                "Adjust process parameters",
                "Retrain operators",
                "Implement additional quality checks"
            ])
        elif quality_level == QualityLevel.ACCEPTABLE:
            actions.extend([
                "Monitor similar products closely",
                "Review process consistency",
                "Consider preventive maintenance"
            ])
        else:
            actions.append("Continue normal production")
        
        return actions
    
    def _calculate_average_quality(self, inspections: List[InspectionResult]) -> float:
        """Calculate average quality score from inspections"""
        if not inspections:
            return 1.0
        
        quality_scores = {
            QualityLevel.EXCELLENT: 1.0,
            QualityLevel.GOOD: 0.9,
            QualityLevel.ACCEPTABLE: 0.7,
            QualityLevel.DEFECTIVE: 0.4,
            QualityLevel.REJECT: 0.0
        }
        
        total_score = sum(quality_scores[i.quality_level] for i in inspections)
        return total_score / len(inspections)
    
    async def _generate_quality_alert(self, product_id: str, inspection_point: str, 
                                    quality_level: QualityLevel, defects: List[Dict]):
        """Generate quality alert for defects"""
        alert = QualityAlert(
            alert_id=f"ALERT_{len(self.quality_alerts)+1:03d}",
            alert_type="quality_failure",
            severity=quality_level,
            description=f"Quality failure detected in product {product_id} at {inspection_point}",
            product_id=product_id,
            timestamp=datetime.now(),
            acknowledged=False,
            resolved=False
        )
        
        self.quality_alerts[alert.alert_id] = alert
        logger.warning(f"Generated quality alert: {alert.description}")
    
    def analyze_quality_trends(self, metric_name: str = "defect_rate") -> Dict:
        """Analyze quality trends and provide insights"""
        try:
            # Get recent inspection data
            recent_inspections = [r for r in self.inspection_results.values() 
                                if r.timestamp >= datetime.now() - timedelta(days=30)]
            
            # Calculate trend metrics
            trend_data = self._calculate_trend_metrics(recent_inspections, metric_name)
            
            # Generate insights
            insights = self._generate_quality_insights(trend_data)
            
            # Predict future trends
            predictions = self._predict_quality_trends(trend_data)
            
            # Generate recommendations
            recommendations = self._generate_quality_recommendations(trend_data, insights)
            
            return {
                "metric_name": metric_name,
                "current_value": trend_data["current"],
                "trend_direction": trend_data["direction"],
                "trend_strength": trend_data["strength"],
                "insights": insights,
                "predictions": predictions,
                "recommendations": recommendations,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing quality trends: {str(e)}")
            raise
    
    def _calculate_trend_metrics(self, inspections: List[InspectionResult], metric_name: str) -> Dict:
        """Calculate trend metrics from inspection data"""
        if metric_name == "defect_rate":
            total_inspections = len(inspections)
            defective_inspections = len([r for r in inspections 
                                      if r.quality_level in [QualityLevel.DEFECTIVE, QualityLevel.REJECT]])
            current_rate = defective_inspections / total_inspections if total_inspections > 0 else 0
        elif metric_name == "first_pass_yield":
            total_inspections = len(inspections)
            passed_inspections = len([r for r in inspections 
                                    if r.quality_level in [QualityLevel.EXCELLENT, QualityLevel.GOOD]])
            current_rate = passed_inspections / total_inspections if total_inspections > 0 else 0
        else:
            current_rate = random.uniform(0.8, 0.98)  # Default for other metrics
        
        # Calculate trend direction (simplified)
        direction = random.choice(["improving", "stable", "declining"])
        strength = random.uniform(0.1, 0.9)
        
        return {
            "current": current_rate,
            "direction": direction,
            "strength": strength,
            "sample_size": len(inspections)
        }
    
    def _generate_quality_insights(self, trend_data: Dict) -> List[str]:
        """Generate quality insights"""
        insights = []
        
        current = trend_data["current"]
        direction = trend_data["direction"]
        strength = trend_data["strength"]
        
        if direction == "improving" and strength > 0.7:
            insights.append("Quality performance is significantly improving")
        elif direction == "declining" and strength > 0.7:
            insights.append("Quality performance is deteriorating - immediate attention required")
        elif direction == "stable":
            insights.append("Quality performance is stable")
        
        if current < 0.8:
            insights.append("Quality levels are below acceptable threshold")
        elif current > 0.95:
            insights.append("Quality performance is excellent")
        
        return insights
    
    def _predict_quality_trends(self, trend_data: Dict) -> Dict:
        """Predict future quality trends"""
        current = trend_data["current"]
        direction = trend_data["direction"]
        strength = trend_data["strength"]
        
        # Simple prediction based on trend
        if direction == "improving":
            predicted = min(current + (strength * 0.1), 1.0)
        elif direction == "declining":
            predicted = max(current - (strength * 0.1), 0.0)
        else:
            predicted = current
        
        return {
            "predicted_value": predicted,
            "confidence": 0.85,
            "prediction_period": "30_days"
        }
    
    def _generate_quality_recommendations(self, trend_data: Dict, insights: List[str]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        current = trend_data["current"]
        direction = trend_data["direction"]
        
        if direction == "declining":
            recommendations.extend([
                "Investigate root causes of quality decline",
                "Review process parameters and controls",
                "Conduct operator training review",
                "Implement additional quality checks"
            ])
        elif direction == "improving":
            recommendations.extend([
                "Document best practices",
                "Share improvements across production lines",
                "Continue monitoring performance",
                "Consider process optimization"
            ])
        else:
            recommendations.extend([
                "Maintain current quality practices",
                "Monitor for early warning signs",
                "Consider incremental improvements"
            ])
        
        if current < 0.8:
            recommendations.append("Implement immediate quality improvement plan")
        
        return recommendations
    
    def get_quality_dashboard(self) -> Dict:
        """Generate comprehensive quality dashboard"""
        try:
            # Calculate key quality metrics
            total_products = len(self.products)
            total_inspections = len(self.inspection_results)
            
            # Quality distribution
            quality_distribution = {}
            for level in QualityLevel:
                count = len([r for r in self.inspection_results.values() if r.quality_level == level])
                quality_distribution[level.value] = {
                    "count": count,
                    "percentage": (count / total_inspections * 100) if total_inspections > 0 else 0
                }
            
            # Defect analysis
            all_defects = []
            for inspection in self.inspection_results.values():
                all_defects.extend(inspection.defects)
            
            defect_types = {}
            for defect in all_defects:
                defect_type = defect.get("defect_type", "unknown")
                defect_types[defect_type] = defect_types.get(defect_type, 0) + 1
            
            # Process parameter status
            parameter_status = {}
            for level in QualityLevel:
                count = len([p for p in self.process_parameters.values() if p.status == level])
                parameter_status[level.value] = count
            
            # Quality trends
            quality_trends = self._get_quality_trends_summary()
            
            # Alerts summary
            active_alerts = len([a for a in self.quality_alerts.values() if not a.resolved])
            critical_alerts = len([a for a in self.quality_alerts.values() 
                                 if a.severity == QualityLevel.REJECT and not a.resolved])
            
            return {
                "overview": {
                    "total_products": total_products,
                    "total_inspections": total_inspections,
                    "first_pass_yield": self._calculate_first_pass_yield(),
                    "defect_rate": self._calculate_defect_rate()
                },
                "quality_distribution": quality_distribution,
                "defect_analysis": {
                    "total_defects": len(all_defects),
                    "defect_types": defect_types,
                    "top_defects": sorted(defect_types.items(), key=lambda x: x[1], reverse=True)[:5]
                },
                "process_parameters": {
                    "total_parameters": len(self.process_parameters),
                    "status_distribution": parameter_status,
                    "out_of_control": len([p for p in self.process_parameters.values() 
                                         if p.status in [QualityLevel.DEFECTIVE, QualityLevel.REJECT]])
                },
                "quality_trends": quality_trends,
                "alerts": {
                    "active_alerts": active_alerts,
                    "critical_alerts": critical_alerts,
                    "recent_alerts": [a.__dict__ for a in list(self.quality_alerts.values())[-5:]]
                },
                "performance_metrics": self._calculate_performance_metrics(),
                "recommendations": self._generate_dashboard_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating quality dashboard: {str(e)}")
            raise
    
    def _calculate_first_pass_yield(self) -> float:
        """Calculate first pass yield percentage"""
        total_inspections = len(self.inspection_results)
        passed_inspections = len([r for r in self.inspection_results.values() 
                                if r.quality_level in [QualityLevel.EXCELLENT, QualityLevel.GOOD]])
        
        return (passed_inspections / total_inspections * 100) if total_inspections > 0 else 0
    
    def _calculate_defect_rate(self) -> float:
        """Calculate defect rate percentage"""
        total_inspections = len(self.inspection_results)
        defective_inspections = len([r for r in self.inspection_results.values() 
                                   if r.quality_level in [QualityLevel.DEFECTIVE, QualityLevel.REJECT]])
        
        return (defective_inspections / total_inspections * 100) if total_inspections > 0 else 0
    
    def _get_quality_trends_summary(self) -> Dict:
        """Get quality trends summary"""
        return {
            "defect_rate_trend": random.choice(["improving", "stable", "declining"]),
            "first_pass_yield_trend": random.choice(["improving", "stable", "declining"]),
            "cycle_time_trend": random.choice(["improving", "stable", "declining"]),
            "overall_trend": random.choice(["improving", "stable", "declining"])
        }
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        return {
            "inspection_efficiency": random.uniform(85, 98),
            "detection_accuracy": random.uniform(90, 99),
            "false_positive_rate": random.uniform(1, 5),
            "process_capability": random.uniform(1.2, 2.0),
            "customer_satisfaction": random.uniform(85, 95)
        }
    
    def _generate_dashboard_recommendations(self) -> List[str]:
        """Generate dashboard recommendations"""
        recommendations = [
            "Monitor defect rate trends closely",
            "Review process parameters for optimization",
            "Implement predictive maintenance",
            "Enhance operator training programs"
        ]
        
        # Add contextual recommendations based on current state
        defect_rate = self._calculate_defect_rate()
        if defect_rate > 5:
            recommendations.append("Immediate quality improvement plan required")
        
        return recommendations

# FastAPI Application
app = FastAPI(title="Smart Quality Control", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
qc_ai = SmartQualityControlAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=qc_ai.web_components.render_quality_dashboard())

@app.get("/api/products")
async def get_products():
    """Get all products"""
    return {"products": list(qc_ai.products.values())}

@app.get("/api/inspections")
async def get_inspections():
    """Get all inspection results"""
    return {"inspections": list(qc_ai.inspection_results.values())}

@app.post("/api/inspections/{product_id}/{inspection_point}")
async def perform_inspection(product_id: str, inspection_point: str):
    """Perform quality inspection"""
    try:
        inspection = await qc_ai.perform_quality_inspection(product_id, inspection_point)
        return inspection.dict()
    except Exception as e:
        logger.error(f"Error performing inspection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quality-trends")
async def get_quality_trends():
    """Get quality trend analysis"""
    try:
        trend_analysis = qc_ai.analyze_quality_trends()
        return trend_analysis
    except Exception as e:
        logger.error(f"Error analyzing quality trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quality-dashboard")
async def get_quality_dashboard():
    """Get quality dashboard data"""
    try:
        dashboard_data = qc_ai.get_quality_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting quality dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/process-parameters")
async def get_process_parameters():
    """Get all process parameters"""
    return {"parameters": list(qc_ai.process_parameters.values())}

@app.get("/api/quality-alerts")
async def get_quality_alerts():
    """Get all quality alerts"""
    return {"alerts": list(qc_ai.quality_alerts.values())}

@app.get("/api/inspection-points")
async def get_inspection_points():
    """Get inspection points configuration"""
    return {"points": [point.__dict__ for point in qc_ai.inspection_points]}

@app.post("/api/demo/generate-inspection")
async def generate_demo_inspection():
    """Generate a random demo inspection for testing"""
    product_ids = list(qc_ai.products.keys())
    if not product_ids:
        raise HTTPException(status_code=404, detail="No products available for inspection")
    
    product_id = random.choice(product_ids)
    inspection_point = random.choice(qc_ai.inspection_points).point_id
    
    inspection = await qc_ai.perform_quality_inspection(product_id, inspection_point)
    return {"inspection": inspection.dict(), "product_id": product_id, "inspection_point": inspection_point}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Smart Quality Control...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")