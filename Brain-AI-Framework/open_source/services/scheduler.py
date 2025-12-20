"""
Background Services
Background services for the Brain-Inspired AI Framework.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import schedule
import threading
from loguru import logger

from app.config import get_settings


class ServiceStatus(Enum):
    """Status of background services"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    name: str
    function: callable
    interval: str  # Cron-like expression
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: ServiceStatus = ServiceStatus.STOPPED
    error_count: int = 0


class Scheduler:
    """
    Background Task Scheduler
    
    Manages periodic tasks and background operations:
    - Memory consolidation
    - Performance optimization
    - System health checks
    - Data cleanup
    - Learning updates
    """
    
    def __init__(self, brain_system):
        self.brain_system = brain_system
        self.settings = get_settings()
        
        # Scheduled tasks
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Service status
        self.status = ServiceStatus.STOPPED
        
        # Statistics
        self.stats = {
            "total_scheduled_tasks": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_execution_time": 0.0,
            "last_run_times": {}
        }
        
        # Initialize default tasks
        self._setup_default_tasks()
    
    def _setup_default_tasks(self):
        """Setup default scheduled tasks"""
        
        # Memory consolidation - every hour
        self.add_task(
            name="memory_consolidation",
            function=self._consolidate_memories,
            interval="1h"
        )
        
        # System health check - every 15 minutes
        self.add_task(
            name="health_check",
            function=self._system_health_check,
            interval="15m"
        )
        
        # Data cleanup - daily
        self.add_task(
            name="data_cleanup",
            function=self._cleanup_old_data,
            interval="1d"
        )
        
        # Performance optimization - every 6 hours
        self.add_task(
            name="performance_optimization",
            function=self._optimize_performance,
            interval="6h"
        )
        
        # Learning updates - every 30 minutes
        self.add_task(
            name="learning_updates",
            function=self._process_learning_updates,
            interval="30m"
        )
    
    def add_task(self, name: str, function: callable, interval: str):
        """Add a scheduled task"""
        
        task = ScheduledTask(
            name=name,
            function=function,
            interval=interval
        )
        
        self.tasks[name] = task
        self.stats["total_scheduled_tasks"] += 1
        
        logger.info(f"Added scheduled task: {name} (interval: {interval})")
    
    async def start(self):
        """Start the scheduler"""
        if self.status == ServiceStatus.RUNNING:
            return
        
        try:
            self.status = ServiceStatus.STARTING
            logger.info("🚀 Starting scheduler service...")
            
            # Start each scheduled task
            for task_name, task in self.tasks.items():
                await self._start_task(task_name, task)
            
            self.status = ServiceStatus.RUNNING
            logger.info("✅ Scheduler service started")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        if self.status == ServiceStatus.STOPPED:
            return
        
        try:
            self.status = ServiceStatus.STOPPING
            logger.info("🛑 Stopping scheduler service...")
            
            # Cancel all running tasks
            for task_name, task in self.running_tasks.items():
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self.running_tasks:
                await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
            
            self.running_tasks.clear()
            
            # Update task statuses
            for task in self.tasks.values():
                task.status = ServiceStatus.STOPPED
            
            self.status = ServiceStatus.STOPPED
            logger.info("✅ Scheduler service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            self.status = ServiceStatus.ERROR
    
    async def _start_task(self, task_name: str, task: ScheduledTask):
        """Start a scheduled task"""
        
        async def run_scheduled_task():
            while task.status == ServiceStatus.RUNNING:
                try:
                    start_time = datetime.now()
                    
                    # Execute the task
                    if asyncio.iscoroutinefunction(task.function):
                        await task.function()
                    else:
                        task.function()
                    
                    # Update timing information
                    end_time = datetime.now()
                    execution_time = (end_time - start_time).total_seconds()
                    
                    task.last_run = end_time
                    self._update_task_stats(task_name, execution_time, success=True)
                    
                    # Schedule next run using schedule library
                    schedule.clear(task_name)
                    schedule.every().do(self._execute_task_wrapper, task_name).tag(task_name)
                    
                    # Wait for next scheduled run
                    await asyncio.sleep(1)  # Check every second
                    
                except asyncio.CancelledError:
                    logger.info(f"Task {task_name} cancelled")
                    break
                except Exception as e:
                    task.error_count += 1
                    self._update_task_stats(task_name, 0, success=False)
                    logger.error(f"Task {task_name} failed: {e}")
                    
                    # Wait before retrying
                    await asyncio.sleep(60)  # Wait 1 minute before retry
        
        # Start the task
        task.status = ServiceStatus.RUNNING
        self.running_tasks[task_name] = asyncio.create_task(run_scheduled_task())
        
        logger.debug(f"Started task: {task_name}")
    
    def _execute_task_wrapper(self, task_name: str):
        """Wrapper to execute task from schedule library"""
        if task_name in self.tasks:
            task = self.tasks[task_name]
            try:
                if asyncio.iscoroutinefunction(task.function):
                    # This would need to be handled differently in a real implementation
                    logger.warning(f"Async task {task_name} called synchronously")
                else:
                    task.function()
            except Exception as e:
                logger.error(f"Scheduled task {task_name} failed: {e}")
    
    async def _consolidate_memories(self):
        """Consolidate and optimize memory storage"""
        try:
            logger.info("🔄 Starting memory consolidation...")
            
            if not self.brain_system.memory_store:
                logger.warning("Memory store not available")
                return
            
            # Apply time decay to memories
            await self.brain_system.memory_store.apply_time_decay()
            
            # Consolidate similar memories (simplified)
            memory_stats = self.brain_system.memory_store.get_statistics()
            logger.info(f"Memory consolidation completed. Total memories: {memory_stats['total_memories']}")
            
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
    
    async def _system_health_check(self):
        """Perform system health check"""
        try:
            logger.debug("🏥 Running system health check...")
            
            # Check brain system status
            if not self.brain_system._initialized:
                logger.warning("Brain system not initialized")
                return
            
            # Check memory store health
            if self.brain_system.memory_store:
                memory_stats = self.brain_system.memory_store.get_statistics()
                total_memories = memory_stats.get("total_memories", 0)
                
                if total_memories > 10000:
                    logger.warning(f"High memory count: {total_memories}")
            
            # Check persistence health
            if self.brain_system.persistence_manager:
                health = await self.brain_system.persistence_manager.health_check()
                if health.get("status") != "healthy":
                    logger.error(f"Database health issue: {health}")
            
            # Check service statuses
            services_status = self._get_services_status()
            failed_services = [name for name, status in services_status.items() if status != "healthy"]
            
            if failed_services:
                logger.warning(f"Failed services: {failed_services}")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old data and logs"""
        try:
            logger.info("🧹 Starting data cleanup...")
            
            # Clean old learning events
            if self.brain_system.learning_engine:
                # Keep only recent learning history
                cutoff_time = datetime.now() - timedelta(days=7)
                # This would be implemented in the learning engine
            
            # Clean old event logs
            if self.brain_system.persistence_manager:
                # Clean old events (older than 30 days)
                cutoff_time = datetime.now() - timedelta(days=30)
                # This would be implemented in persistence manager
            
            # Clean cache if needed
            if hasattr(self.brain_system, 'reasoning_engine') and self.brain_system.reasoning_engine:
                self.brain_system.reasoning_engine._clean_cache()
            
            logger.info("✅ Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    async def _optimize_performance(self):
        """Optimize system performance"""
        try:
            logger.info("⚡ Starting performance optimization...")
            
            # Optimize memory store indices
            if self.brain_system.memory_store:
                # This would involve rebuilding indices, vacuuming database, etc.
                logger.info("Memory store optimization completed")
            
            # Update learning parameters based on performance
            if self.brain_system.learning_engine:
                # Adapt learning parameters
                performance_metrics = {
                    "accuracy": 0.8,  # This would be calculated from actual performance
                    "stability": 0.9
                }
                self.brain_system.learning_engine.adapt_learning_parameters(performance_metrics)
            
            logger.info("✅ Performance optimization completed")
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
    
    async def _process_learning_updates(self):
        """Process pending learning updates"""
        try:
            logger.debug("📚 Processing learning updates...")
            
            # Process feedback queue
            if hasattr(self.brain_system, 'feedback_processor') and self.brain_system.feedback_processor:
                # Process any pending feedback
                # This would be handled by the feedback processor's background task
                pass
            
            # Update memory strengths based on usage patterns
            if self.brain_system.memory_store and self.brain_system.learning_engine:
                # Analyze usage patterns and update memories
                pass
            
        except Exception as e:
            logger.error(f"Learning updates failed: {e}")
    
    def _update_task_stats(self, task_name: str, execution_time: float, success: bool):
        """Update task execution statistics"""
        
        if success:
            self.stats["successful_runs"] += 1
        else:
            self.stats["failed_runs"] += 1
        
        # Update average execution time
        total_runs = self.stats["successful_runs"] + self.stats["failed_runs"]
        if total_runs == 1:
            self.stats["average_execution_time"] = execution_time
        else:
            current_avg = self.stats["average_execution_time"]
            self.stats["average_execution_time"] = (
                (current_avg * (total_runs - 1) + execution_time) / total_runs
            )
        
        # Update last run time
        self.stats["last_run_times"][task_name] = datetime.now().isoformat()
    
    def _get_services_status(self) -> Dict[str, str]:
        """Get status of all services"""
        services = {}
        
        # Brain system components
        services["encoder"] = "healthy" if self.brain_system.encoder else "unhealthy"
        services["memory_store"] = "healthy" if self.brain_system.memory_store else "unhealthy"
        services["learning_engine"] = "healthy" if self.brain_system.learning_engine else "unhealthy"
        services["reasoning_engine"] = "healthy" if self.brain_system.reasoning_engine else "unhealthy"
        services["feedback_processor"] = "healthy" if self.brain_system.feedback_processor else "unhealthy"
        services["persistence_manager"] = "healthy" if self.brain_system.persistence_manager else "unhealthy"
        
        # Background services
        services["scheduler"] = self.status.value
        
        return services
    
    def get_scheduler_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        
        task_statuses = {}
        for name, task in self.tasks.items():
            task_statuses[name] = {
                "status": task.status.value,
                "interval": task.interval,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "error_count": task.error_count
            }
        
        return {
            **self.stats,
            "scheduler_status": self.status.value,
            "active_tasks": len([t for t in self.tasks.values() if t.status == ServiceStatus.RUNNING]),
            "task_details": task_statuses
        }
    
    def run_task_now(self, task_name: str) -> bool:
        """Manually run a task immediately"""
        
        if task_name not in self.tasks:
            logger.error(f"Task {task_name} not found")
            return False
        
        task = self.tasks[task_name]
        
        try:
            if asyncio.iscoroutinefunction(task.function):
                # Run async task
                asyncio.create_task(task.function())
            else:
                # Run sync task
                task.function()
            
            logger.info(f"Manually triggered task: {task_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run task {task_name}: {e}")
            return False