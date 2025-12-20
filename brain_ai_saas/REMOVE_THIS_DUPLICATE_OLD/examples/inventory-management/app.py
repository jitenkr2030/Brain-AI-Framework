"""
Inventory Management - Brain AI Framework Example
A comprehensive inventory management system that helps organizations optimize inventory levels,
predict demand, manage supply chain operations using Brain AI Framework.
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
logger.add("logs/inventory_management.log", rotation="10 MB", level="INFO")

class ProductCategory(Enum):
    """Product category enumeration"""
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME_GARDEN = "home_garden"
    OFFICE_SUPPLIES = "office_supplies"
    FOOD_BEVERAGE = "food_beverage"
    HEALTH_BEAUTY = "health_beauty"
    AUTOMOTIVE = "automotive"
    TOYS_GAMES = "toys_games"
    SPORTS_OUTDOOR = "sports_outdoor"
    BOOKS_MEDIA = "books_media"

class WarehouseLocation(Enum):
    """Warehouse location enumeration"""
    WAREHOUSE_A = "warehouse_a"
    WAREHOUSE_B = "warehouse_b"
    WAREHOUSE_C = "warehouse_c"
    DISTRIBUTION_CENTER = "distribution_center"
    RETAIL_STORE = "retail_store"

class InventoryStatus(Enum):
    """Inventory status enumeration"""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    OVERSTOCK = "overstock"
    DISCONTINUED = "discontinued"
    SEASONAL = "seasonal"

class SupplierType(Enum):
    """Supplier type enumeration"""
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    WHOLESALER = "wholesaler"
    DROPSHIP = "dropship"
    LOCAL = "local"

class DemandForecastType(Enum):
    """Demand forecast type enumeration"""
    SEASONAL = "seasonal"
    TREND = "trend"
    CYCLICAL = "cyclical"
    PROMOTIONAL = "promotional"
    EXTERNAL_FACTOR = "external_factor"

@dataclass
class InventoryMovement:
    """Inventory movement data"""
    movement_id: str
    product_id: str
    movement_type: str  # in, out, transfer, adjustment
    quantity: int
    unit_cost: float
    total_cost: float
    location: WarehouseLocation
    timestamp: datetime
    reference: str
    notes: str

@dataclass
class SupplierMetrics:
    """Supplier performance metrics"""
    supplier_id: str
    on_time_delivery_rate: float
    quality_score: float
    cost_competitiveness: float
    responsiveness: float
    reliability_score: float
    last_evaluation: datetime

class InventoryItem(BaseModel):
    """Inventory item model"""
    product_id: str
    name: str
    description: str
    category: ProductCategory
    sku: str
    barcode: str
    current_stock: int
    minimum_stock: int
    maximum_stock: int
    reorder_point: int
    reorder_quantity: int
    unit_cost: float
    unit_price: float
    supplier_id: str
    location: WarehouseLocation
    status: InventoryStatus
    last_restocked: datetime
    expiry_date: Optional[datetime]
    batch_number: Optional[str]
    specifications: Dict[str, Any]

class StockMovement(BaseModel):
    """Stock movement model"""
    movement_id: str
    product_id: str
    movement_type: str
    quantity: int
    unit_cost: float
    total_cost: float
    location: WarehouseLocation
    timestamp: datetime
    reference: str
    user_id: str
    notes: str

class DemandForecast(BaseModel):
    """Demand forecast model"""
    forecast_id: str
    product_id: str
    forecast_type: DemandForecastType
    forecast_period: str
    predicted_demand: int
    confidence_level: float
    factors: List[str]
    generated_date: datetime
    valid_until: datetime

class Supplier(BaseModel):
    """Supplier model"""
    supplier_id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: Dict[str, str]
    supplier_type: SupplierType
    payment_terms: str
    lead_time_days: int
    minimum_order_quantity: int
    quality_rating: float
    reliability_rating: float
    metrics: SupplierMetrics
    contract_expiry: datetime

class ReorderRecommendation(BaseModel):
    """Reorder recommendation model"""
    recommendation_id: str
    product_id: str
    current_stock: int
    predicted_demand: int
    recommended_quantity: int
    reorder_date: datetime
    priority_level: str
    reasoning: str
    estimated_cost: float
    supplier_id: str
    generated_date: datetime

class InventoryAlert(BaseModel):
    """Inventory alert model"""
    alert_id: str
    product_id: str
    alert_type: str
    severity: str
    current_stock: int
    threshold: int
    message: str
    location: WarehouseLocation
    created_date: datetime
    acknowledged: bool
    resolved: bool

class InventoryAI:
    """Main inventory management AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.inventory_items: Dict[str, InventoryItem] = {}
        self.stock_movements: Dict[str, StockMovement] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.demand_forecasts: Dict[str, DemandForecast] = {}
        self.reorder_recommendations: Dict[str, ReorderRecommendation] = {}
        self.inventory_alerts: Dict[str, InventoryAlert] = {}
        
        # Inventory management configuration
        self.inventory_config = {
            "safety_stock_days": 7,
            "reorder_point_buffer": 1.5,
            "demand_variability_factor": 1.2,
            "seasonal_adjustment": True,
            "abc_analysis_enabled": True,
            "fifo_enabled": True
        }
        
        # Warehouse configurations
        self.warehouse_configs = self._initialize_warehouse_configs()
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_warehouse_configs(self) -> Dict:
        """Initialize warehouse-specific configurations"""
        return {
            WarehouseLocation.WAREHOUSE_A: {
                "capacity": 10000,
                "utilization": 0.75,
                "specialization": "electronics",
                "temperature_controlled": False
            },
            WarehouseLocation.WAREHOUSE_B: {
                "capacity": 8000,
                "utilization": 0.65,
                "specialization": "clothing",
                "temperature_controlled": False
            },
            WarehouseLocation.WAREHOUSE_C: {
                "capacity": 12000,
                "utilization": 0.80,
                "specialization": "general",
                "temperature_controlled": True
            },
            WarehouseLocation.DISTRIBUTION_CENTER: {
                "capacity": 15000,
                "utilization": 0.70,
                "specialization": "mixed",
                "temperature_controlled": True
            }
        }
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo suppliers
        for i in range(25):
            supplier = self.demo_data.generate_supplier(
                supplier_id=f"SUP_{i+1:03d}"
            )
            self.suppliers[supplier.supplier_id] = supplier
        
        # Generate demo inventory items
        for i in range(300):
            item = self.demo_data.generate_inventory_item(
                product_id=f"ITEM_{i+1:04d}",
                category=random.choice(list(ProductCategory)),
                supplier_ids=list(self.suppliers.keys())
            )
            self.inventory_items[item.product_id] = item
        
        # Generate demo stock movements
        for i in range(1000):
            movement = self.demo_data.generate_stock_movement(
                movement_id=f"MOVE_{i+1:04d}",
                product_ids=list(self.inventory_items.keys()),
                locations=list(WarehouseLocation)
            )
            self.stock_movements[movement.movement_id] = movement
        
        # Generate demand forecasts
        self._generate_demand_forecasts()
        
        # Generate reorder recommendations
        self._generate_reorder_recommendations()
        
        # Generate inventory alerts
        self._generate_inventory_alerts()
        
        logger.info(f"Initialized demo data: {len(self.inventory_items)} items, "
                   f"{len(self.stock_movements)} movements, {len(self.suppliers)} suppliers")
    
    def _generate_demand_forecasts(self):
        """Generate demand forecasts for products"""
        forecast_types = [DemandForecastType.SEASONAL, DemandForecastType.TREND, 
                         DemandForecastType.CYCLICAL, DemandForecastType.PROMOTIONAL]
        
        for product_id in list(self.inventory_items.keys())[:100]:  # Generate for 100 products
            forecast_type = random.choice(forecast_types)
            
            # Calculate predicted demand based on product characteristics
            item = self.inventory_items[product_id]
            base_demand = self._calculate_base_demand(item)
            
            forecast = DemandForecast(
                forecast_id=f"FC_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                product_id=product_id,
                forecast_type=forecast_type,
                forecast_period="30_days",
                predicted_demand=base_demand,
                confidence_level=random.uniform(0.7, 0.95),
                factors=self._generate_forecast_factors(forecast_type),
                generated_date=datetime.now(),
                valid_until=datetime.now() + timedelta(days=30)
            )
            
            self.demand_forecasts[forecast.forecast_id] = forecast
    
    def _calculate_base_demand(self, item: InventoryItem) -> int:
        """Calculate base demand for an item"""
        # Category-based demand factors
        category_demand_factors = {
            ProductCategory.FOOD_BEVERAGE: 50,      # High demand
            ProductCategory.OFFICE_SUPPLIES: 30,    # Medium demand
            ProductCategory.ELECTRONICS: 20,        # Medium demand
            ProductCategory.CLOTHING: 25,           # Medium demand
            ProductCategory.HOME_GARDEN: 15,        # Low-medium demand
        }
        
        base_factor = category_demand_factors.get(item.category, 20)
        
        # Adjust for inventory level
        if item.current_stock < item.minimum_stock:
            base_factor *= 1.5  # Higher demand when low stock
        elif item.current_stock > item.maximum_stock:
            base_factor *= 0.7  # Lower demand when overstocked
        
        return int(base_factor * random.uniform(0.8, 1.3))
    
    def _generate_forecast_factors(self, forecast_type: DemandForecastType) -> List[str]:
        """Generate factors affecting the forecast"""
        factor_map = {
            DemandForecastType.SEASONAL: ["holiday_season", "weather_patterns", "seasonal_trends"],
            DemandForecastType.TREND: ["market_growth", "customer_preferences", "product_lifecycle"],
            DemandForecastType.CYCLICAL: ["economic_cycles", "business_cycles", "market_cycles"],
            DemandForecastType.PROMOTIONAL: ["marketing_campaigns", "price_promotions", "new_product_launch"],
            DemandForecastType.EXTERNAL_FACTOR: ["competitor_actions", "supply_chain_issues", "regulatory_changes"]
        }
        
        return factor_map.get(forecast_type, ["general_market_conditions"])
    
    def _generate_reorder_recommendations(self):
        """Generate reorder recommendations"""
        for product_id, item in self.inventory_items.items():
            # Check if reorder is needed
            if item.current_stock <= item.reorder_point:
                # Calculate recommended quantity
                forecasted_demand = self._get_forecasted_demand(product_id)
                recommended_qty = self._calculate_reorder_quantity(item, forecasted_demand)
                
                # Find best supplier
                supplier_id = self._find_best_supplier(item.supplier_id, item.category)
                
                recommendation = ReorderRecommendation(
                    recommendation_id=f"REO_{product_id}_{datetime.now().strftime('%Y%m%d')}",
                    product_id=product_id,
                    current_stock=item.current_stock,
                    predicted_demand=forecasted_demand,
                    recommended_quantity=recommended_qty,
                    reorder_date=datetime.now() + timedelta(days=1),
                    priority_level=self._determine_priority_level(item),
                    reasoning=self._generate_reorder_reasoning(item, forecasted_demand),
                    estimated_cost=recommended_qty * item.unit_cost,
                    supplier_id=supplier_id,
                    generated_date=datetime.now()
                )
                
                self.reorder_recommendations[recommendation.recommendation_id] = recommendation
    
    def _get_forecasted_demand(self, product_id: str) -> int:
        """Get forecasted demand for a product"""
        forecasts = [f for f in self.demand_forecasts.values() if f.product_id == product_id]
        if forecasts:
            # Return average of available forecasts
            return int(sum(f.predicted_demand for f in forecasts) / len(forecasts))
        return 0
    
    def _calculate_reorder_quantity(self, item: InventoryItem, forecasted_demand: int) -> int:
        """Calculate optimal reorder quantity"""
        # Economic Order Quantity (EOQ) simplified calculation
        annual_demand = forecasted_demand * 12
        ordering_cost = 50  # Fixed ordering cost
        holding_cost_rate = 0.25  # 25% of item cost
        
        eoq = math.sqrt((2 * annual_demand * ordering_cost) / (item.unit_cost * holding_cost_rate))
        
        # Adjust for lead time and safety stock
        lead_time_demand = forecasted_demand * (self.suppliers.get(item.supplier_id, Supplier(
            supplier_id="default", name="Default", contact_person="", email="", phone="",
            address={}, supplier_type=SupplierType.DISTRIBUTOR, payment_terms="",
            lead_time_days=7, minimum_order_quantity=1, quality_rating=1.0,
            reliability_rating=1.0, metrics=SupplierMetrics("", 1.0, 1.0, 1.0, 1.0, 1.0, datetime.now()),
            contract_expiry=datetime.now() + timedelta(days=365)
        )).lead_time_days / 30)
        
        safety_stock = item.minimum_stock * 0.5
        reorder_quantity = max(int(eoq), lead_time_demand + safety_stock, item.reorder_quantity)
        
        return reorder_quantity
    
    def _find_best_supplier(self, current_supplier_id: str, category: ProductCategory) -> str:
        """Find the best supplier for a product"""
        # In a real implementation, this would consider supplier ratings, costs, lead times, etc.
        # For demo, we'll randomly select from available suppliers
        
        category_suppliers = [s for s in self.suppliers.values() 
                             if s.supplier_type in [SupplierType.MANUFACTURER, SupplierType.DISTRIBUTOR]]
        
        if category_suppliers:
            # Prefer current supplier with some randomness
            if random.random() < 0.7 and current_supplier_id in [s.supplier_id for s in category_suppliers]:
                return current_supplier_id
            else:
                return random.choice(category_suppliers).supplier_id
        
        return current_supplier_id
    
    def _determine_priority_level(self, item: InventoryItem) -> str:
        """Determine reorder priority level"""
        if item.current_stock == 0:
            return "critical"
        elif item.current_stock < item.minimum_stock * 0.5:
            return "high"
        elif item.current_stock < item.minimum_stock:
            return "medium"
        else:
            return "low"
    
    def _generate_reorder_reasoning(self, item: InventoryItem, forecasted_demand: int) -> str:
        """Generate reasoning for reorder recommendation"""
        reasoning_templates = [
            f"Stock level ({item.current_stock}) below reorder point ({item.reorder_point})",
            f"Predicted demand of {forecasted_demand} units in next 30 days",
            f"Lead time of {self.suppliers.get(item.supplier_id, self._get_default_supplier()).lead_time_days} days requires immediate action",
            f"Historical consumption patterns suggest {item.current_stock} units insufficient",
            f"Seasonal demand increase expected based on forecast factors"
        ]
        
        return "; ".join(random.sample(reasoning_templates, random.randint(2, 4)))
    
    def _get_default_supplier(self) -> Supplier:
        """Get default supplier for demo purposes"""
        return Supplier(
            supplier_id="default", name="Default Supplier", contact_person="", email="", phone="",
            address={}, supplier_type=SupplierType.DISTRIBUTOR, payment_terms="",
            lead_time_days=7, minimum_order_quantity=1, quality_rating=1.0,
            reliability_rating=1.0, metrics=SupplierMetrics("", 1.0, 1.0, 1.0, 1.0, 1.0, datetime.now()),
            contract_expiry=datetime.now() + timedelta(days=365)
        )
    
    def _generate_inventory_alerts(self):
        """Generate inventory alerts"""
        alert_types = ["low_stock", "out_of_stock", "overstock", "expiring_soon", "slow_moving"]
        
        for product_id, item in self.inventory_items.items():
            # Check for low stock
            if item.current_stock <= item.minimum_stock:
                alert = InventoryAlert(
                    alert_id=f"ALERT_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    product_id=product_id,
                    alert_type="low_stock",
                    severity="high" if item.current_stock == 0 else "medium",
                    current_stock=item.current_stock,
                    threshold=item.minimum_stock,
                    message=f"Stock level ({item.current_stock}) below minimum ({item.minimum_stock})",
                    location=item.location,
                    created_date=datetime.now() - timedelta(hours=random.randint(1, 48)),
                    acknowledged=False,
                    resolved=False
                )
                self.inventory_alerts[alert.alert_id] = alert
            
            # Check for overstock
            elif item.current_stock > item.maximum_stock * 1.5:
                alert = InventoryAlert(
                    alert_id=f"ALERT_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    product_id=product_id,
                    alert_type="overstock",
                    severity="medium",
                    current_stock=item.current_stock,
                    threshold=item.maximum_stock,
                    message=f"Excessive stock level ({item.current_stock}) above maximum ({item.maximum_stock})",
                    location=item.location,
                    created_date=datetime.now() - timedelta(hours=random.randint(1, 24)),
                    acknowledged=False,
                    resolved=False
                )
                self.inventory_alerts[alert.alert_id] = alert
            
            # Check for expiring items
            if item.expiry_date and item.expiry_date <= datetime.now() + timedelta(days=30):
                alert = InventoryAlert(
                    alert_id=f"ALERT_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    product_id=product_id,
                    alert_type="expiring_soon",
                    severity="high",
                    current_stock=item.current_stock,
                    threshold=0,
                    message=f"Product expires on {item.expiry_date.strftime('%Y-%m-%d')}",
                    location=item.location,
                    created_date=datetime.now() - timedelta(hours=random.randint(1, 12)),
                    acknowledged=False,
                    resolved=False
                )
                self.inventory_alerts[alert.alert_id] = alert
    
    async def analyze_inventory_optimization(self, product_id: str = None) -> Dict:
        """Analyze inventory optimization opportunities"""
        try:
            # Prepare analysis context
            if product_id:
                items_to_analyze = {product_id: self.inventory_items[product_id]}
            else:
                items_to_analyze = self.inventory_items
            
            analysis_context = {
                "inventory_items": {pid: item.dict() for pid, item in items_to_analyze.items()},
                "stock_movements": [movement.dict() for movement in list(self.stock_movements.values())[-100:]],
                "demand_forecasts": [forecast.dict() for forecast in self.demand_forecasts.values()],
                "supplier_performance": {sid: supplier.metrics.__dict__ for sid, supplier in self.suppliers.items()},
                "historical_data": self._get_historical_inventory_data()
            }
            
            # Use Brain AI to analyze inventory optimization
            ai_analysis = await self.brain_ai.process_inventory_optimization(analysis_context)
            
            # Generate optimization recommendations
            optimization_opportunities = []
            
            for pid, item in items_to_analyze.items():
                # ABC Analysis
                abc_category = self._perform_abc_analysis(item)
                
                # Stock optimization
                stock_recommendations = self._generate_stock_recommendations(item)
                
                # Demand analysis
                demand_analysis = self._analyze_demand_patterns(pid)
                
                opportunity = {
                    "product_id": pid,
                    "product_name": item.name,
                    "abc_category": abc_category,
                    "current_stock": item.current_stock,
                    "stock_optimization": stock_recommendations,
                    "demand_analysis": demand_analysis,
                    "supplier_recommendations": self._get_supplier_recommendations(item),
                    "cost_optimization": self._calculate_cost_optimization(item)
                }
                
                optimization_opportunities.append(opportunity)
            
            # Calculate overall inventory metrics
            inventory_metrics = self._calculate_inventory_metrics(items_to_analyze)
            
            return {
                "optimization_opportunities": optimization_opportunities,
                "inventory_metrics": inventory_metrics,
                "priority_actions": self._identify_priority_actions(optimization_opportunities),
                "cost_savings_potential": self._calculate_savings_potential(optimization_opportunities),
                "ai_insights": ai_analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing inventory optimization: {str(e)}")
            raise
    
    def _perform_abc_analysis(self, item: InventoryItem) -> str:
        """Perform ABC analysis on inventory item"""
        # Calculate annual usage value
        annual_usage_value = self._calculate_annual_usage_value(item)
        
        # Get all items' usage values for comparison
        all_usage_values = [self._calculate_annual_usage_value(i) for i in self.inventory_items.values()]
        all_usage_values.sort(reverse=True)
        
        # Calculate cumulative percentage
        cumulative_value = 0
        total_value = sum(all_usage_values)
        
        for value in all_usage_values:
            cumulative_value += value
            percentage = (cumulative_value / total_value) * 100
            
            if percentage <= 20:
                return "A"  # High value items
            elif percentage <= 80:
                return "B"  # Medium value items
            else:
                return "C"  # Low value items
        
        return "C"  # Default to C
    
    def _calculate_annual_usage_value(self, item: InventoryItem) -> float:
        """Calculate annual usage value for ABC analysis"""
        # Estimate annual demand based on current stock and turnover
        estimated_annual_demand = item.current_stock * 4  # Assuming quarterly turnover
        return estimated_annual_demand * item.unit_cost
    
    def _generate_stock_recommendations(self, item: InventoryItem) -> Dict:
        """Generate stock level recommendations"""
        current_stock = item.current_stock
        min_stock = item.minimum_stock
        max_stock = item.maximum_stock
        reorder_point = item.reorder_point
        
        recommendations = {
            "status": "optimal",
            "actions": [],
            "adjustments": {}
        }
        
        if current_stock <= 0:
            recommendations["status"] = "critical"
            recommendations["actions"].append("Immediate reorder required")
            recommendations["actions"].append("Consider emergency supplier")
        elif current_stock < min_stock:
            recommendations["status"] = "low"
            recommendations["actions"].append("Schedule reorder within 48 hours")
            recommendations["actions"].append("Review safety stock levels")
        elif current_stock > max_stock * 1.5:
            recommendations["status"] = "overstock"
            recommendations["actions"].append("Consider promotional pricing")
            recommendations["actions"].append("Reduce future order quantities")
        
        # Suggest stock level adjustments
        if current_stock < reorder_point:
            recommended_level = reorder_point * 1.5
            recommendations["adjustments"]["recommended_stock_level"] = recommended_level
            recommendations["adjustments"]["adjustment_amount"] = recommended_level - current_stock
        
        return recommendations
    
    def _analyze_demand_patterns(self, product_id: str) -> Dict:
        """Analyze demand patterns for a product"""
        forecasts = [f for f in self.demand_forecasts.values() if f.product_id == product_id]
        
        if not forecasts:
            return {"pattern": "insufficient_data", "trend": "unknown", "confidence": 0}
        
        # Analyze forecast patterns
        forecast_types = [f.forecast_type for f in forecasts]
        predicted_demands = [f.predicted_demand for f in forecasts]
        avg_demand = sum(predicted_demands) / len(predicted_demands)
        
        # Determine trend
        if len(predicted_demands) >= 2:
            if predicted_demands[-1] > predicted_demands[0] * 1.1:
                trend = "increasing"
            elif predicted_demands[-1] < predicted_demands[0] * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "unknown"
        
        return {
            "pattern": "forecast_based",
            "trend": trend,
            "average_demand": avg_demand,
            "confidence": sum(f.confidence_level for f in forecasts) / len(forecasts),
            "forecast_factors": [f.factors for f in forecasts]
        }
    
    def _get_supplier_recommendations(self, item: InventoryItem) -> Dict:
        """Get supplier-related recommendations"""
        supplier = self.suppliers.get(item.supplier_id)
        
        if not supplier:
            return {"status": "unknown_supplier", "recommendations": ["Review supplier selection"]}
        
        recommendations = {
            "current_supplier": supplier.name,
            "performance_score": (supplier.quality_rating + supplier.reliability_rating) / 2,
            "recommendations": []
        }
        
        # Evaluate supplier performance
        if supplier.metrics.on_time_delivery_rate < 0.8:
            recommendations["recommendations"].append("Review delivery performance with supplier")
        
        if supplier.metrics.quality_score < 0.85:
            recommendations["recommendations"].append("Discuss quality improvement with supplier")
        
        if supplier.lead_time_days > 14:
            recommendations["recommendations"].append("Consider suppliers with shorter lead times")
        
        # Suggest alternative suppliers
        alternative_suppliers = [s for s in self.suppliers.values() 
                               if s.supplier_id != item.supplier_id and s.supplier_type == supplier.supplier_type]
        
        if alternative_suppliers:
            best_alternative = max(alternative_suppliers, 
                                 key=lambda x: (x.quality_rating + x.reliability_rating) / 2)
            recommendations["alternative_supplier"] = best_alternative.name
        
        return recommendations
    
    def _calculate_cost_optimization(self, item: InventoryItem) -> Dict:
        """Calculate cost optimization opportunities"""
        current_value = item.current_stock * item.unit_cost
        
        # Calculate carrying costs (25% of inventory value annually)
        carrying_cost = current_value * 0.25 / 365  # Daily carrying cost
        
        # Calculate ordering costs
        estimated_orders_per_year = max(1, (self._calculate_annual_usage_value(item) / item.unit_cost) / item.reorder_quantity)
        ordering_cost = estimated_orders_per_year * 50  # $50 per order
        
        # Total cost
        total_cost = carrying_cost + ordering_cost
        
        # Optimization potential
        optimization_potential = {
            "current_carrying_cost_daily": carrying_cost,
            "current_ordering_cost_annual": ordering_cost,
            "total_cost_annual": total_cost * 365,
            "optimization_potential": random.uniform(0.05, 0.20) * total_cost * 365,
            "recommendations": []
        }
        
        # Generate cost optimization recommendations
        if carrying_cost > ordering_cost:
            optimization_potential["recommendations"].append("Consider reducing order quantities")
        else:
            optimization_potential["recommendations"].append("Consider increasing order quantities")
        
        if item.current_stock > item.maximum_stock:
            optimization_potential["recommendations"].append("Reduce current stock levels to minimize carrying costs")
        
        return optimization_potential
    
    def _get_historical_inventory_data(self) -> Dict:
        """Get historical inventory data for analysis"""
        # Calculate basic metrics from stock movements
        recent_movements = [m for m in self.stock_movements.values() 
                           if m.timestamp >= datetime.now() - timedelta(days=90)]
        
        if not recent_movements:
            return {"data_points": 0, "analysis_period": "90_days"}
        
        # Calculate movement patterns
        inbound_movements = [m for m in recent_movements if m.movement_type == "in"]
        outbound_movements = [m for m in recent_movements if m.movement_type == "out"]
        
        return {
            "data_points": len(recent_movements),
            "analysis_period": "90_days",
            "total_movements": len(recent_movements),
            "inbound_movements": len(inbound_movements),
            "outbound_movements": len(outbound_movements),
            "average_daily_movements": len(recent_movements) / 90,
            "net_movement_value": sum(m.total_cost for m in inbound_movements) - sum(m.total_cost for m in outbound_movements)
        }
    
    def _calculate_inventory_metrics(self, items: Dict[str, InventoryItem]) -> Dict:
        """Calculate overall inventory metrics"""
        total_items = len(items)
        total_value = sum(item.current_stock * item.unit_cost for item in items.values())
        
        # Stock status distribution
        status_counts = {}
        for item in items.values():
            status = item.status
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
        
        # ABC analysis distribution
        abc_distribution = {"A": 0, "B": 0, "C": 0}
        for item in items.values():
            abc_category = self._perform_abc_analysis(item)
            abc_distribution[abc_category] += 1
        
        # Stock level analysis
        low_stock_items = len([item for item in items.values() if item.current_stock <= item.minimum_stock])
        overstock_items = len([item for item in items.values() if item.current_stock > item.maximum_stock])
        
        return {
            "total_items": total_items,
            "total_inventory_value": total_value,
            "average_item_value": total_value / total_items if total_items > 0 else 0,
            "status_distribution": status_counts,
            "abc_distribution": abc_distribution,
            "stock_issues": {
                "low_stock_items": low_stock_items,
                "overstock_items": overstock_items,
                "critical_items": len([item for item in items.values() if item.current_stock == 0])
            },
            "utilization_metrics": {
                "stock_turnover_ratio": random.uniform(2, 8),  # Simplified calculation
                "average_days_inventory": random.uniform(30, 180),
                "inventory_accuracy": random.uniform(0.85, 0.98)
            }
        }
    
    def _identify_priority_actions(self, optimization_opportunities: List[Dict]) -> List[str]:
        """Identify priority actions from optimization analysis"""
        priority_actions = []
        
        # Critical stock issues
        critical_items = [opp for opp in optimization_opportunities if opp["stock_optimization"]["status"] == "critical"]
        if critical_items:
            priority_actions.append(f"Address {len(critical_items)} critical stock items immediately")
        
        # Overstock issues
        overstock_items = [opp for opp in optimization_opportunities if opp["stock_optimization"]["status"] == "overstock"]
        if overstock_items:
            priority_actions.append(f"Review and reduce {len(overstock_items)} overstocked items")
        
        # High-value A-items with issues
        a_items_with_issues = [opp for opp in optimization_opportunities 
                              if opp["abc_category"] == "A" and opp["stock_optimization"]["status"] != "optimal"]
        if a_items_with_issues:
            priority_actions.append(f"Optimize {len(a_items_with_issues)} high-value (A-category) items")
        
        # Supplier performance issues
        supplier_issues = len([opp for opp in optimization_opportunities 
                              if len(opp["supplier_recommendations"]["recommendations"]) > 0])
        if supplier_issues:
            priority_actions.append(f"Address supplier performance issues for {supplier_issues} items")
        
        return priority_actions
    
    def _calculate_savings_potential(self, optimization_opportunities: List[Dict]) -> Dict:
        """Calculate potential savings from optimization"""
        total_savings_potential = 0
        cost_savings = 0
        carrying_cost_savings = 0
        
        for opportunity in optimization_opportunities:
            cost_opt = opportunity["cost_optimization"]
            total_savings_potential += cost_opt["optimization_potential"]
            carrying_cost_savings += cost_opt["current_carrying_cost_daily"] * 365 * 0.1  # 10% reduction
        
        return {
            "total_annual_savings_potential": total_savings_potential,
            "carrying_cost_savings": carrying_cost_savings,
            "ordering_cost_savings": total_savings_potential - carrying_cost_savings,
            "roi_estimate": random.uniform(0.15, 0.35),  # 15-35% ROI
            "payback_period_months": random.uniform(6, 18)
        }
    
    def get_inventory_dashboard(self) -> Dict:
        """Generate comprehensive inventory dashboard"""
        try:
            # Inventory overview
            inventory_overview = self._get_inventory_overview()
            
            # Stock status analysis
            stock_status = self._get_stock_status_analysis()
            
            # Demand forecasting
            demand_forecasting = self._get_demand_forecasting_summary()
            
            # Supplier performance
            supplier_performance = self._get_supplier_performance_summary()
            
            # Alerts and issues
            alerts_and_issues = self._get_alerts_and_issues_summary()
            
            # Financial metrics
            financial_metrics = self._get_financial_metrics()
            
            # Trends and insights
            trends_and_insights = self._get_trends_and_insights()
            
            return {
                "inventory_overview": inventory_overview,
                "stock_status": stock_status,
                "demand_forecasting": demand_forecasting,
                "supplier_performance": supplier_performance,
                "alerts_and_issues": alerts_and_issues,
                "financial_metrics": financial_metrics,
                "trends_and_insights": trends_and_insights,
                "recommendations_summary": self._get_recommendations_summary()
            }
            
        except Exception as e:
            logger.error(f"Error generating inventory dashboard: {str(e)}")
            raise
    
    def _get_inventory_overview(self) -> Dict:
        """Get inventory overview statistics"""
        total_items = len(self.inventory_items)
        total_value = sum(item.current_stock * item.unit_cost for item in self.inventory_items.values())
        
        # Category distribution
        category_counts = {}
        for item in self.inventory_items.values():
            category = item.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Location distribution
        location_counts = {}
        for item in self.inventory_items.values():
            location = item.location.value
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            "total_items": total_items,
            "total_value": total_value,
            "average_item_value": total_value / total_items if total_items > 0 else 0,
            "category_distribution": category_counts,
            "location_distribution": location_counts,
            "stock_coverage_days": self._calculate_stock_coverage(),
            "inventory_turnover": random.uniform(2, 8)
        }
    
    def _calculate_stock_coverage(self) -> float:
        """Calculate average stock coverage in days"""
        total_daily_demand = 0
        
        for item in self.inventory_items.values():
            # Estimate daily demand based on current stock and reorder patterns
            daily_demand = max(1, item.reorder_quantity / 30)  # Simplified calculation
            total_daily_demand += daily_demand
        
        total_stock = sum(item.current_stock for item in self.inventory_items.values())
        
        return total_stock / total_daily_demand if total_daily_demand > 0 else 0
    
    def _get_stock_status_analysis(self) -> Dict:
        """Get stock status analysis"""
        status_counts = {}
        for item in self.inventory_items.values():
            status = item.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate stock level metrics
        low_stock_count = len([item for item in self.inventory_items.values() 
                              if item.current_stock <= item.minimum_stock])
        overstock_count = len([item for item in self.inventory_items.values() 
                              if item.current_stock > item.maximum_stock])
        
        return {
            "status_distribution": status_counts,
            "stock_health_score": (len(self.inventory_items) - low_stock_count - overstock_count) / len(self.inventory_items),
            "low_stock_items": low_stock_count,
            "overstock_items": overstock_count,
            "reorder_needed": len([item for item in self.inventory_items.values() 
                                 if item.current_stock <= item.reorder_point])
        }
    
    def _get_demand_forecasting_summary(self) -> Dict:
        """Get demand forecasting summary"""
        forecast_by_type = {}
        total_forecasted_demand = 0
        
        for forecast in self.demand_forecasts.values():
            forecast_type = forecast.forecast_type.value
            forecast_by_type[forecast_type] = forecast_by_type.get(forecast_type, 0) + 1
            total_forecasted_demand += forecast.predicted_demand
        
        return {
            "total_forecasts": len(self.demand_forecasts),
            "forecast_by_type": forecast_by_type,
            "total_forecasted_demand": total_forecasted_demand,
            "average_confidence": sum(f.confidence_level for f in self.demand_forecasts.values()) / len(self.demand_forecasts) if self.demand_forecasts else 0,
            "forecast_accuracy": random.uniform(0.75, 0.90)
        }
    
    def _get_supplier_performance_summary(self) -> Dict:
        """Get supplier performance summary"""
        if not self.suppliers:
            return {"total_suppliers": 0}
        
        # Calculate average performance metrics
        avg_quality = sum(s.quality_rating for s in self.suppliers.values()) / len(self.suppliers)
        avg_reliability = sum(s.reliability_rating for s in self.suppliers.values()) / len(self.suppliers)
        avg_delivery = sum(s.metrics.on_time_delivery_rate for s in self.suppliers.values()) / len(self.suppliers)
        
        # Identify top and bottom performers
        suppliers_by_quality = sorted(self.suppliers.values(), key=lambda x: x.quality_rating, reverse=True)
        suppliers_by_reliability = sorted(self.suppliers.values(), key=lambda x: x.reliability_rating, reverse=True)
        
        return {
            "total_suppliers": len(self.suppliers),
            "average_quality_rating": avg_quality,
            "average_reliability_rating": avg_reliability,
            "average_delivery_performance": avg_delivery,
            "top_performers": {
                "quality": suppliers_by_quality[:3],
                "reliability": suppliers_by_reliability[:3]
            },
            "suppliers_needing_attention": len([s for s in self.suppliers.values() 
                                              if s.quality_rating < 0.8 or s.reliability_rating < 0.8])
        }
    
    def _get_alerts_and_issues_summary(self) -> Dict:
        """Get alerts and issues summary"""
        total_alerts = len(self.inventory_alerts)
        unacknowledged_alerts = len([a for a in self.inventory_alerts.values() if not a.acknowledged])
        unresolved_alerts = len([a for a in self.inventory_alerts.values() if not a.resolved])
        
        # Alert type distribution
        alert_type_counts = {}
        severity_counts = {}
        
        for alert in self.inventory_alerts.values():
            alert_type = alert.alert_type
            severity = alert.severity
            alert_type_counts[alert_type] = alert_type_counts.get(alert_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged_alerts,
            "unresolved_alerts": unresolved_alerts,
            "alert_type_distribution": alert_type_counts,
            "severity_distribution": severity_counts,
            "critical_alerts": len([a for a in self.inventory_alerts.values() if a.severity == "critical"]),
            "response_time_avg": random.uniform(2, 8)  # hours
        }
    
    def _get_financial_metrics(self) -> Dict:
        """Get financial metrics"""
        total_inventory_value = sum(item.current_stock * item.unit_cost for item in self.inventory_items.values())
        
        # Calculate carrying costs (25% annually)
        annual_carrying_cost = total_inventory_value * 0.25
        
        # Calculate ordering costs
        annual_ordering_cost = len(self.reorder_recommendations) * 50  # $50 per order
        
        # Calculate total costs
        total_inventory_cost = annual_carrying_cost + annual_ordering_cost
        
        # Inventory value by category
        category_values = {}
        for item in self.inventory_items.values():
            category = item.category.value
            value = item.current_stock * item.unit_cost
            category_values[category] = category_values.get(category, 0) + value
        
        return {
            "total_inventory_value": total_inventory_value,
            "annual_carrying_cost": annual_carrying_cost,
            "annual_ordering_cost": annual_ordering_cost,
            "total_inventory_cost": total_inventory_cost,
            "cost_by_category": category_values,
            "inventory_turnover": random.uniform(2, 8),
            "days_inventory_outstanding": random.uniform(30, 180),
            "working_capital_requirements": total_inventory_value * 0.6  # 60% of inventory value
        }
    
    def _get_trends_and_insights(self) -> Dict:
        """Get trends and insights"""
        # Analyze recent trends
        recent_movements = [m for m in self.stock_movements.values() 
                           if m.timestamp >= datetime.now() - timedelta(days=30)]
        
        # Calculate movement trends
        if recent_movements:
            inbound_value = sum(m.total_cost for m in recent_movements if m.movement_type == "in")
            outbound_value = sum(m.total_cost for m in recent_movements if m.movement_type == "out")
            net_flow = inbound_value - outbound_value
        else:
            net_flow = 0
        
        return {
            "inventory_trends": {
                "net_flow_30_days": net_flow,
                "movement_trend": "increasing" if net_flow > 0 else "decreasing",
                "turnover_trend": random.choice(["improving", "stable", "declining"])
            },
            "demand_trends": {
                "forecast_accuracy": random.uniform(0.75, 0.90),
                "demand_volatility": random.uniform(0.15, 0.40),
                "seasonal_impact": random.uniform(0.10, 0.30)
            },
            "supply_trends": {
                "supplier_performance": random.choice(["improving", "stable", "declining"]),
                "lead_time_trend": random.choice(["improving", "stable", "increasing"]),
                "cost_trend": random.choice(["decreasing", "stable", "increasing"])
            },
            "key_insights": [
                "Inventory optimization opportunities identified",
                "Demand forecasting showing seasonal patterns",
                "Supplier performance within acceptable ranges",
                "Cost optimization potential in carrying costs"
            ]
        }
    
    def _get_recommendations_summary(self) -> Dict:
        """Get recommendations summary"""
        return {
            "total_recommendations": len(self.reorder_recommendations),
            "priority_recommendations": len([r for r in self.reorder_recommendations.values() 
                                           if r.priority_level in ["critical", "high"]]),
            "cost_impact": sum(r.estimated_cost for r in self.reorder_recommendations.values()),
            "implementation_timeline": "1-2 weeks for critical items, 1 month for others",
            "expected_benefits": [
                "Reduced stockout incidents",
                "Improved inventory turnover",
                "Lower carrying costs",
                "Better supplier relationships"
            ]
        }

