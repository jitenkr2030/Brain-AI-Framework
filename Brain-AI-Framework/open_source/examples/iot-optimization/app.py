"""
IoT Optimization - Brain AI Framework Example
A comprehensive IoT optimization system that helps organizations optimize device performance,
energy consumption, and operational efficiency using Brain AI Framework.
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
logger.add("logs/iot_optimization.log", rotation="10 MB", level="INFO")

class DeviceType(Enum):
    """Device type enumeration"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    CAMERA = "camera"
    CONTROLLER = "controller"
    METER = "meter"
    SWITCH = "switch"
    LIGHT = "light"
    THERMOSTAT = "thermostat"

class DeviceStatus(Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    LOW_BATTERY = "low_battery"

class EnvironmentType(Enum):
    """Environment type enumeration"""
    OFFICE = "office"
    FACTORY = "factory"
    WAREHOUSE = "warehouse"
    RETAIL = "retail"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    HOME = "home"
    OUTDOOR = "outdoor"

class OptimizationType(Enum):
    """Optimization type enumeration"""
    ENERGY = "energy"
    PERFORMANCE = "performance"
    COST = "cost"
    RELIABILITY = "reliability"
    COMFORT = "comfort"
    SECURITY = "security"

@dataclass
class IoTMetric:
    """IoT performance metric"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    threshold: float
    status: str

@dataclass
class EnergyConsumption:
    """Energy consumption data point"""
    device_id: str
    timestamp: datetime
    power_consumption: float  # Watts
    energy_consumed: float    # kWh
    efficiency_score: float
    cost_per_hour: float

@dataclass
class NetworkTraffic:
    """Network traffic data point"""
    device_id: str
    timestamp: datetime
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    latency: float  # milliseconds
    bandwidth_utilization: float

class IoTDevice(BaseModel):
    """IoT device model"""
    device_id: str
    name: str
    device_type: DeviceType
    environment: EnvironmentType
    location: str
    firmware_version: str
    battery_level: float
    last_seen: datetime
    status: DeviceStatus
    specifications: Dict[str, Any]
    tags: List[str]

class DeviceReading(BaseModel):
    """Device sensor reading model"""
    reading_id: str
    device_id: str
    timestamp: datetime
    sensor_type: str
    value: float
    unit: str
    quality: float  # Data quality score 0-1
    anomalies: List[str]

class OptimizationRule(BaseModel):
    """Optimization rule model"""
    rule_id: str
    name: str
    description: str
    optimization_type: OptimizationType
    conditions: List[Dict]
    actions: List[Dict]
    priority: int
    enabled: bool
    last_triggered: Optional[datetime]

class PerformanceInsight(BaseModel):
    """Performance insight model"""
    insight_id: str
    device_id: str
    insight_type: str
    title: str
    description: str
    impact_level: str
    recommendations: List[str]
    potential_savings: Dict[str, float]
    confidence_score: float
    timestamp: datetime

class IoTOptimizationAI:
    """Main IoT optimization AI engine"""
    
    def __init__(self, brain_ai: BrainAIIntegration):
        self.brain_ai = brain_ai
        self.demo_data = DemoDataGenerator()
        self.web_components = WebComponents()
        self.devices: Dict[str, IoTDevice] = {}
        self.device_readings: Dict[str, List[DeviceReading]] = {}
        self.energy_consumption: Dict[str, List[EnergyConsumption]] = {}
        self.network_traffic: Dict[str, List[NetworkTraffic]] = {}
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.performance_insights: Dict[str, PerformanceInsight] = {}
        
        # Optimization thresholds
        self.thresholds = {
            "battery_low": 20.0,  # Percentage
            "energy_high": 100.0,  # Watts
            "latency_high": 100.0,  # Milliseconds
            "temperature_high": 35.0,  # Celsius
            "humidity_high": 80.0,  # Percentage
            "traffic_high": 1000000  # Bytes per minute
        }
        
        # Environment configurations
        self.environment_configs = self._initialize_environment_configs()
        
        # Initialize demo data
        self._initialize_demo_data()
    
    def _initialize_environment_configs(self) -> Dict:
        """Initialize environment-specific configurations"""
        return {
            EnvironmentType.OFFICE: {
                "optimal_temperature": (20, 24),
                "optimal_humidity": (40, 60),
                "lighting_level": 500,  # Lux
                "occupancy_threshold": 0.3
            },
            EnvironmentType.FACTORY: {
                "optimal_temperature": (18, 26),
                "optimal_humidity": (30, 70),
                "lighting_level": 750,  # Lux
                "occupancy_threshold": 0.5
            },
            EnvironmentType.RETAIL: {
                "optimal_temperature": (21, 23),
                "optimal_humidity": (45, 55),
                "lighting_level": 1000,  # Lux
                "occupancy_threshold": 0.4
            }
        }
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Generate demo IoT devices
        for i in range(150):
            device = self.demo_data.generate_iot_device(
                device_id=f"DEVICE_{i+1:03d}",
                device_type=random.choice(list(DeviceType)),
                environment=random.choice(list(EnvironmentType))
            )
            self.devices[device.device_id] = device
            
            # Initialize empty readings list
            self.device_readings[device.device_id] = []
            self.energy_consumption[device.device_id] = []
            self.network_traffic[device.device_id] = []
        
        # Generate demo device readings
        self._generate_device_readings()
        
        # Generate energy consumption data
        self._generate_energy_consumption()
        
        # Generate network traffic data
        self._generate_network_traffic()
        
        # Generate optimization rules
        self._generate_optimization_rules()
        
        # Generate performance insights
        self._generate_performance_insights()
        
        logger.info(f"Initialized demo data: {len(self.devices)} devices, "
                   f"{sum(len(readings) for readings in self.device_readings.values())} readings")
    
    def _generate_device_readings(self):
        """Generate demo device readings"""
        sensor_types = ["temperature", "humidity", "pressure", "light", "motion", "sound", "vibration"]
        
        for device_id in self.devices.keys():
            # Generate readings for the last 30 days
            for day in range(30):
                for hour in range(0, 24, 2):  # Every 2 hours
                    timestamp = datetime.now() - timedelta(days=day, hours=hour)
                    
                    # Generate 1-3 readings per time slot
                    for _ in range(random.randint(1, 3)):
                        sensor_type = random.choice(sensor_types)
                        value = self._generate_sensor_value(sensor_type)
                        
                        reading = DeviceReading(
                            reading_id=f"READING_{len(self.device_readings[device_id])+1:06d}",
                            device_id=device_id,
                            timestamp=timestamp,
                            sensor_type=sensor_type,
                            value=value,
                            unit=self._get_sensor_unit(sensor_type),
                            quality=random.uniform(0.8, 1.0),
                            anomalies=self._detect_anomalies(sensor_type, value)
                        )
                        
                        self.device_readings[device_id].append(reading)
    
    def _generate_sensor_value(self, sensor_type: str) -> float:
        """Generate realistic sensor values"""
        ranges = {
            "temperature": (15, 30),
            "humidity": (30, 80),
            "pressure": (990, 1030),
            "light": (100, 1500),
            "motion": (0, 1),
            "sound": (30, 80),
            "vibration": (0, 10)
        }
        
        if sensor_type in ranges:
            return random.uniform(*ranges[sensor_type])
        else:
            return random.uniform(0, 100)
    
    def _get_sensor_unit(self, sensor_type: str) -> str:
        """Get unit for sensor type"""
        units = {
            "temperature": "°C",
            "humidity": "%",
            "pressure": "hPa",
            "light": "lux",
            "motion": "bool",
            "sound": "dB",
            "vibration": "mm/s"
        }
        return units.get(sensor_type, "unit")
    
    def _detect_anomalies(self, sensor_type: str, value: float) -> List[str]:
        """Detect sensor anomalies"""
        anomalies = []
        
        if sensor_type == "temperature":
            if value > 30 or value < 15:
                anomalies.append("Temperature outside normal range")
        elif sensor_type == "humidity":
            if value > 80 or value < 30:
                anomalies.append("Humidity outside normal range")
        elif sensor_type == "light":
            if value > 1500:
                anomalies.append("Unusually high light levels")
        elif sensor_type == "motion":
            if value == 1 and random.random() < 0.1:  # 10% chance of anomaly
                anomalies.append("Unexpected motion detected")
        
        return anomalies
    
    def _generate_energy_consumption(self):
        """Generate energy consumption data"""
        for device_id in self.devices.keys():
            device = self.devices[device_id]
            
            # Generate consumption for the last 30 days
            for day in range(30):
                for hour in range(24):
                    timestamp = datetime.now() - timedelta(days=day, hours=hour)
                    
                    # Base consumption depends on device type
                    base_power = self._get_device_base_power(device.device_type)
                    power_variation = random.uniform(0.8, 1.2)
                    actual_power = base_power * power_variation
                    
                    # Add peak hours variation
                    if 8 <= hour <= 18:  # Business hours
                        actual_power *= 1.3
                    
                    energy_kwh = actual_power / 1000  # Convert to kWh
                    cost_per_hour = energy_kwh * 0.12  # $0.12 per kWh
                    
                    consumption = EnergyConsumption(
                        device_id=device_id,
                        timestamp=timestamp,
                        power_consumption=actual_power,
                        energy_consumed=energy_kwh,
                        efficiency_score=random.uniform(0.7, 0.95),
                        cost_per_hour=cost_per_hour
                    )
                    
                    self.energy_consumption[device_id].append(consumption)
    
    def _get_device_base_power(self, device_type: DeviceType) -> float:
        """Get base power consumption for device type"""
        power_map = {
            DeviceType.SENSOR: 5.0,
            DeviceType.ACTUATOR: 25.0,
            DeviceType.GATEWAY: 15.0,
            DeviceType.CAMERA: 50.0,
            DeviceType.CONTROLLER: 30.0,
            DeviceType.METER: 10.0,
            DeviceType.SWITCH: 8.0,
            DeviceType.LIGHT: 60.0,
            DeviceType.THERMOSTAT: 20.0
        }
        return power_map.get(device_type, 20.0)
    
    def _generate_network_traffic(self):
        """Generate network traffic data"""
        for device_id in self.devices.keys():
            device = self.devices[device_id]
            
            # Generate traffic for the last 7 days
            for day in range(7):
                for hour in range(24):
                    timestamp = datetime.now() - timedelta(days=day, hours=hour)
                    
                    # Base traffic depends on device type
                    base_bytes = self._get_device_base_traffic(device.device_type)
                    bytes_variation = random.uniform(0.5, 2.0)
                    actual_bytes = base_bytes * bytes_variation
                    
                    # Split between sent and received
                    bytes_sent = int(actual_bytes * 0.4)
                    bytes_received = int(actual_bytes * 0.6)
                    
                    packets_sent = bytes_sent // 1000  # Approximate
                    packets_received = bytes_received // 1000
                    
                    latency = random.uniform(10, 200)
                    bandwidth_util = random.uniform(0.1, 0.8)
                    
                    traffic = NetworkTraffic(
                        device_id=device_id,
                        timestamp=timestamp,
                        bytes_sent=bytes_sent,
                        bytes_received=bytes_received,
                        packets_sent=packets_sent,
                        packets_received=packets_received,
                        latency=latency,
                        bandwidth_utilization=bandwidth_util
                    )
                    
                    self.network_traffic[device_id].append(traffic)
    
    def _get_device_base_traffic(self, device_type: DeviceType) -> int:
        """Get base network traffic for device type"""
        traffic_map = {
            DeviceType.SENSOR: 5000,      # 5KB per hour
            DeviceType.ACTUATOR: 2000,    # 2KB per hour
            DeviceType.GATEWAY: 100000,   # 100KB per hour
            DeviceType.CAMERA: 500000,    # 500KB per hour
            DeviceType.CONTROLLER: 10000, # 10KB per hour
            DeviceType.METER: 3000,       # 3KB per hour
            DeviceType.SWITCH: 8000,      # 8KB per hour
            DeviceType.LIGHT: 1000,       # 1KB per hour
            DeviceType.THERMOSTAT: 2000   # 2KB per hour
        }
        return traffic_map.get(device_type, 5000)
    
    def _generate_optimization_rules(self):
        """Generate optimization rules"""
        rule_templates = [
            {
                "name": "Energy Saver - Office Hours",
                "description": "Reduce power consumption during non-business hours",
                "type": OptimizationType.ENERGY,
                "conditions": [{"time_range": "18:00-08:00"}, {"environment": "office"}],
                "actions": [{"action": "dim_lights"}, {"action": "reduce_hvac"}],
                "priority": 1
            },
            {
                "name": "Battery Saver",
                "description": "Optimize device settings when battery is low",
                "type": OptimizationType.ENERGY,
                "conditions": [{"battery_level": "< 20"}],
                "actions": [{"action": "reduce_transmission"}, {"action": "increase_interval"}],
                "priority": 2
            },
            {
                "name": "Performance Optimizer",
                "description": "Optimize device performance based on usage patterns",
                "type": OptimizationType.PERFORMANCE,
                "conditions": [{"usage_pattern": "high"}],
                "actions": [{"action": "increase_processing"}, {"action": "cache_data"}],
                "priority": 3
            },
            {
                "name": "Security Mode",
                "description": "Enhanced security during off-hours",
                "type": OptimizationType.SECURITY,
                "conditions": [{"time_range": "22:00-06:00"}, {"environment": "retail"}],
                "actions": [{"action": "enable_alerts"}, {"action": "increase_recording"}],
                "priority": 1
            }
        ]
        
        for i, template in enumerate(rule_templates):
            rule = OptimizationRule(
                rule_id=f"RULE_{i+1:03d}",
                name=template["name"],
                description=template["description"],
                optimization_type=template["type"],
                conditions=template["conditions"],
                actions=template["actions"],
                priority=template["priority"],
                enabled=True,
                last_triggered=None
            )
            
            self.optimization_rules[rule.rule_id] = rule
    
    def _generate_performance_insights(self):
        """Generate performance insights"""
        insight_templates = [
            {
                "type": "energy_efficiency",
                "title": "High Energy Consumption Detected",
                "description": "Device consuming above average energy",
                "impact": "high",
                "savings": {"energy": 15.5, "cost": 23.25}
            },
            {
                "type": "network_optimization",
                "title": "Network Traffic Optimization Opportunity",
                "description": "Reduce network traffic through data compression",
                "impact": "medium",
                "savings": {"bandwidth": 25.0, "cost": 12.75}
            },
            {
                "type": "maintenance",
                "title": "Predictive Maintenance Recommended",
                "description": "Device showing signs of wear",
                "impact": "high",
                "savings": {"downtime": 500.0, "cost": 150.0}
            },
            {
                "type": "configuration",
                "title": "Configuration Optimization",
                "description": "Optimize device configuration for better performance",
                "impact": "medium",
                "savings": {"performance": 8.5, "cost": 5.2}
            }
        ]
        
        for device_id in list(self.devices.keys())[:20]:  # Generate insights for 20 devices
            template = random.choice(insight_templates)
            
            insight = PerformanceInsight(
                insight_id=f"INSIGHT_{len(self.performance_insights)+1:03d}",
                device_id=device_id,
                insight_type=template["type"],
                title=template["title"],
                description=template["description"],
                impact_level=template["impact"],
                recommendations=self._generate_recommendations(template["type"]),
                potential_savings=template["savings"],
                confidence_score=random.uniform(0.7, 0.95),
                timestamp=datetime.now() - timedelta(hours=random.randint(1, 48))
            )
            
            self.performance_insights[insight.insight_id] = insight
    
    def _generate_recommendations(self, insight_type: str) -> List[str]:
        """Generate recommendations based on insight type"""
        recommendations_map = {
            "energy_efficiency": [
                "Implement energy-saving mode",
                "Optimize duty cycles",
                "Upgrade to energy-efficient hardware",
                "Schedule maintenance check"
            ],
            "network_optimization": [
                "Enable data compression",
                "Optimize transmission intervals",
                "Reduce unnecessary data transfers",
                "Implement local data processing"
            ],
            "maintenance": [
                "Schedule preventive maintenance",
                "Replace worn components",
                "Update firmware",
                "Clean and calibrate sensors"
            ],
            "configuration": [
                "Optimize device settings",
                "Update configuration parameters",
                "Enable power management features",
                "Review and update security settings"
            ]
        }
        
        return random.sample(recommendations_map.get(insight_type, []), random.randint(1, 3))
    
    async def analyze_device_performance(self, device_id: str) -> PerformanceInsight:
        """Analyze device performance using Brain AI"""
        try:
            device = self.devices.get(device_id)
            if not device:
                raise ValueError(f"Device {device_id} not found")
            
            # Prepare performance analysis context
            analysis_context = {
                "device_info": device.dict(),
                "recent_readings": self.device_readings.get(device_id, [])[-100:],  # Last 100 readings
                "energy_data": self.energy_consumption.get(device_id, [])[-24:],   # Last 24 hours
                "network_data": self.network_traffic.get(device_id, [])[-24:],      # Last 24 hours
                "device_history": self._get_device_history(device_id),
                "similar_devices": self._get_similar_devices(device)
            }
            
            # Use Brain AI to analyze device performance
            ai_analysis = await self.brain_ai.process_device_performance_analysis(analysis_context)
            
            # Generate performance insight
            insight_type = self._determine_insight_type(device, analysis_context)
            insight = PerformanceInsight(
                insight_id=f"INSIGHT_{len(self.performance_insights)+1:04d}",
                device_id=device_id,
                insight_type=insight_type,
                title=self._generate_insight_title(insight_type),
                description=self._generate_insight_description(device, insight_type),
                impact_level=self._assess_impact_level(device, analysis_context),
                recommendations=self._generate_insight_recommendations(insight_type, device),
                potential_savings=self._calculate_potential_savings(device, insight_type),
                confidence_score=0.89,
                timestamp=datetime.now()
            )
            
            # Store in memory for future reference
            await self.brain_ai.store_performance_insight(device_id, insight.dict())
            
            self.performance_insights[insight.insight_id] = insight
            logger.info(f"Analyzed device performance for {device_id}, insight: {insight.insight_type}")
            
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing device performance: {str(e)}")
            raise
    
    def _get_device_history(self, device_id: str) -> Dict:
        """Get device performance history"""
        readings = self.device_readings.get(device_id, [])
        
        return {
            "total_readings": len(readings),
            "last_reading": readings[-1].timestamp if readings else None,
            "uptime_percentage": random.uniform(95, 99.9),
            "maintenance_count": random.randint(0, 3),
            "firmware_updates": random.randint(1, 5)
        }
    
    def _get_similar_devices(self, device: IoTDevice) -> List[Dict]:
        """Get similar devices for comparison"""
        similar = []
        for other_device in self.devices.values():
            if (other_device.device_type == device.device_type and 
                other_device.environment == device.environment and
                other_device.device_id != device.device_id):
                similar.append(other_device.dict())
                if len(similar) >= 5:  # Limit to 5 similar devices
                    break
        
        return similar
    
    def _determine_insight_type(self, device: IoTDevice, context: Dict) -> str:
        """Determine type of performance insight"""
        readings = context["recent_readings"]
        energy_data = context["energy_data"]
        
        # Analyze patterns to determine insight type
        avg_power = sum(e.power_consumption for e in energy_data) / len(energy_data) if energy_data else 0
        device_base_power = self._get_device_base_power(device.device_type)
        
        if avg_power > device_base_power * 1.2:
            return "energy_efficiency"
        elif len(readings) > 0 and any(r.anomalies for r in readings):
            return "anomaly_detection"
        elif device.battery_level < self.thresholds["battery_low"]:
            return "battery_optimization"
        else:
            return "performance_optimization"
    
    def _generate_insight_title(self, insight_type: str) -> str:
        """Generate insight title"""
        titles = {
            "energy_efficiency": "Energy Optimization Opportunity",
            "performance_optimization": "Performance Enhancement Available",
            "battery_optimization": "Battery Life Extension Possible",
            "anomaly_detection": "Anomalous Behavior Detected",
            "maintenance": "Maintenance Required",
            "network_optimization": "Network Performance Optimization"
        }
        return titles.get(insight_type, "Performance Insight Available")
    
    def _generate_insight_description(self, device: IoTDevice, insight_type: str) -> str:
        """Generate insight description"""
        descriptions = {
            "energy_efficiency": f"Device {device.name} is consuming more energy than optimal. Optimization could reduce consumption by 15-25%.",
            "performance_optimization": f"Device {device.name} performance can be enhanced through configuration optimization.",
            "battery_optimization": f"Device {device.name} battery level is low. Optimization strategies can extend battery life.",
            "anomaly_detection": f"Unusual behavior detected in device {device.name}. Investigation recommended.",
            "maintenance": f"Device {device.name} may require maintenance based on performance patterns.",
            "network_optimization": f"Network performance for {device.name} can be optimized to reduce traffic."
        }
        return descriptions.get(insight_type, f"Performance optimization opportunity identified for {device.name}")
    
    def _assess_impact_level(self, device: IoTDevice, context: Dict) -> str:
        """Assess impact level of the insight"""
        device_type_impact = {
            DeviceType.GATEWAY: "high",
            DeviceType.CAMERA: "high",
            DeviceType.CONTROLLER: "high",
            DeviceType.SENSOR: "medium",
            DeviceType.ACTUATOR: "medium"
        }
        
        base_impact = device_type_impact.get(device.device_type, "medium")
        
        # Adjust based on device status and environment
        if device.status == DeviceStatus.ERROR:
            return "critical"
        elif device.environment in [EnvironmentType.FACTORY, EnvironmentType.HOSPITAL]:
            return "high" if base_impact == "medium" else base_impact
        
        return base_impact
    
    def _generate_insight_recommendations(self, insight_type: str, device: IoTDevice) -> List[str]:
        """Generate recommendations for the insight"""
        base_recommendations = self._generate_recommendations(insight_type)
        
        # Add device-specific recommendations
        if device.device_type == DeviceType.CAMERA:
            base_recommendations.append("Optimize recording settings")
            base_recommendations.append("Implement motion-based activation")
        elif device.device_type == DeviceType.SENSOR:
            base_recommendations.append("Optimize transmission frequency")
            base_recommendations.append("Enable local processing")
        
        return base_recommendations
    
    def _calculate_potential_savings(self, device: IoTDevice, insight_type: str) -> Dict[str, float]:
        """Calculate potential savings from optimization"""
        base_power = self._get_device_base_power(device.device_type)
        
        savings_map = {
            "energy_efficiency": {
                "energy": base_power * 0.2,  # 20% energy reduction
                "cost": base_power * 0.2 * 0.12  # Energy cost savings
            },
            "network_optimization": {
                "bandwidth": self._get_device_base_traffic(device.device_type) * 0.3,  # 30% traffic reduction
                "cost": 10.0  # Network cost savings
            },
            "maintenance": {
                "downtime": 50.0,  # Downtime cost savings
                "cost": 100.0  # Maintenance cost savings
            }
        }
        
        return savings_map.get(insight_type, {"cost": 5.0})
    
    def optimize_energy_consumption(self, environment: EnvironmentType = None) -> Dict:
        """Generate energy optimization recommendations"""
        try:
            # Filter devices by environment if specified
            devices_to_analyze = self.devices.values()
            if environment:
                devices_to_analyze = [d for d in devices_to_analyze if d.environment == environment]
            
            # Calculate current energy consumption
            total_consumption = 0
            optimization_opportunities = []
            
            for device in devices_to_analyze:
                energy_data = self.energy_consumption.get(device.device_id, [])
                if energy_data:
                    avg_power = sum(e.power_consumption for e in energy_data) / len(energy_data)
                    daily_consumption = avg_power * 24 / 1000  # kWh per day
                    total_consumption += daily_consumption
                    
                    # Identify optimization opportunities
                    if avg_power > self._get_device_base_power(device.device_type) * 1.1:
                        optimization_opportunities.append({
                            "device_id": device.device_id,
                            "device_name": device.name,
                            "current_power": avg_power,
                            "potential_savings": avg_power * 0.15,  # 15% savings
                            "priority": self._calculate_optimization_priority(device, avg_power)
                        })
            
            # Generate environment-specific recommendations
            env_recommendations = self._generate_energy_recommendations(environment)
            
            # Calculate total potential savings
            total_potential_savings = sum(op["potential_savings"] for op in optimization_opportunities)
            
            return {
                "environment": environment.value if environment else "all",
                "total_devices": len(devices_to_analyze),
                "current_daily_consumption": total_consumption,
                "optimization_opportunities": optimization_opportunities,
                "total_potential_savings": total_potential_savings,
                "savings_percentage": (total_potential_savings / total_consumption * 100) if total_consumption > 0 else 0,
                "recommendations": env_recommendations,
                "roi_analysis": self._calculate_energy_roi(optimization_opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing energy consumption: {str(e)}")
            raise
    
    def _calculate_optimization_priority(self, device: IoTDevice, current_power: float) -> str:
        """Calculate optimization priority for device"""
        base_power = self._get_device_base_power(device.device_type)
        excess_power = current_power - base_power
        
        if excess_power > base_power * 0.3:
            return "high"
        elif excess_power > base_power * 0.15:
            return "medium"
        else:
            return "low"
    
    def _generate_energy_recommendations(self, environment: EnvironmentType = None) -> List[str]:
        """Generate environment-specific energy recommendations"""
        recommendations = [
            "Implement smart scheduling for non-critical devices",
            "Enable power-saving modes during off-hours",
            "Optimize device duty cycles",
            "Consider upgrading to energy-efficient models"
        ]
        
        if environment == EnvironmentType.OFFICE:
            recommendations.extend([
                "Optimize HVAC scheduling",
                "Implement occupancy-based lighting",
                "Use natural light when available"
            ])
        elif environment == EnvironmentType.FACTORY:
            recommendations.extend([
                "Optimize manufacturing equipment schedules",
                "Implement predictive maintenance",
                "Use energy-efficient industrial equipment"
            ])
        elif environment == EnvironmentType.RETAIL:
            recommendations.extend([
                "Optimize store hours and lighting",
                "Implement smart climate control",
                "Use energy-efficient display equipment"
            ])
        
        return recommendations
    
    def _calculate_energy_roi(self, optimization_opportunities: List[Dict]) -> Dict:
        """Calculate return on investment for energy optimizations"""
        total_investment = len(optimization_opportunities) * 1000  # $1000 per device
        total_savings = sum(op["potential_savings"] for op in optimization_opportunities) * 24 * 365  # Annual savings
        annual_cost_savings = total_savings * 0.12  # $0.12 per kWh
        
        roi_percentage = (annual_cost_savings - total_investment) / total_investment * 100 if total_investment > 0 else 0
        payback_months = total_investment / (annual_cost_savings / 12) if annual_cost_savings > 0 else 0
        
        return {
            "investment_required": total_investment,
            "annual_savings": annual_cost_savings,
            "roi_percentage": roi_percentage,
            "payback_months": payback_months,
            "net_present_value": annual_cost_savings * 5 - total_investment  # 5-year NPV
        }
    
    def get_iot_dashboard(self) -> Dict:
        """Generate comprehensive IoT dashboard"""
        try:
            # Device overview
            device_overview = self._get_device_overview()
            
            # Performance metrics
            performance_metrics = self._get_performance_metrics()
            
            # Energy analysis
            energy_analysis = self._get_energy_analysis()
            
            # Network analysis
            network_analysis = self._get_network_analysis()
            
            # Optimization insights
            optimization_insights = self._get_optimization_insights()
            
            # Alerts and issues
            alerts_and_issues = self._get_alerts_and_issues()
            
            return {
                "device_overview": device_overview,
                "performance_metrics": performance_metrics,
                "energy_analysis": energy_analysis,
                "network_analysis": network_analysis,
                "optimization_insights": optimization_insights,
                "alerts_and_issues": alerts_and_issues,
                "environment_summary": self._get_environment_summary(),
                "predictive_insights": self._get_predictive_insights()
            }
            
        except Exception as e:
            logger.error(f"Error generating IoT dashboard: {str(e)}")
            raise
    
    def _get_device_overview(self) -> Dict:
        """Get device overview statistics"""
        total_devices = len(self.devices)
        online_devices = len([d for d in self.devices.values() if d.status == DeviceStatus.ONLINE])
        offline_devices = len([d for d in self.devices.values() if d.status == DeviceStatus.OFFLINE])
        error_devices = len([d for d in self.devices.values() if d.status == DeviceStatus.ERROR])
        
        # Device type distribution
        device_types = {}
        for device_type in DeviceType:
            count = len([d for d in self.devices.values() if d.device_type == device_type])
            device_types[device_type.value] = count
        
        return {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": offline_devices,
            "error_devices": error_devices,
            "availability_percentage": (online_devices / total_devices * 100) if total_devices > 0 else 0,
            "device_type_distribution": device_types,
            "environment_distribution": self._get_environment_distribution()
        }
    
    def _get_environment_distribution(self) -> Dict:
        """Get device distribution by environment"""
        distribution = {}
        for env in EnvironmentType:
            count = len([d for d in self.devices.values() if d.environment == env])
            distribution[env.value] = count
        return distribution
    
    def _get_performance_metrics(self) -> Dict:
        """Get performance metrics"""
        all_readings = []
        for readings_list in self.device_readings.values():
            all_readings.extend(readings_list)
        
        # Calculate data quality
        quality_scores = [r.quality for r in all_readings if hasattr(r, 'quality')]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Calculate anomaly rates
        total_readings = len(all_readings)
        anomalous_readings = len([r for r in all_readings if r.anomalies])
        anomaly_rate = (anomalous_readings / total_readings * 100) if total_readings > 0 else 0
        
        return {
            "data_quality_score": avg_quality,
            "anomaly_rate": anomaly_rate,
            "total_readings": total_readings,
            "last_24h_readings": len([r for r in all_readings if r.timestamp >= datetime.now() - timedelta(days=1)]),
            "sensor_types": len(set(r.sensor_type for r in all_readings)),
            "avg_reading_frequency": self._calculate_reading_frequency(all_readings)
        }
    
    def _calculate_reading_frequency(self, readings: List[DeviceReading]) -> float:
        """Calculate average reading frequency"""
        if len(readings) < 2:
            return 0
        
        readings.sort(key=lambda x: x.timestamp)
        time_span = (readings[-1].timestamp - readings[0].timestamp).total_seconds()
        return len(readings) / (time_span / 3600) if time_span > 0 else 0  # readings per hour
    
    def _get_energy_analysis(self) -> Dict:
        """Get energy consumption analysis"""
        total_daily_consumption = 0
        high_consumption_devices = []
        
        for device_id, energy_data in self.energy_consumption.items():
            if energy_data:
                avg_power = sum(e.power_consumption for e in energy_data) / len(energy_data)
                daily_consumption = avg_power * 24 / 1000  # kWh
                total_daily_consumption += daily_consumption
                
                if daily_consumption > 5:  # More than 5 kWh per day
                    device = self.devices[device_id]
                    high_consumption_devices.append({
                        "device_id": device_id,
                        "device_name": device.name,
                        "daily_consumption": daily_consumption
                    })
        
        # Sort by consumption
        high_consumption_devices.sort(key=lambda x: x["daily_consumption"], reverse=True)
        
        return {
            "total_daily_consumption": total_daily_consumption,
            "estimated_monthly_cost": total_daily_consumption * 30 * 0.12,
            "high_consumption_devices": high_consumption_devices[:10],
            "efficiency_score": random.uniform(0.7, 0.9),
            "optimization_potential": total_daily_consumption * 0.2  # 20% potential savings
        }
    
    def _get_network_analysis(self) -> Dict:
        """Get network traffic analysis"""
        total_traffic = 0
        high_traffic_devices = []
        
        for device_id, traffic_data in self.network_traffic.items():
            if traffic_data:
                recent_traffic = traffic_data[-24:]  # Last 24 hours
                avg_bytes = sum(t.bytes_sent + t.bytes_received for t in recent_traffic) / len(recent_traffic)
                total_traffic += avg_bytes
                
                if avg_bytes > 100000:  # More than 100KB per hour
                    device = self.devices[device_id]
                    high_traffic_devices.append({
                        "device_id": device_id,
                        "device_name": device.name,
                        "avg_hourly_traffic": avg_bytes
                    })
        
        high_traffic_devices.sort(key=lambda x: x["avg_hourly_traffic"], reverse=True)
        
        return {
            "total_hourly_traffic": total_traffic,
            "high_traffic_devices": high_traffic_devices[:10],
            "network_efficiency": random.uniform(0.6, 0.9),
            "bandwidth_utilization": random.uniform(0.3, 0.8)
        }
    
    def _get_optimization_insights(self) -> Dict:
        """Get optimization insights summary"""
        insights_by_type = {}
        for insight in self.performance_insights.values():
            insight_type = insight.insight_type
            if insight_type not in insights_by_type:
                insights_by_type[insight_type] = []
            insights_by_type[insight_type].append(insight.dict())
        
        # Calculate potential total savings
        total_savings = 0
        for insight in self.performance_insights.values():
            total_savings += sum(insight.potential_savings.values())
        
        return {
            "total_insights": len(self.performance_insights),
            "insights_by_type": {k: len(v) for k, v in insights_by_type.items()},
            "potential_savings": total_savings,
            "high_impact_insights": len([i for i in self.performance_insights.values() if i.impact_level == "high"]),
            "recent_insights": [i.dict() for i in list(self.performance_insights.values())[-5:]]
        }
    
    def _get_alerts_and_issues(self) -> Dict:
        """Get alerts and issues summary"""
        # Check for device issues
        offline_devices = [d for d in self.devices.values() if d.status == DeviceStatus.OFFLINE]
        error_devices = [d for d in self.devices.values() if d.status == DeviceStatus.ERROR]
        low_battery_devices = [d for d in self.devices.values() if d.battery_level < self.thresholds["battery_low"]]
        
        # Check for threshold violations in recent readings
        threshold_violations = []
        for device_id, readings in self.device_readings.items():
            recent_readings = [r for r in readings if r.timestamp >= datetime.now() - timedelta(hours=1)]
            for reading in recent_readings:
                if self._check_threshold_violation(reading):
                    threshold_violations.append({
                        "device_id": device_id,
                        "reading": reading.dict()
                    })
        
        return {
            "offline_devices": len(offline_devices),
            "error_devices": len(error_devices),
            "low_battery_devices": len(low_battery_devices),
            "threshold_violations": len(threshold_violations),
            "critical_issues": len(error_devices) + len([d for d in low_battery_devices if d.status == DeviceStatus.ONLINE]),
            "recent_violations": threshold_violations[-10:]  # Last 10 violations
        }
    
    def _check_threshold_violation(self, reading: DeviceReading) -> bool:
        """Check if reading violates thresholds"""
        if reading.sensor_type == "temperature":
            return reading.value > self.thresholds["temperature_high"]
        elif reading.sensor_type == "humidity":
            return reading.value > self.thresholds["humidity_high"]
        return False
    
    def _get_environment_summary(self) -> Dict:
        """Get environment-wise summary"""
        env_summary = {}
        
        for env in EnvironmentType:
            env_devices = [d for d in self.devices.values() if d.environment == env]
            if env_devices:
                env_summary[env.value] = {
                    "device_count": len(env_devices),
                    "online_devices": len([d for d in env_devices if d.status == DeviceStatus.ONLINE]),
                    "avg_battery_level": sum(d.battery_level for d in env_devices) / len(env_devices),
                    "performance_score": random.uniform(0.7, 0.95)
                }
        
        return env_summary
    
    def _get_predictive_insights(self) -> Dict:
        """Get predictive insights"""
        return {
            "predicted_failures": len([d for d in self.devices.values() if d.battery_level < 10]),
            "maintenance_schedules": random.randint(5, 15),
            "energy_optimization": {
                "potential_savings": random.uniform(10, 30),
                "roi_months": random.uniform(6, 18)
            },
            "capacity_planning": {
                "additional_devices_needed": random.randint(2, 10),
                "infrastructure_upgrades": random.randint(1, 5)
            }
        }

# FastAPI Application
app = FastAPI(title="IoT Optimization", version="1.0.0")

# Initialize Brain AI Integration
brain_ai = BrainAIIntegration(mode="demo")
iot_ai = IoTOptimizationAI(brain_ai)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    return HTMLResponse(content=iot_ai.web_components.render_iot_dashboard())

@app.get("/api/devices")
async def get_devices():
    """Get all IoT devices"""
    return {"devices": list(iot_ai.devices.values())}

@app.get("/api/device/{device_id}/performance")
async def analyze_device_performance_endpoint(device_id: str):
    """Analyze device performance"""
    try:
        insight = await iot_ai.analyze_device_performance(device_id)
        return insight.dict()
    except Exception as e:
        logger.error(f"Error analyzing device performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/energy-optimization")
async def optimize_energy_consumption_endpoint():
    """Get energy optimization recommendations"""
    try:
        optimization = iot_ai.optimize_energy_consumption()
        return optimization
    except Exception as e:
        logger.error(f"Error optimizing energy consumption: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/iot-dashboard")
async def get_iot_dashboard():
    """Get IoT dashboard data"""
    try:
        dashboard_data = iot_ai.get_iot_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting IoT dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/device-readings")
async def get_device_readings():
    """Get device readings"""
    return {"readings": iot_ai.device_readings}

@app.get("/api/energy-consumption")
async def get_energy_consumption():
    """Get energy consumption data"""
    return {"energy_data": iot_ai.energy_consumption}

@app.get("/api/network-traffic")
async def get_network_traffic():
    """Get network traffic data"""
    return {"traffic_data": iot_ai.network_traffic}

@app.get("/api/optimization-rules")
async def get_optimization_rules():
    """Get optimization rules"""
    return {"rules": list(iot_ai.optimization_rules.values())}

@app.get("/api/performance-insights")
async def get_performance_insights():
    """Get performance insights"""
    return {"insights": list(iot_ai.performance_insights.values())}

@app.post("/api/demo/analyze-device")
async def analyze_demo_device():
    """Analyze a random demo device for testing"""
    device_ids = list(iot_ai.devices.keys())
    if not device_ids:
        raise HTTPException(status_code=404, detail="No devices available for analysis")
    
    device_id = random.choice(device_ids)
    insight = await iot_ai.analyze_device_performance(device_id)
    return {"device_id": device_id, "insight": insight.dict()}

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting IoT Optimization...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")