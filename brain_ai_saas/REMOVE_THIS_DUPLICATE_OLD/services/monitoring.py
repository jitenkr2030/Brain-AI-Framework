"""
Monitoring and Metrics Service
Monitoring, logging, and metrics collection for the Brain-Inspired AI Framework.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import time
from loguru import logger

from app.config import get_settings


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"        # Monotonically increasing
    GAUGE = "gauge"           # Can go up and down
    HISTOGRAM = "histogram"   # Distribution of values
    TIMER = "timer"           # Timing measurements


@dataclass
class Metric:
    """Represents a metric"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = None
    unit: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels or {},
            "unit": self.unit
        }


class MetricsCollector:
    """
    Metrics Collection Service
    
    Collects and manages metrics for the brain-inspired AI system:
    - System metrics (CPU, memory, disk)
    - Application metrics (requests, errors, performance)
    - Brain-specific metrics (memory operations, learning, reasoning)
    - Custom business metrics
    """
    
    def __init__(self):
        self.settings = get_settings()
        
        # Metrics storage
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.timers: Dict[str, List[float]] = {}
        
        # Metric collection settings
        self.collection_interval = 30  # seconds
        self.max_metrics_history = 10000
        self.max_timer_history = 1000
        
        # Service status
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            "metrics_collected": 0,
            "collection_cycles": 0,
            "errors": 0,
            "average_collection_time": 0.0
        }
        
        # Initialize default metrics
        self._setup_default_metrics()
    
    def _setup_default_metrics(self):
        """Setup default system and application metrics"""
        
        # System metrics
        self.register_counter("system.cpu.usage", "CPU usage percentage", unit="%")
        self.register_gauge("system.memory.usage", "Memory usage", unit="bytes")
        self.register_gauge("system.memory.available", "Available memory", unit="bytes")
        self.register_gauge("system.disk.usage", "Disk usage", unit="bytes")
        self.register_gauge("system.disk.free", "Free disk space", unit="bytes")
        
        # Application metrics
        self.register_counter("app.requests.total", "Total requests")
        self.register_counter("app.requests.errors", "Total request errors")
        self.register_counter("app.requests.success", "Total successful requests")
        self.register_gauge("app.requests.active", "Active requests")
        self.register_timer("app.request.duration", "Request duration")
        
        # Brain-specific metrics
        self.register_counter("brain.memories.total", "Total memories")
        self.register_counter("brain.memories.accessed", "Memory accesses")
        self.register_counter("brain.learning.updates", "Learning updates applied")
        self.register_counter("brain.reasoning.requests", "Reasoning requests")
        self.register_gauge("brain.activation.active_memories", "Currently active memories")
        self.register_counter("brain.feedback.processed", "Feedback processed")
        
        # Performance metrics
        self.register_timer("brain.processing.time", "Brain processing time")
        self.register_histogram("brain.memory.retrieval.time", "Memory retrieval time")
        self.register_histogram("brain.reasoning.time", "Reasoning execution time")
    
    async def start(self):
        """Start the metrics collection service"""
        if self.running:
            return
        
        try:
            self.running = True
            logger.info("📊 Starting metrics collection service...")
            
            # Start collection task
            self.collection_task = asyncio.create_task(self._collection_loop())
            
            logger.info("✅ Metrics collection service started")
            
        except Exception as e:
            self.running = False
            logger.error(f"❌ Failed to start metrics collection: {e}")
            raise
    
    async def stop(self):
        """Stop the metrics collection service"""
        if not self.running:
            return
        
        try:
            self.running = False
            logger.info("🛑 Stopping metrics collection service...")
            
            # Cancel collection task
            if self.collection_task and not self.collection_task.done():
                self.collection_task.cancel()
                try:
                    await self.collection_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Metrics collection service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping metrics collection: {e}")
    
    async def _collection_loop(self):
        """Main metrics collection loop"""
        while self.running:
            try:
                start_time = time.time()
                
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect application metrics
                await self._collect_application_metrics()
                
                # Calculate collection time
                collection_time = time.time() - start_time
                self._update_collection_stats(collection_time)
                
                # Wait for next collection
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                logger.info("Metrics collection loop cancelled")
                break
            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_gauge("system.cpu.usage", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_gauge("system.memory.usage", memory.used)
            self.record_gauge("system.memory.available", memory.available)
            self.record_gauge("system.memory.percent", memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.record_gauge("system.disk.usage", disk.used)
            self.record_gauge("system.disk.free", disk.free)
            self.record_gauge("system.disk.percent", disk.percent)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # These would be populated by the application
            # For now, we'll use placeholder values
            
            # Request metrics (would be updated by API layer)
            active_requests = len(getattr(self, '_active_requests', []))
            self.record_gauge("app.requests.active", active_requests)
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    def _update_collection_stats(self, collection_time: float):
        """Update collection statistics"""
        
        self.stats["metrics_collected"] += 1
        self.stats["collection_cycles"] += 1
        
        # Update average collection time
        total_cycles = self.stats["collection_cycles"]
        current_avg = self.stats["average_collection_time"]
        self.stats["average_collection_time"] = (
            (current_avg * (total_cycles - 1) + collection_time) / total_cycles
        )
    
    # Metric registration methods
    
    def register_counter(self, name: str, description: str = "", unit: str = ""):
        """Register a counter metric"""
        self.counters[name] = 0.0
        logger.debug(f"Registered counter metric: {name}")
    
    def register_gauge(self, name: str, description: str = "", unit: str = ""):
        """Register a gauge metric"""
        self.gauges[name] = 0.0
        logger.debug(f"Registered gauge metric: {name}")
    
    def register_histogram(self, name: str, description: str = "", unit: str = ""):
        """Register a histogram metric"""
        self.histograms[name] = []
        logger.debug(f"Registered histogram metric: {name}")
    
    def register_timer(self, name: str, description: str = "", unit: str = "seconds"):
        """Register a timer metric"""
        self.timers[name] = []
        logger.debug(f"Registered timer metric: {name}")
    
    # Metric recording methods
    
    def record_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Record a counter value"""
        try:
            if name in self.counters:
                self.counters[name] += value
                
                metric = Metric(
                    name=name,
                    value=self.counters[name],
                    metric_type=MetricType.COUNTER,
                    timestamp=datetime.now(),
                    labels=labels,
                    unit="count"
                )
                self._add_metric(metric)
            else:
                logger.warning(f"Counter metric {name} not registered")
                
        except Exception as e:
            logger.error(f"Error recording counter {name}: {e}")
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a gauge value"""
        try:
            if name in self.gauges:
                self.gauges[name] = value
                
                metric = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType.GAUGE,
                    timestamp=datetime.now(),
                    labels=labels
                )
                self._add_metric(metric)
            else:
                logger.warning(f"Gauge metric {name} not registered")
                
        except Exception as e:
            logger.error(f"Error recording gauge {name}: {e}")
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        try:
            if name in self.histograms:
                self.histograms[name].append(value)
                
                # Keep histogram size manageable
                if len(self.histograms[name]) > self.max_timer_history:
                    self.histograms[name] = self.histograms[name][-self.max_timer_history:]
                
                metric = Metric(
                    name=name,
                    value=value,
                    metric_type=MetricType.HISTOGRAM,
                    timestamp=datetime.now(),
                    labels=labels
                )
                self._add_metric(metric)
            else:
                logger.warning(f"Histogram metric {name} not registered")
                
        except Exception as e:
            logger.error(f"Error recording histogram {name}: {e}")
    
    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """Record a timer value"""
        try:
            if name in self.timers:
                self.timers[name].append(duration)
                
                # Keep timer size manageable
                if len(self.timers[name]) > self.max_timer_history:
                    self.timers[name] = self.timers[name][-self.max_timer_history:]
                
                metric = Metric(
                    name=name,
                    value=duration,
                    metric_type=MetricType.TIMER,
                    timestamp=datetime.now(),
                    labels=labels,
                    unit="seconds"
                )
                self._add_metric(metric)
            else:
                logger.warning(f"Timer metric {name} not registered")
                
        except Exception as e:
            logger.error(f"Error recording timer {name}: {e}")
    
    def _add_metric(self, metric: Metric):
        """Add a metric to the collection"""
        
        self.metrics.append(metric)
        
        # Keep metrics history manageable
        if len(self.metrics) > self.max_metrics_history:
            self.metrics = self.metrics[-self.max_metrics_history:]
    
    # Brain-specific metric methods
    
    def record_memory_retrieval(self, memory_count: int):
        """Record memory retrieval operation"""
        self.record_counter("brain.memories.retrieved", memory_count)
    
    def record_memory_storage(self):
        """Record memory storage operation"""
        self.record_counter("brain.memories.stored")
    
    def record_learning_update(self):
        """Record learning update"""
        self.record_counter("brain.learning.updates")
    
    def record_reasoning_request(self, duration: float = None):
        """Record reasoning request"""
        self.record_counter("brain.reasoning.requests")
        if duration is not None:
            self.record_timer("brain.reasoning.time", duration)
    
    def record_active_memories(self, count: int):
        """Record active memory count"""
        self.record_gauge("brain.activation.active_memories", count)
    
    def record_feedback_processed(self):
        """Record feedback processing"""
        self.record_counter("brain.feedback.processed")
    
    def record_error(self):
        """Record error occurrence"""
        self.record_counter("app.requests.errors")
    
    def record_success(self):
        """Record successful operation"""
        self.record_counter("app.requests.success")
    
    def record_processing_time(self, duration: float):
        """Record overall processing time"""
        self.record_timer("brain.processing.time", duration)
    
    # Utility methods
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get summary of metrics for the last N hours"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        
        # Group by metric name
        metrics_by_name = {}
        for metric in recent_metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)
        
        # Calculate summaries
        summary = {}
        for name, metrics in metrics_by_name.items():
            values = [m.value for m in metrics]
            
            summary[name] = {
                "count": len(values),
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "avg": sum(values) / len(values) if values else 0,
                "latest": values[-1] if values else 0,
                "metric_type": metrics[0].metric_type.value if metrics else "unknown"
            }
        
        return summary
    
    def get_current_values(self) -> Dict[str, float]:
        """Get current values of all metrics"""
        
        current_values = {}
        
        # Add counter values
        current_values.update(self.counters)
        
        # Add gauge values
        current_values.update(self.gauges)
        
        # Add latest histogram values
        for name, values in self.histograms.items():
            if values:
                current_values[name] = values[-1]
        
        # Add latest timer values
        for name, values in self.timers.items():
            if values:
                current_values[name] = values[-1]
        
        return current_values
    
    def get_histogram_stats(self, metric_name: str) -> Dict[str, Any]:
        """Get statistics for a histogram metric"""
        
        if metric_name not in self.histograms:
            return {}
        
        values = self.histograms[metric_name]
        if not values:
            return {"count": 0}
        
        sorted_values = sorted(values)
        count = len(values)
        
        return {
            "count": count,
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / count,
            "median": sorted_values[count // 2],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)]
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        
        if format.lower() == "json":
            metrics_data = [metric.to_dict() for metric in self.metrics]
            return f"{{\n  \"metrics\": {metrics_data}\n}}"
        elif format.lower() == "prometheus":
            # Export in Prometheus format
            lines = []
            for metric in self.metrics:
                labels = ""
                if metric.labels:
                    label_strs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    labels = "{" + ",".join(label_strs) + "}"
                
                lines.append(f"{metric.name}{labels} {metric.value} {int(metric.timestamp.timestamp())}")
            
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get metrics service statistics"""
        
        return {
            **self.stats,
            "running": self.running,
            "metrics_count": len(self.metrics),
            "counters_count": len(self.counters),
            "gauges_count": len(self.gauges),
            "histograms_count": len(self.histograms),
            "timers_count": len(self.timers),
            "collection_interval_seconds": self.collection_interval
        }


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def setup_monitoring(app):
    """Setup monitoring for FastAPI app"""
    
    @app.on_event("startup")
    async def startup_event():
        """Start metrics collection on app startup"""
        metrics = get_metrics_collector()
        await metrics.start()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Stop metrics collection on app shutdown"""
        metrics = get_metrics_collector()
        await metrics.stop()
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def metrics_endpoint():
        """Prometheus metrics endpoint"""
        metrics = get_metrics_collector()
        return metrics.export_metrics("prometheus")
    
    logger.info("📊 Monitoring setup complete")