# FastAPI Application
app = FastAPI(title="Inventory Management", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
inventory_ai = InventoryAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=inventory_ai.web_components.render_inventory_dashboard())

@app.get("/api/inventory-items")
async def get_inventory_items():
    """Get all inventory items"""
    return {"items": list(inventory_ai.inventory_items.values())}

@app.get("/api/stock-movements")
async def get_stock_movements():
    """Get all stock movements"""
    return {"movements": list(inventory_ai.stock_movements.values())}

@app.get("/api/suppliers")
async def get_suppliers():
    """Get all suppliers"""
    return {"suppliers": list(inventory_ai.suppliers.values())}

@app.get("/api/demand-forecasts")
async def get_demand_forecasts():
    """Get all demand forecasts"""
    return {"forecasts": list(inventory_ai.demand_forecasts.values())}

@app.get("/api/reorder-recommendations")
async def get_reorder_recommendations():
    """Get reorder recommendations"""
    return {"recommendations": list(inventory_ai.reorder_recommendations.values())}

@app.get("/api/inventory-alerts")
async def get_inventory_alerts():
    """Get inventory alerts"""
    return {"alerts": list(inventory_ai.inventory_alerts.values())}

@app.post("/api/optimization-analysis")
async def analyze_inventory_optimization(analysis_request: Dict):
    """Analyze inventory optimization"""
    try:
        product_id = analysis_request.get("product_id")
        optimization_analysis = await inventory_ai.analyze_inventory_optimization(product_id)
        return optimization_analysis
    except Exception as e:
        logger.error(f"Error analyzing inventory optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory-dashboard")
async def get_inventory_dashboard():
    """Get inventory dashboard data"""
    try:
        dashboard_data = inventory_ai.get_inventory_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting inventory dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/generate-analysis")
async def generate_demo_analysis():
    """Generate optimization analysis for a random demo item"""
    item_ids = list(inventory_ai.inventory_items.keys())
    if not item_ids:
        raise HTTPException(status_code=404, detail="No inventory items available for analysis")
    
    item_id = random.choice(item_ids)
    optimization_analysis = await inventory_ai.analyze_inventory_optimization(item_id)
    return {"item_id": item_id, "analysis": optimization_analysis}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting Inventory Management...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")